from opentrons import protocol_api, types
from opentrons.protocol_api.labware import OutOfTipsError, Well, Labware, next_available_tip
from opentrons.protocol_api.instrument_context import InstrumentContext
from typing import Any, AnyStr, List, Dict, Optional, Union, Tuple, TYPE_CHECKING
import logging
import logging

from contextlib import suppress

# ---------- Protocol Setup

# requirements
requirements = {"robotType": "OT-2"}

# ---------- Custom Systems

class CustomPipette(InstrumentContext):
    """This is a wrapper to the Opentrons pipette classes that does two things.
    First, it changes the out of tips behavior to wait for you to replace the tips.
    Secondly, it enables multichannels to pick up individual tips.

    :param parent_instance: The parent pipette instance
    :param parent_protocol: The protocol context spawning this pipette"""
    def __init__(self, parent_instance, parent_protocol):
        vars(self).update(vars(parent_instance))
        self.protocol = parent_protocol

        if self.mount == 'left':
            checked_mount = types.Mount.LEFT
        if self.mount == 'right':
            checked_mount = types.Mount.RIGHT

        self.protocol._instruments[checked_mount] = self

    def pick_up_tip(self,
                    number: Optional[int] = 1,
                    **kwargs) -> InstrumentContext:
        """Wrapper of the pick up tip function. Prompts operator to refill tips and enables less-than-max
        tip collection by multichannel pipettes.

        :param number: number of tips to pick up (defaults to 1, errors >1 on single channels)

        See super().pick_up_tip for other paramaters"""

        # Bypass everything if operator tells speifically where to pick up a tip
        if kwargs.get('location'): # if location arg exists and is not none
            super().pick_up_tip(**kwargs)
            return self

        # Sanity checking for multichannels
        if not isinstance(number, int) or not 0 < number <= self.channels:
            raise ValueError(f"Invalid value for number of pipette channels: {number}")
        # @TODO: Check for deck conflicts when multichannels are picking up less than the max number of tips.

        # Check to see if there is enought tips for the pipette. If not, have the tips replaced.
        next_tip = None
        try:
            next_tip =  self.next_tip(number)
        except OutOfTipsError:
            input(f"Please replace the following tip boxes then press enter: {self.tip_racks}")
            super().reset_tipracks()

        if not next_tip:
            next_tip = self.next_tip(number)

        # Set the depression strength
        pipette_type = self.model
        if pipette_type == "p20_multi_gen2":
            pickup_current = 0.075
        else:
            pickup_current = 1
        pickup_current = pickup_current*number # of tips
        if self.mount == 'left':
            mountpoint = types.Mount.LEFT
        else:
            mountpoint = types.Mount.RIGHT

        # The doccumented way to actually change the pick up voltage is outdated
        # self.protocol._hw_manager.hardware._attached_instruments[mountpoint].update_config_item('pickupCurrent', pickup_current)

        # Overwrite the tip location (for multichannel pick ups less than max)
        kwargs['location'] = next_tip

        super().pick_up_tip(**kwargs)

        return self

    def next_tip(self, number_of_tips: int) -> Well:
        ''''''
        # Determine where the tips should be picked up from.
        target_well = None
        for tip_rack in self.tip_racks:
            truth_table = [[well.has_tip for well in column] for column in tip_rack.columns()]
            for i1, column in enumerate(tip_rack.columns()):
                for i2, _ in enumerate(column[::-1]):
                    well_index = 7-i2
                    if well_index+number_of_tips > 8:
                        continue
                    if all(truth_table[i1][well_index:well_index+number_of_tips]):
                        target_well = column[well_index]
                        break
                if target_well:
                    break
            if target_well:
                break
        else:
            raise OutOfTipsError
        return target_well

    def get_available_volume(self)-> float:
        "Returns the available space in the tip OR lower(max volume next tip, max volume pipette)"
        if self.has_tip:
            return self.max_volume - self.current_volume
        else:
            next_tip = self.next_tip(1)
            return min([next_tip.max_volume, self.max_volume])

    def get_current_volume(self)-> float:
        return self.current_volume

    def transfer(self, volume, source, destination, touch_tip=False, blow_out=False, reverse=False):
        aspiration_volume = volume
        despense_volume = volume

        if self.get_current_volume():
            self.dispense(self.get_current_volume(), source)

        if reverse and volume*1.1 <= self.get_available_volume():
            aspiration_volume = volume*1.1
        if aspiration_volume > self.get_available_volume():
            raise ValueError(f"Volume {aspiration_volume} is too large for the current tip. Available volume is {self.get_available_volume()}")

        self.aspirate(aspiration_volume, source)
        self.dispense(despense_volume, destination)
        if blow_out:
            self.blow_out(destination)
        if touch_tip:
            self.touch_tip(destination)

        return self.get_current_volume()



# ---------- Actual Protocol

