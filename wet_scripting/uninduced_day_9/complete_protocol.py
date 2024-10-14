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
final_positions = {'F6': ['C2', 'MCH10', 'R0.25', 42.60646974842882, 147.89353025157118], 'E5': ['D2', 'MCH10', 'R0.5', 23.038216074932638, 167.46178392506735], 'B5': ['E2', 'MCH10', 'R1', 21.585603118473912, 168.9143968815261], 'C6': ['F2', 'MCH10', 'R2', 19.76618440495498, 170.73381559504503], 'D3': ['G2', 'MCH10', 'R4', 18.394069792833548, 172.10593020716647], 'F2': ['C3', 'MCH25', 'R0.25', 16.107288057883935, 174.39271194211608], 'C5': ['D3', 'MCH25', 'R0.5', 19.358262118753537, 171.14173788124646], 'C3': ['E3', 'MCH25', 'R1', 26.044646347609294, 164.4553536523907], 'G2': ['F3', 'MCH25', 'R2', 21.15716422057784, 169.34283577942216], 'D2': ['G3', 'MCH25', 'R4', 21.695438641357896, 168.8045613586421], 'E3': ['C4', 'MCH50', 'R0.25', 14.14902846462644, 176.35097153537356], 'G3': ['D4', 'MCH50', 'R0.5', 15.634776096507085, 174.8652239034929], 'B3': ['E4', 'MCH50', 'R1', 16.3089232915383, 174.1910767084617], 'F5': ['F4', 'MCH50', 'R2', 18.102979811154135, 172.39702018884586], 'G4': ['G4', 'MCH50', 'R4', 14.885489694571104, 175.6145103054289], 'E6': ['C5', 'MCH75', 'R0.25', 14.708103432091235, 175.79189656790876], 'F3': ['D5', 'MCH75', 'R0.5', 15.92678605491683, 174.57321394508318], 'B6': ['E5', 'MCH75', 'R1', 17.219032164971413, 173.28096783502858], 'B2': ['F5', 'MCH75', 'R2', 15.293204614682802, 175.2067953853172], 'F4': ['G5', 'MCH75', 'R4', 13.803401813950348, 176.69659818604964], 'B4': ['C6', 'MCH90', 'R0.25', 13.844146945821048, 176.65585305417895], 'C2': ['D6', 'MCH90', 'R0.5', 14.885489694571104, 175.6145103054289], 'D4': ['E6', 'MCH90', 'R1', 15.081741646542229, 175.41825835345776], 'G6': ['F6', 'MCH90', 'R2', 14.30001879063297, 176.19998120936702], 'C4': ['G6', 'MCH90', 'R4', 13.997015450772729, 176.50298454922728], 'G9': ['C7', 'MCH10', 'R0.25', 43.11564493504888, 147.38435506495114], 'D9': ['D7', 'MCH10', 'R0.5', 24.341497852061604, 166.1585021479384], 'B9': ['E7', 'MCH10', 'R1', 22.13573667159755, 168.36426332840244], 'E7': ['F7', 'MCH10', 'R2', 19.74953751282787, 170.75046248717211], 'F10': ['G7', 'MCH10', 'R4', 18.315057200947912, 172.1849427990521], 'C11': ['C8', 'MCH25', 'R0.25', 16.263679657017203, 174.2363203429828], 'E9': ['D8', 'MCH25', 'R0.5', 19.239150542449373, 171.26084945755062], 'G7': ['E8', 'MCH25', 'R1', 24.215820523054887, 166.2841794769451], 'D10': ['F8', 'MCH25', 'R2', 20.165619319430625, 170.33438068056938], 'E10': ['G8', 'MCH25', 'R4', 21.516285492890937, 168.98371450710906], 'D11': ['C9', 'MCH50', 'R0.25', 13.5717349266368, 176.9282650733632], 'G11': ['D9', 'MCH50', 'R0.5', 15.393593454002161, 175.10640654599783], 'F11': ['E9', 'MCH50', 'R1', 15.233597946659817, 175.2664020533402], 'C7': ['F9', 'MCH50', 'R2', 17.219032164971413, 173.28096783502858], 'B7': ['G9', 'MCH50', 'R4', 14.625545754446092, 175.87445424555392], 'C10': ['C10', 'MCH75', 'R0.25', 14.378932409865758, 176.12106759013423], 'G8': ['D10', 'MCH75', 'R0.5', 15.562148210877282, 174.9378517891227], 'F9': ['E10', 'MCH75', 'R1', 16.662356636963153, 173.83764336303685], 'G10': ['F10', 'MCH75', 'R2', 14.698884206617391, 175.80111579338262], 'D8': ['G10', 'MCH75', 'R4', 13.393454535655305, 177.1065454643447], 'F8': ['C11', 'MCH90', 'R0.25', 13.38199052962407, 177.11800947037594], 'C8': ['D11', 'MCH90', 'R0.5', 13.963677993467458, 176.53632200653254], 'B8': ['E11', 'MCH90', 'R1', 14.46764082296816, 176.03235917703185], 'B11': ['F11', 'MCH90', 'R2', 13.901594694057664, 176.59840530594232], 'E11': ['G11', 'MCH90', 'R4', 13.926361896068547, 176.57363810393144], 'E2': ['blank', 'blank', 'blank', 0, 190.5], 'E4': ['blank', 'blank', 'blank', 0, 190.5], 'D5': ['blank', 'blank', 'blank', 0, 190.5], 'G5': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'D7': ['blank', 'blank', 'blank', 0, 190.5], 'F7': ['blank', 'blank', 'blank', 0, 190.5], 'E8': ['blank', 'blank', 'blank', 0, 190.5], 'C9': ['blank', 'blank', 'blank', 0, 190.5], 'B10': ['blank', 'blank', 'blank', 0, 190.5]}
iptg_volume = 9.5
metadata = {'protocolName': 'Burden_100424', 'author': 'Cameron <croots@utexas.edu>', 'description': 'Burden experiment on codon-specific strains', 'apiLevel': '2.18'}
induced_wells = ['B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6']
uninduced_wells = ['B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11']
