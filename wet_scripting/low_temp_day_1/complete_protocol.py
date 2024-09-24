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
final_positions = {'E11': ['C2', 'GFP10', 'R0.25', 22.28932739277357, 168.21067260722643], 'G10': ['D2', 'GFP10', 'R0.5', 18.766486328064854, 171.73351367193516], 'E7': ['E2', 'GFP10', 'R1', 27.440441610365212, 163.0595583896348], 'F6': ['F2', 'GFP10', 'R2', 28.014095439235927, 162.48590456076408], 'B7': ['G2', 'GFP10', 'R4', 27.06046609310986, 163.43953390689015], 'C11': ['C3', 'GFP25', 'R0.25', 22.01727515647429, 168.48272484352572], 'B6': ['D3', 'GFP25', 'R0.5', 22.28932739277357, 168.21067260722643], 'C6': ['E3', 'GFP25', 'R1', 20.577921987621377, 169.92207801237862], 'G8': ['F3', 'GFP25', 'R2', 26.951615133748568, 163.54838486625144], 'C9': ['G3', 'GFP25', 'R4', 20.8431253692568, 169.6568746307432], 'E4': ['C4', 'GFP50', 'R0.25', 21.03004285023948, 169.46995714976052], 'F9': ['D4', 'GFP50', 'R0.5', 26.63025385305647, 163.86974614694353], 'D11': ['E4', 'GFP50', 'R1', 27.029275540388987, 163.470724459611], 'B8': ['F4', 'GFP50', 'R2', 25.528630823040093, 164.9713691769599], 'F3': ['G4', 'GFP50', 'R4', 20.04153491573178, 170.45846508426823], 'D3': ['C5', 'GFP75', 'R0.25', 21.863321484242118, 168.6366785157579], 'C7': ['D5', 'GFP75', 'R0.5', 20.301791281708354, 170.19820871829165], 'F8': ['E5', 'GFP75', 'R1', 21.65137072150179, 168.8486292784982], 'D5': ['F5', 'GFP75', 'R2', 19.981765771796713, 170.51823422820328], 'G7': ['G5', 'GFP75', 'R4', 18.00291816845077, 172.49708183154922], 'F4': ['C6', 'GFP90', 'R0.25', 17.492615505192514, 173.0073844948075], 'B11': ['D6', 'GFP90', 'R0.5', 21.365341804599762, 169.13465819540025], 'G4': ['E6', 'GFP90', 'R1', 20.08444617887977, 170.41555382112023], 'E10': ['F6', 'GFP90', 'R2', 22.96601679927361, 167.5339832007264], 'C8': ['G6', 'GFP90', 'R4', 19.947771039395313, 170.55222896060468], 'D8': ['C7', 'MCH10', 'R0.25', 36.32373057498434, 154.17626942501568], 'B4': ['D7', 'MCH10', 'R0.5', 23.793224060362054, 166.70677593963794], 'G5': ['E7', 'MCH10', 'R1', 29.812611617987123, 160.68738838201287], 'E9': ['F7', 'MCH10', 'R2', 24.098860720995006, 166.401139279005], 'F7': ['G7', 'MCH10', 'R4', 25.349258860234336, 165.15074113976567], 'G9': ['C8', 'MCH25', 'R0.25', 21.83278996203352, 168.66721003796647], 'G3': ['D8', 'MCH25', 'R0.5', 21.115253755368006, 169.384746244632], 'D2': ['E8', 'MCH25', 'R1', 20.523891873880125, 169.97610812611987], 'D7': ['F8', 'MCH25', 'R2', 29.254739775227854, 161.24526022477215], 'F10': ['G8', 'MCH25', 'R4', 19.157421469661756, 171.34257853033824], 'F2': ['C9', 'MCH50', 'R0.25', 16.912303307538394, 173.5876966924616], 'C2': ['D9', 'MCH50', 'R0.5', 18.42731385281783, 172.07268614718217], 'B2': ['E9', 'MCH50', 'R1', 22.048325203035745, 168.45167479696426], 'E2': ['F9', 'MCH50', 'R2', 20.532878520445035, 169.96712147955498], 'G6': ['G9', 'MCH50', 'R4', 17.41467486333191, 173.08532513666808], 'B3': ['C10', 'MCH75', 'R0.25', 15.617074876931152, 174.88292512306884], 'B10': ['D10', 'MCH75', 'R0.5', 17.886202393000225, 172.61379760699978], 'C5': ['E10', 'MCH75', 'R1', 25.487013939107644, 165.01298606089236], 'E5': ['F10', 'MCH75', 'R2', 18.333671299969044, 172.16632870003096], 'B5': ['G10', 'MCH75', 'R4', 15.050766851572881, 175.4492331484271], 'G11': ['C11', 'MCH90', 'R0.25', 16.138324716887993, 174.361675283112], 'C4': ['D11', 'MCH90', 'R0.5', 17.466557242966907, 173.0334427570331], 'F11': ['E11', 'MCH90', 'R1', 16.91840499954035, 173.58159500045966], 'G2': ['F11', 'MCH90', 'R2', 14.794397631797418, 175.7056023682026], 'F5': ['G11', 'MCH90', 'R4', 15.336211170638524, 175.16378882936147], 'B9': ['blank', 'blank', 'blank', 0, 190.5], 'C3': ['blank', 'blank', 'blank', 0, 190.5], 'C10': ['blank', 'blank', 'blank', 0, 190.5], 'D4': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'D9': ['blank', 'blank', 'blank', 0, 190.5], 'D10': ['blank', 'blank', 'blank', 0, 190.5], 'E3': ['blank', 'blank', 'blank', 0, 190.5], 'E6': ['blank', 'blank', 'blank', 0, 190.5], 'E8': ['blank', 'blank', 'blank', 0, 190.5]}
iptg_volume = 9.5
metadata = {'protocolName': 'Burden_092324', 'author': 'Cameron <croots@utexas.edu>', 'description': 'Burden experiment on codon-specific strains', 'apiLevel': '2.18'}
