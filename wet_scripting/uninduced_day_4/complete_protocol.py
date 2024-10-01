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
final_positions = {'C4': ['C2', 'GFP10', 'R0.25', 20.794146437318396, 169.7058535626816], 'F3': ['D2', 'GFP10', 'R0.5', 20.81260172690734, 169.68739827309267], 'F6': ['E2', 'GFP10', 'R1', 23.971990967137664, 166.52800903286234], 'F2': ['F2', 'GFP10', 'R2', 23.72942037040878, 166.77057962959123], 'E3': ['G2', 'GFP10', 'R4', 29.50688835797418, 160.9931116420258], 'G5': ['C3', 'GFP25', 'R0.25', 21.628406745248864, 168.87159325475113], 'B2': ['D3', 'GFP25', 'R0.5', 21.688417216166474, 168.81158278383353], 'B4': ['E3', 'GFP25', 'R1', 21.708494777586196, 168.7915052224138], 'D2': ['F3', 'GFP25', 'R2', 29.731347478178204, 160.7686525218218], 'C5': ['G3', 'GFP25', 'R4', 18.756728981997732, 171.74327101800228], 'C3': ['C4', 'GFP50', 'R0.25', 22.575787147970335, 167.92421285202965], 'F4': ['D4', 'GFP50', 'R0.5', 25.141355058472953, 165.35864494152705], 'B3': ['E4', 'GFP50', 'R1', 22.67401395504883, 167.82598604495118], 'D6': ['F4', 'GFP50', 'R2', 21.548907470150187, 168.9510925298498], 'D5': ['G4', 'GFP50', 'R4', 19.51370955206452, 170.9862904479355], 'F5': ['C5', 'GFP75', 'R0.25', 33.80266568649569, 156.6973343135043], 'D3': ['D5', 'GFP75', 'R0.5', 22.29674414249521, 168.2032558575048], 'G4': ['E5', 'GFP75', 'R1', 19.8355674518022, 170.6644325481978], 'B5': ['F5', 'GFP75', 'R2', 20.255323227489423, 170.2446767725106], 'E4': ['G5', 'GFP75', 'R4', 17.36759818383736, 173.13240181616266], 'E5': ['C6', 'GFP90', 'R0.25', 25.400055360958113, 165.0999446390419], 'G6': ['D6', 'GFP90', 'R0.5', 20.794146437318396, 169.7058535626816], 'E6': ['E6', 'GFP90', 'R1', 20.10769480656539, 170.3923051934346], 'G2': ['F6', 'GFP90', 'R2', 19.652712250113524, 170.84728774988648], 'C2': ['G6', 'GFP90', 'R4', 17.25260209218054, 173.24739790781945], 'F8': ['C7', 'GFP10', 'R0.25', 21.50937953128232, 168.99062046871768], 'F9': ['D7', 'GFP10', 'R0.5', 19.777018699378864, 170.72298130062114], 'G9': ['E7', 'GFP10', 'R1', 22.586660990543734, 167.91333900945625], 'C8': ['F7', 'GFP10', 'R2', 22.67401395504883, 167.82598604495118], 'E8': ['G7', 'GFP10', 'R4', 28.025812266375866, 162.47418773362415], 'E9': ['C8', 'GFP25', 'R0.25', 20.14223727591188, 170.3577627240881], 'G10': ['D8', 'GFP25', 'R0.5', 19.660952021166384, 170.8390479788336], 'B11': ['E8', 'GFP25', 'R1', 21.198283927854593, 169.3017160721454], 'F11': ['F8', 'GFP25', 'R2', 29.285795710959988, 161.21420428904003], 'G11': ['G8', 'GFP25', 'R4', 18.65971732225879, 171.84028267774121], 'C11': ['C9', 'GFP50', 'R0.25', 20.8681646744055, 169.6318353255945], 'D11': ['D9', 'GFP50', 'R0.5', 21.658368921561603, 168.8416310784384], 'B9': ['E9', 'GFP50', 'R1', 20.557177526037755, 169.94282247396225], 'D8': ['F9', 'GFP50', 'R2', 21.539012608526317, 168.96098739147368], 'C9': ['G9', 'GFP50', 'R4', 19.304876787607125, 171.19512321239287], 'G7': ['C10', 'GFP75', 'R0.25', 32.179210247336684, 158.3207897526633], 'D10': ['D10', 'GFP75', 'R0.5', 21.35269867209543, 169.1473013279046], 'D7': ['E10', 'GFP75', 'R1', 18.779258849173967, 171.72074115082603], 'B8': ['F10', 'GFP75', 'R2', 18.454141942878113, 172.04585805712188], 'D9': ['G10', 'GFP75', 'R4', 17.341910786781444, 173.15808921321855], 'F10': ['C11', 'GFP90', 'R0.25', 20.980182561159463, 169.51981743884053], 'F7': ['D11', 'GFP90', 'R0.5', 19.32078220724424, 171.17921779275576], 'B7': ['E11', 'GFP90', 'R1', 19.01528499529385, 171.48471500470615], 'G8': ['F11', 'GFP90', 'R2', 18.461404963612768, 172.03859503638722], 'C7': ['G11', 'GFP90', 'R4', 16.68784832068627, 173.81215167931373], 'E2': ['blank', 'blank', 'blank', 0, 190.5], 'G3': ['blank', 'blank', 'blank', 0, 190.5], 'D4': ['blank', 'blank', 'blank', 0, 190.5], 'B6': ['blank', 'blank', 'blank', 0, 190.5], 'C6': ['blank', 'blank', 'blank', 0, 190.5], 'E7': ['blank', 'blank', 'blank', 0, 190.5], 'B10': ['blank', 'blank', 'blank', 0, 190.5], 'C10': ['blank', 'blank', 'blank', 0, 190.5], 'E10': ['blank', 'blank', 'blank', 0, 190.5], 'E11': ['blank', 'blank', 'blank', 0, 190.5]}
iptg_volume = 9.5
metadata = {'protocolName': 'Burden_092924', 'author': 'Cameron <croots@utexas.edu>', 'description': 'Burden experiment on codon-specific strains', 'apiLevel': '2.18'}
induced_wells = ['B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6']
uninduced_wells = ['B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11']