# protocol run function
def run(protocol: protocol_api.ProtocolContext):
    protocol.home()
    # labware

    plate_1 = protocol.load_labware('nest_96_wellplate_200ul_flat', 4)
    plate_2 = protocol.load_labware('nest_96_wellplate_200ul_flat', 5)

    reagent_reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', 6)
    lb_location = reagent_reservoir['A1'].bottom(5)
    iptg_location = reagent_reservoir['A3'].bottom(5)


    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)
    tiprack_20 = protocol.load_labware('opentrons_96_tiprack_20ul', 9)

    p300 = protocol.load_instrument('p300_single', "left", tip_racks=[tiprack_300])
    p20 = protocol.load_instrument('p20_multi_gen2', "right", tip_racks=[tiprack_20])

    p300 = CustomPipette(p300, protocol)
    p20 = CustomPipette(p20, protocol)

    # Define liquids

    lb = protocol.define_liquid(
    name="LB-Carb",
    description="LB + 1x Carbenicillin",
    display_color="#b58005",
    )
    reagent_reservoir['A1'].load_liquid(liquid=lb, volume=15000)
    iptg = protocol.define_liquid(
        name="LB-Carb-IPTG",
        description="LB + 1x Carbenicillin + IPTG",
        display_color="#83b505",
    )
    reagent_reservoir['A3'].load_liquid(liquid=iptg, volume=15000)

    # Set up dictionaries for cell volumes and LB
    lb_instructions = [(value[4], key)
                        for key, value in final_positions.items()] # Volume, Destination
    cell_instructions = [(value[3], value[0], key)
                         for key, value in final_positions.items()]  # Volume, Source, Destination
    locations = list(final_positions.keys())


    # Add LB
    p300.pick_up_tip(1)
    for lb_volume, destination in lb_instructions:  # Add LB to all relevant wells
        p300.transfer(lb_volume, lb_location, plate_2[destination], touch_tip=True, reverse=True)
    p300.drop_tip()

    # Add Cells
    for cell_volume, source, destination in cell_instructions:  # Add cells to all releveant wells
        if cell_volume > 10:
            pipette = p300
        else:
            pipette = p20
        if source == "blank":
            source = lb_location
        else:
            pipette.pick_up_tip(1)
            source = plate_1[source]

            pipette.transfer(cell_volume,
                            source,
                            plate_2[destination],
                            touch_tip=True,
                            reverse=True)
            pipette.drop_tip()

    # Induction
    induced_locations = [x for x in final_positions if x in induced_wells]
    uninduced_locations = [x for x in final_positions if x not in induced_wells]
    for i, (locations, iptg_source) in enumerate(zip((induced_locations, uninduced_locations), (iptg_location, lb_location))):
        if i == 0:
            protocol.comment("Inducing with iptg")
        else:
            protocol.comment("Inducing without IPTG")


        column_occupancy = {n: [False]*12 for n in range(1, 13)} # Logic for tip quantity and where to induce first
        letters = "ABCDEFGH"
        for location in locations:
            column_occupancy[int(location[1:])][letters.index(location[0])] = True
        for column in column_occupancy.keys():
            try:
                start_row = next(i for i, x in enumerate(column_occupancy[column]) if x)
                num_tips = sum(column_occupancy[column])
            except:
                start_row = 0
                num_tips = 0

            column_occupancy[column] = (start_row, num_tips, iptg_source)

        for column, (row, num_tips, iptg_source) in column_occupancy.items():  # Induce all wells
            if num_tips == 0:
                continue
            p20.pick_up_tip(num_tips)
            start_point = plate_2[str(letters[row]) + str(column)]
            p20.transfer((iptg_volume), iptg_source, start_point, touch_tip=True, reverse=True)
            p20.drop_tip()


    protocol.home()

