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
        column_occupancy[column] = (start_row, num_tips)

    for column, (row, num_tips) in column_occupancy.items():  # Induce all wells
        if num_tips == 0:
            continue
        p20.pick_up_tip(num_tips)
        start_point = plate_2[str(letters[row]) + str(column)]
        p20.transfer((iptg_volume), iptg_location, start_point, touch_tip=True, reverse=True)
        p20.drop_tip()


    protocol.home()

final_positions = {}
iptg_volume = 0
# ---------- Appended Data
final_positions = {'C4': ['C2', 'GFP50', 'R0.25', 33.74187193601469, 156.7581280639853], 'D8': ['D2', 'GFP50', 'R0.5', 40.0864977074027, 150.4135022925973], 'C11': ['E2', 'GFP50', 'R1', 44.080077840040516, 146.41992215995947], 'D5': ['F2', 'GFP50', 'R2', 35.34378119424359, 155.1562188057564], 'B6': ['G2', 'GFP50', 'R4', 38.44360518628316, 152.05639481371685], 'C3': ['C3', 'GGG', 'R0.25', 21.753802404935364, 168.74619759506464], 'B3': ['D3', 'GGG', 'R0.5', 39.780493780481216, 150.7195062195188], 'F11': ['E3', 'GGG', 'R1', 46.80758812147772, 143.69241187852228], 'D2': ['F3', 'GGG', 'R2', 45.40290384302102, 145.09709615697898], 'B8': ['G3', 'GGG', 'R4', 32.12411104477278, 158.37588895522723], 'C2': ['C4', 'GGA', 'R0.25', 33.91265435011298, 156.58734564988703], 'F8': ['D4', 'GGA', 'R0.5', 42.989186362505606, 147.51081363749438], 'F7': ['E4', 'GGA', 'R1', 45.66815725527987, 144.83184274472012], 'G2': ['F4', 'GGA', 'R2', 41.579078888622064, 148.92092111137794], 'G9': ['G4', 'GGA', 'R4', 36.02242865472833, 154.47757134527166], 'C7': ['C5', 'GAG', 'R0.25', 37.94595419116421, 152.55404580883578], 'F9': ['D5', 'GAG', 'R0.5', 40.53690508498589, 149.9630949150141], 'C10': ['E5', 'GAG', 'R1', 35.211111051237, 155.288888948763], 'B10': ['F5', 'GAG', 'R2', 30.69450177726875, 159.80549822273125], 'E6': ['G5', 'GAG', 'R4', 32.775121399286306, 157.72487860071368], 'D9': ['C6', 'CTA', 'R0.25', 29.949681861973833, 160.55031813802617], 'G5': ['D6', 'CTA', 'R0.5', 38.317975039224784, 152.1820249607752], 'F3': ['E6', 'CTA', 'R1', 40.25854054596106, 150.24145945403893], 'C8': ['F6', 'CTA', 'R2', 37.85407381713513, 152.64592618286486], 'B9': ['G6', 'CTA', 'R4', 21.357560407786128, 169.14243959221386], 'B2': ['blank', 'blank', 'blank', 0, 190.5], 'B4': ['blank', 'blank', 'blank', 0, 190.5], 'B5': ['blank', 'blank', 'blank', 0, 190.5], 'B7': ['blank', 'blank', 'blank', 0, 190.5], 'B11': ['blank', 'blank', 'blank', 0, 190.5], 'C5': ['blank', 'blank', 'blank', 0, 190.5], 'C6': ['blank', 'blank', 'blank', 0, 190.5], 'C9': ['blank', 'blank', 'blank', 0, 190.5], 'D3': ['blank', 'blank', 'blank', 0, 190.5], 'D4': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'D7': ['blank', 'blank', 'blank', 0, 190.5], 'D10': ['blank', 'blank', 'blank', 0, 190.5], 'D11': ['blank', 'blank', 'blank', 0, 190.5], 'E2': ['blank', 'blank', 'blank', 0, 190.5], 'E3': ['blank', 'blank', 'blank', 0, 190.5], 'E4': ['blank', 'blank', 'blank', 0, 190.5], 'E5': ['blank', 'blank', 'blank', 0, 190.5], 'E7': ['blank', 'blank', 'blank', 0, 190.5], 'E8': ['blank', 'blank', 'blank', 0, 190.5], 'E9': ['blank', 'blank', 'blank', 0, 190.5], 'E10': ['blank', 'blank', 'blank', 0, 190.5], 'E11': ['blank', 'blank', 'blank', 0, 190.5], 'F2': ['blank', 'blank', 'blank', 0, 190.5], 'F4': ['blank', 'blank', 'blank', 0, 190.5], 'F5': ['blank', 'blank', 'blank', 0, 190.5], 'F6': ['blank', 'blank', 'blank', 0, 190.5], 'F10': ['blank', 'blank', 'blank', 0, 190.5], 'G3': ['blank', 'blank', 'blank', 0, 190.5], 'G4': ['blank', 'blank', 'blank', 0, 190.5], 'G6': ['blank', 'blank', 'blank', 0, 190.5], 'G7': ['blank', 'blank', 'blank', 0, 190.5], 'G8': ['blank', 'blank', 'blank', 0, 190.5], 'G10': ['blank', 'blank', 'blank', 0, 190.5], 'G11': ['blank', 'blank', 'blank', 0, 190.5]}
iptg_volume = 9.5
metadata = {'protocolName': 'Burden_090424', 'author': 'Cameron <croots@utexas.edu>', 'description': 'Burden experiment on codon-specific strains', 'apiLevel': '2.18'}
