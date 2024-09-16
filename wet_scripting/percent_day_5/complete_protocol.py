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
final_positions = {'D5': ['C2', 'GFP10', 'R0.25', 58.39292673207237, 132.10707326792763], 'E5': ['D2', 'GFP10', 'R0.5', 39.67281240902912, 150.82718759097088], 'D11': ['E2', 'GFP10', 'R1', 30.690484031725614, 159.80951596827438], 'B9': ['F2', 'GFP10', 'R2', 49.10091812701321, 141.39908187298678], 'E9': ['G2', 'GFP10', 'R4', 44.44768908128513, 146.05231091871488], 'F11': ['C3', 'GFP25', 'R0.25', 36.493308863019976, 154.00669113698], 'B4': ['D3', 'GFP25', 'R0.5', 32.954747873684944, 157.54525212631506], 'E10': ['E3', 'GFP25', 'R1', 39.20849459684402, 151.29150540315598], 'E11': ['F3', 'GFP25', 'R2', 40.07964534874982, 150.4203546512502], 'E3': ['G3', 'GFP25', 'R4', 34.10500245515704, 156.39499754484297], 'F9': ['C4', 'GFP50', 'R0.25', 43.258807950777, 147.241192049223], 'C5': ['D4', 'GFP50', 'R0.5', 51.641928484514224, 138.8580715154858], 'G5': ['E4', 'GFP50', 'R1', 43.49953395849384, 147.00046604150617], 'D9': ['F4', 'GFP50', 'R2', 36.75066657052645, 153.74933342947355], 'B5': ['G4', 'GFP50', 'R4', 33.56799090262197, 156.93200909737803], 'F4': ['C5', 'GFP75', 'R0.25', 32.119710354124386, 158.38028964587562], 'C10': ['D5', 'GFP75', 'R0.5', 36.12786780033783, 154.37213219966216], 'D8': ['E5', 'GFP75', 'R1', 38.00129590402187, 152.49870409597813], 'D10': ['F5', 'GFP75', 'R2', 36.72189168114442, 153.77810831885557], 'B8': ['G5', 'GFP75', 'R4', 32.977919933963, 157.522080066037], 'F10': ['C6', 'GFP90', 'R0.25', 34.279490079677, 156.220509920323], 'G2': ['D6', 'GFP90', 'R0.5', 34.99567171682602, 155.50432828317398], 'C7': ['E6', 'GFP90', 'R1', 32.931611799991536, 157.56838820000846], 'D4': ['F6', 'GFP90', 'R2', 28.94778434472155, 161.55221565527845], 'D2': ['G6', 'GFP90', 'R4', 32.45308582802544, 158.04691417197455], 'B2': ['blank', 'blank', 'blank', 0, 190.5], 'B3': ['blank', 'blank', 'blank', 0, 190.5], 'B6': ['blank', 'blank', 'blank', 0, 190.5], 'B7': ['blank', 'blank', 'blank', 0, 190.5], 'B10': ['blank', 'blank', 'blank', 0, 190.5], 'B11': ['blank', 'blank', 'blank', 0, 190.5], 'C2': ['blank', 'blank', 'blank', 0, 190.5], 'C3': ['blank', 'blank', 'blank', 0, 190.5], 'C4': ['blank', 'blank', 'blank', 0, 190.5], 'C6': ['blank', 'blank', 'blank', 0, 190.5], 'C8': ['blank', 'blank', 'blank', 0, 190.5], 'C9': ['blank', 'blank', 'blank', 0, 190.5], 'C11': ['blank', 'blank', 'blank', 0, 190.5], 'D3': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'D7': ['blank', 'blank', 'blank', 0, 190.5], 'E2': ['blank', 'blank', 'blank', 0, 190.5], 'E4': ['blank', 'blank', 'blank', 0, 190.5], 'E6': ['blank', 'blank', 'blank', 0, 190.5], 'E7': ['blank', 'blank', 'blank', 0, 190.5], 'E8': ['blank', 'blank', 'blank', 0, 190.5], 'F2': ['blank', 'blank', 'blank', 0, 190.5], 'F3': ['blank', 'blank', 'blank', 0, 190.5], 'F5': ['blank', 'blank', 'blank', 0, 190.5], 'F6': ['blank', 'blank', 'blank', 0, 190.5], 'F7': ['blank', 'blank', 'blank', 0, 190.5], 'F8': ['blank', 'blank', 'blank', 0, 190.5], 'G3': ['blank', 'blank', 'blank', 0, 190.5], 'G4': ['blank', 'blank', 'blank', 0, 190.5], 'G6': ['blank', 'blank', 'blank', 0, 190.5], 'G7': ['blank', 'blank', 'blank', 0, 190.5], 'G8': ['blank', 'blank', 'blank', 0, 190.5], 'G9': ['blank', 'blank', 'blank', 0, 190.5], 'G10': ['blank', 'blank', 'blank', 0, 190.5], 'G11': ['blank', 'blank', 'blank', 0, 190.5]}
iptg_volume = 9.5
metadata = {'protocolName': 'Burden_091324', 'author': 'Cameron <croots@utexas.edu>', 'description': 'Burden experiment on codon-specific strains', 'apiLevel': '2.18'}
