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
final_positions = {'C6': ['C2', 'GFP10', 'R0.25', 56.43268450918091, 134.06731549081908], 'D7': ['D2', 'GFP10', 'R0.5', 35.79971024158715, 154.70028975841285], 'E5': ['E2', 'GFP10', 'R1', 43.06418248441604, 147.43581751558395], 'F9': ['F2', 'GFP10', 'R2', 46.20352392897618, 144.29647607102382], 'D2': ['G2', 'GFP10', 'R4', 35.636503363362465, 154.86349663663754], 'D5': ['C3', 'GFP25', 'R0.25', 32.910813305993585, 157.5891866940064], 'D4': ['D3', 'GFP25', 'R0.5', 30.935425422848628, 159.56457457715138], 'C4': ['E3', 'GFP25', 'R1', 27.09329385786714, 163.40670614213286], 'G8': ['F3', 'GFP25', 'R2', 38.19005146739254, 152.30994853260745], 'G5': ['G3', 'GFP25', 'R4', 33.71518895270709, 156.78481104729292], 'E10': ['C4', 'GFP50', 'R0.25', 43.99324512725053, 146.50675487274947], 'D8': ['D4', 'GFP50', 'R0.5', 32.3657451944015, 158.13425480559852], 'F6': ['E4', 'GFP50', 'R1', 32.63600186189126, 157.86399813810874], 'B8': ['F4', 'GFP50', 'R2', 47.70745759621089, 142.79254240378913], 'G7': ['G4', 'GFP50', 'R4', 40.428584327713274, 150.07141567228672], 'E2': ['C5', 'GFP75', 'R0.25', 35.024418521861335, 155.47558147813868], 'B2': ['D5', 'GFP75', 'R0.5', 33.331817401341326, 157.1681825986587], 'F2': ['E5', 'GFP75', 'R1', 34.58535448101346, 155.91464551898653], 'G10': ['F5', 'GFP75', 'R2', 35.79971024158715, 154.70028975841285], 'F4': ['G5', 'GFP75', 'R4', 30.85402341689735, 159.64597658310265], 'G3': ['C6', 'GFP90', 'R0.25', 35.636503363362465, 154.86349663663754], 'G11': ['D6', 'GFP90', 'R0.5', 39.84470399903818, 150.6552960009618], 'F3': ['E6', 'GFP90', 'R1', 39.0160568880121, 151.4839431119879], 'E8': ['F6', 'GFP90', 'R2', 36.61010225768831, 153.8898977423117], 'B5': ['G6', 'GFP90', 'R4', 29.66365269039431, 160.83634730960569], 'C10': ['C7', 'MCH10', 'R0.25', 55.0418974674318, 135.4581025325682], 'G6': ['D7', 'MCH10', 'R0.5', 33.35552295729257, 157.14447704270742], 'E3': ['E7', 'MCH10', 'R1', 25.025987800819582, 165.4740121991804], 'B9': ['F7', 'MCH10', 'R2', 26.814476478236713, 163.6855235217633], 'B7': ['G7', 'MCH10', 'R4', 25.543923211172554, 164.95607678882743], 'C3': ['C8', 'MCH25', 'R0.25', 27.474198339428625, 163.02580166057137], 'E6': ['D8', 'MCH25', 'R0.5', 26.937681024461664, 163.56231897553835], 'G9': ['E8', 'MCH25', 'R1', 25.06611152867458, 165.43388847132542], 'D11': ['F8', 'MCH25', 'R2', 23.508195528549187, 166.99180447145082], 'E4': ['G8', 'MCH25', 'R4', 21.67238121532383, 168.82761878467616], 'F7': ['C9', 'MCH50', 'R0.25', 34.8681886120874, 155.6318113879126], 'D3': ['D9', 'MCH50', 'R0.5', 39.14631400474312, 151.35368599525688], 'C9': ['E9', 'MCH50', 'R1', 25.782640295420915, 164.71735970457908], 'G2': ['F9', 'MCH50', 'R2', 27.587320251602332, 162.91267974839766], 'D6': ['G9', 'MCH50', 'R4', 25.25507498223827, 165.24492501776172], 'B6': ['C10', 'MCH75', 'R0.25', 35.854446603443066, 154.64555339655692], 'F11': ['D10', 'MCH75', 'R0.5', 40.014673241189556, 150.48532675881046], 'E9': ['E10', 'MCH75', 'R1', 25.543923211172554, 164.95607678882743], 'C5': ['F10', 'MCH75', 'R2', 19.906286122315215, 170.5937138776848], 'C11': ['G10', 'MCH75', 'R4', 23.567257617291396, 166.9327423827086], 'F8': ['C11', 'MCH90', 'R0.25', 35.314509559898845, 155.18549044010115], 'D9': ['D11', 'MCH90', 'R0.5', 64.7717118450412, 125.7282881549588], 'B10': ['E11', 'MCH90', 'R1', 24.199576406279437, 166.30042359372055], 'B3': ['F11', 'MCH90', 'R2', 28.701548949680156, 161.79845105031984], 'C7': ['G11', 'MCH90', 'R4', 26.999711157473698, 163.5002888425263], 'B4': ['blank', 'blank', 'blank', 0, 190.5], 'B11': ['blank', 'blank', 'blank', 0, 190.5], 'C2': ['blank', 'blank', 'blank', 0, 190.5], 'C8': ['blank', 'blank', 'blank', 0, 190.5], 'D10': ['blank', 'blank', 'blank', 0, 190.5], 'E7': ['blank', 'blank', 'blank', 0, 190.5], 'E11': ['blank', 'blank', 'blank', 0, 190.5], 'F5': ['blank', 'blank', 'blank', 0, 190.5], 'F10': ['blank', 'blank', 'blank', 0, 190.5], 'G4': ['blank', 'blank', 'blank', 0, 190.5]}
iptg_volume = 9.5
metadata = {'protocolName': 'Burden_08_29_2024', 'author': 'Cameron <croots@utexas.edu>', 'description': 'Burden experiment on codon-specific strains', 'apiLevel': '2.18'}