final_positions = {}
iptg_volume = 0
induced_wells = []
uninduced_wells = []
# ---------- Appended Data
final_positions = {'C2': ['C2', 'MCH10', 'R0.25', 27.860996999415473, 162.63900300058452], 'D5': ['D2', 'MCH10', 'R0.5', 17.445766416606087, 173.0542335833939], 'C5': ['E2', 'MCH10', 'R1', 18.239557888551968, 172.26044211144804], 'G4': ['F2', 'MCH10', 'R2', 16.92328693077799, 173.57671306922202], 'F2': ['G2', 'MCH10', 'R4', 17.76291556254009, 172.7370844374599], 'B2': ['C3', 'MCH25', 'R0.25', 14.301762036746293, 176.19823796325372], 'G6': ['D3', 'MCH25', 'R0.5', 14.925279915715873, 175.57472008428414], 'E6': ['E3', 'MCH25', 'R1', 16.288532923322464, 174.21146707667754], 'C3': ['F3', 'MCH25', 'R2', 17.95329967994791, 172.54670032005208], 'G5': ['G3', 'MCH25', 'R4', 14.939541995057052, 175.56045800494294], 'E2': ['C4', 'MCH50', 'R0.25', 13.944579715030098, 176.5554202849699], 'B5': ['D4', 'MCH50', 'R0.5', 14.44269320900728, 176.05730679099273], 'F5': ['E4', 'MCH50', 'R1', 15.395615044749775, 175.10438495525023], 'B4': ['F4', 'MCH50', 'R2', 16.165023948462036, 174.33497605153798], 'C6': ['G4', 'MCH50', 'R4', 14.491780420711079, 176.00821957928892], 'B6': ['C5', 'MCH75', 'R0.25', 13.526330912272686, 176.9736690877273], 'D4': ['D5', 'MCH75', 'R0.5', 13.53023252308804, 176.96976747691195], 'D3': ['E5', 'MCH75', 'R1', 15.52300301716614, 174.97699698283387], 'D2': ['F5', 'MCH75', 'R2', 14.411626741517267, 176.08837325848273], 'F6': ['G5', 'MCH75', 'R4', 12.569330502485968, 177.93066949751403], 'F4': ['C6', 'MCH90', 'R0.25', 15.107975877959396, 175.3920241220406], 'G3': ['D6', 'MCH90', 'R0.5', 13.095772032384808, 177.40422796761518], 'E5': ['E6', 'MCH90', 'R1', 13.139799579491168, 177.36020042050882], 'C4': ['F6', 'MCH90', 'R2', 13.239950529678563, 177.26004947032143], 'G2': ['G6', 'MCH90', 'R4', 13.004990650235673, 177.49500934976433], 'D11': ['C7', 'MCH10', 'R0.25', 29.47165746064017, 161.02834253935984], 'C8': ['D7', 'MCH10', 'R0.5', 16.076369684775496, 174.4236303152245], 'E7': ['E7', 'MCH10', 'R1', 16.97228041211798, 173.52771958788202], 'G7': ['F7', 'MCH10', 'R2', 17.33614297525623, 173.16385702474378], 'F8': ['G7', 'MCH10', 'R4', 16.564667788922602, 173.9353322110774], 'E11': ['C8', 'MCH25', 'R0.25', 14.788799571787784, 175.7112004282122], 'D7': ['D8', 'MCH25', 'R0.5', 14.659373870265213, 175.8406261297348], 'F11': ['E8', 'MCH25', 'R1', 15.736545608397146, 174.76345439160286], 'B7': ['F8', 'MCH25', 'R2', 18.476678697312593, 172.0233213026874], 'C10': ['G8', 'MCH25', 'R4', 14.953832778089456, 175.54616722191054], 'G11': ['C9', 'MCH50', 'R0.25', 13.796905111353306, 176.7030948886467], 'G10': ['D9', 'MCH50', 'R0.5', 14.189266245592014, 176.31073375440798], 'B10': ['E9', 'MCH50', 'R1', 14.64106879197645, 175.85893120802356], 'C7': ['F9', 'MCH50', 'R2', 16.01051330045207, 174.48948669954794], 'G9': ['G9', 'MCH50', 'R4', 13.92801522573821, 176.57198477426178], 'C9': ['C10', 'MCH75', 'R0.25', 12.802642165458172, 177.69735783454183], 'D9': ['D10', 'MCH75', 'R0.5', 17.878020667302565, 172.62197933269744], 'B9': ['E10', 'MCH75', 'R1', 15.19116340541395, 175.30883659458604], 'E8': ['F10', 'MCH75', 'R2', 14.849670723387028, 175.65032927661298], 'F10': ['G10', 'MCH75', 'R4', 13.3873379084534, 177.1126620915466], 'C11': ['C11', 'MCH90', 'R0.25', 14.518697258782343, 175.98130274121766], 'E10': ['D11', 'MCH90', 'R0.5', 12.311964682382639, 178.18803531761736], 'B11': ['E11', 'MCH90', 'R1', 12.760842499341459, 177.73915750065854], 'D10': ['F11', 'MCH90', 'R2', 12.225314917862475, 178.27468508213752], 'F7': ['G11', 'MCH90', 'R4', 12.539086674022748, 177.96091332597726], 'B3': ['blank', 'blank', 'blank', 0, 190.5], 'E3': ['blank', 'blank', 'blank', 0, 190.5], 'F3': ['blank', 'blank', 'blank', 0, 190.5], 'E4': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'B8': ['blank', 'blank', 'blank', 0, 190.5], 'D8': ['blank', 'blank', 'blank', 0, 190.5], 'G8': ['blank', 'blank', 'blank', 0, 190.5], 'E9': ['blank', 'blank', 'blank', 0, 190.5], 'F9': ['blank', 'blank', 'blank', 0, 190.5]}
iptg_volume = 9.5
metadata = {'protocolName': 'Burden_100324', 'author': 'Cameron <croots@utexas.edu>', 'description': 'Burden experiment on codon-specific strains', 'apiLevel': '2.18'}
induced_wells = ['B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6']
uninduced_wells = ['B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11']
