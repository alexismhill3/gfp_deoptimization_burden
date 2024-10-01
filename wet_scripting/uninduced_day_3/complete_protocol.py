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
final_positions = {'B4': ['C2', 'GFP50', 'R0.25', 21.09436023202934, 169.40563976797065], 'G5': ['D2', 'GFP50', 'R0.5', 20.91562474356396, 169.58437525643603], 'E4': ['E2', 'GFP50', 'R1', 21.699452883129634, 168.80054711687038], 'E6': ['F2', 'GFP50', 'R2', 19.17935827364275, 171.32064172635725], 'D2': ['G2', 'GFP50', 'R4', 17.973940700103235, 172.52605929989676], 'G4': ['C3', 'GAG', 'R0.25', 18.38253605679702, 172.11746394320298], 'C6': ['D3', 'GAG', 'R0.5', 21.57964457684586, 168.92035542315415], 'E5': ['E3', 'GAG', 'R1', 28.212947419013833, 162.28705258098617], 'E3': ['F3', 'GAG', 'R2', 18.425865829066158, 172.07413417093383], 'F6': ['G3', 'GAG', 'R4', 19.393482123407814, 171.1065178765922], 'E2': ['C4', 'GGA', 'R0.25', 21.80031660318569, 168.69968339681432], 'C3': ['D4', 'GGA', 'R0.5', 21.649371704712944, 168.85062829528707], 'F3': ['E4', 'GGA', 'R1', 25.210278184694918, 165.28972181530509], 'C4': ['F4', 'GGA', 'R2', 22.829634569334157, 167.67036543066584], 'F2': ['G4', 'GGA', 'R4', 18.346580427064936, 172.15341957293506], 'D4': ['C5', 'GGG', 'R0.25', 22.287208844353696, 168.2127911556463], 'B6': ['D5', 'GGG', 'R0.5', 22.686078958839367, 167.81392104116063], 'G2': ['E5', 'GGG', 'R1', 23.031428709547267, 167.46857129045273], 'B3': ['F5', 'GGG', 'R2', 17.465256270748995, 173.034743729251], 'C5': ['G5', 'GGG', 'R4', 18.23955889267839, 172.2604411073216], 'C2': ['C6', 'CTA', 'R0.25', 20.89698914989257, 169.60301085010744], 'D6': ['D6', 'CTA', 'R0.5', 23.658798394235912, 166.8412016057641], 'B2': ['E6', 'CTA', 'R1', 24.3845278750076, 166.1154721249924], 'G6': ['F6', 'CTA', 'R2', 22.297803246157013, 168.202196753843], 'F5': ['G6', 'CTA', 'R4', 21.649371704712944, 168.85062829528707], 'D10': ['C7', 'GFP50', 'R0.25', 20.44159574500168, 170.05840425499832], 'D9': ['D7', 'GFP50', 'R0.5', 20.887681028253617, 169.6123189717464], 'F7': ['E7', 'GFP50', 'R1', 22.098191728749395, 168.40180827125062], 'F8': ['F7', 'GFP50', 'R2', 19.35346967852408, 171.14653032147592], 'E10': ['G7', 'GFP50', 'R4', 17.419848359526107, 173.0801516404739], 'E7': ['C8', 'GAG', 'R0.25', 18.608632925941983, 171.89136707405802], 'F9': ['D8', 'GAG', 'R0.5', 22.05662181509914, 168.44337818490087], 'B9': ['E8', 'GAG', 'R1', 29.10586985044504, 161.39413014955497], 'F11': ['F8', 'GAG', 'R2', 19.645303952997907, 170.8546960470021], 'C7': ['G8', 'GAG', 'R4', 19.828020681423308, 170.6719793185767], 'D11': ['C9', 'GGA', 'R0.25', 22.46871645696829, 168.03128354303172], 'D7': ['D9', 'GGA', 'R0.5', 21.95337806987589, 168.5466219301241], 'G8': ['E9', 'GGA', 'R1', 26.195934655633035, 164.30406534436696], 'E8': ['F9', 'GGA', 'R2', 28.626219733983422, 161.87378026601658], 'E9': ['G9', 'GGA', 'R4', 20.30882532997183, 170.19117467002818], 'B7': ['C10', 'GGG', 'R0.25', 22.46871645696829, 168.03128354303172], 'C11': ['D10', 'GGG', 'R0.5', 21.729615363014965, 168.77038463698503], 'C10': ['E10', 'GGG', 'R1', 20.887681028253617, 169.6123189717464], 'B8': ['F10', 'GGG', 'R2', 18.48396050323487, 172.01603949676513], 'G9': ['G10', 'GGG', 'R4', 19.250206368690215, 171.24979363130979], 'F10': ['C11', 'CTA', 'R0.25', 20.513121083680975, 169.98687891631903], 'G7': ['D11', 'CTA', 'R0.5', 24.071649290168633, 166.42835070983136], 'C8': ['E11', 'CTA', 'R1', 23.551873982809823, 166.9481260171902], 'D8': ['F11', 'CTA', 'R2', 21.840925128567314, 168.6590748714327], 'E11': ['G11', 'CTA', 'R4', 21.500505648243674, 168.9994943517563], 'D3': ['blank', 'blank', 'blank', 0, 190.5], 'G3': ['blank', 'blank', 'blank', 0, 190.5], 'F4': ['blank', 'blank', 'blank', 0, 190.5], 'B5': ['blank', 'blank', 'blank', 0, 190.5], 'D5': ['blank', 'blank', 'blank', 0, 190.5], 'C9': ['blank', 'blank', 'blank', 0, 190.5], 'B10': ['blank', 'blank', 'blank', 0, 190.5], 'G10': ['blank', 'blank', 'blank', 0, 190.5], 'B11': ['blank', 'blank', 'blank', 0, 190.5], 'G11': ['blank', 'blank', 'blank', 0, 190.5]}
iptg_volume = 9.5
metadata = {'protocolName': 'Burden_092824', 'author': 'Cameron <croots@utexas.edu>', 'description': 'Burden experiment on codon-specific strains', 'apiLevel': '2.18'}
induced_wells = ['B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6']
uninduced_wells = ['B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11']
