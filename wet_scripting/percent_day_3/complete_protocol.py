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
final_positions = {'B10': ['C2', 'GFP10', 'R0.25', 29.265693233885802, 161.2343067661142], 'C7': ['D2', 'GFP10', 'R0.5', 32.28775999357144, 158.21224000642854], 'F2': ['E2', 'GFP10', 'R1', 29.102258550270943, 161.39774144972907], 'F3': ['F2', 'GFP10', 'R2', 38.42471098813522, 152.07528901186478], 'F8': ['G2', 'GFP10', 'R4', 24.344026099267424, 166.1559739007326], 'G11': ['C3', 'GFP25', 'R0.25', 34.881155419596425, 155.61884458040356], 'C8': ['D3', 'GFP25', 'R0.5', 33.800232133563995, 156.699767866436], 'G3': ['E3', 'GFP25', 'R1', 33.319977783515945, 157.18002221648405], 'E4': ['F3', 'GFP25', 'R2', 43.97262257780853, 146.52737742219148], 'E3': ['G3', 'GFP25', 'R4', 32.556713820666666, 157.94328617933334], 'C6': ['C4', 'GFP50', 'R0.25', 39.963529640784934, 150.53647035921506], 'D7': ['D4', 'GFP50', 'R0.5', 43.083963321661564, 147.41603667833843], 'B3': ['E4', 'GFP50', 'R1', 47.73173522747044, 142.76826477252956], 'D2': ['F4', 'GFP50', 'R2', 27.163908071537886, 163.3360919284621], 'D8': ['G4', 'GFP50', 'R4', 30.286194357714564, 160.21380564228542], 'E6': ['C5', 'GFP75', 'R0.25', 26.062012950958508, 164.43798704904148], 'F6': ['D5', 'GFP75', 'R0.5', 19.859925188844983, 170.64007481115502], 'C4': ['E5', 'GFP75', 'R1', 24.281011722987746, 166.21898827701224], 'D3': ['F5', 'GFP75', 'R2', 29.43097394247606, 161.06902605752393], 'F5': ['G5', 'GFP75', 'R4', 21.293563356171234, 169.20643664382877], 'F9': ['C6', 'GFP90', 'R0.25', 32.08894366346964, 158.41105633653035], 'C11': ['D6', 'GFP90', 'R0.5', 28.57041797321417, 161.92958202678582], 'B9': ['E6', 'GFP90', 'R1', 31.849245466190073, 158.65075453380993], 'G5': ['F6', 'GFP90', 'R2', 30.864176064393018, 159.635823935607], 'E7': ['G6', 'GFP90', 'R4', 29.729462010300022, 160.7705379897], 'G9': ['C7', 'MCH10', 'R0.25', 29.449454083441474, 161.05054591655852], 'F4': ['D7', 'MCH10', 'R0.5', 30.014848591514337, 160.48515140848565], 'F10': ['E7', 'MCH10', 'R1', 22.423599868222016, 168.07640013177797], 'E11': ['F7', 'MCH10', 'R2', 25.453814706578097, 165.0461852934219], 'G2': ['G7', 'MCH10', 'R4', 22.232272147938676, 168.2677278520613], 'D10': ['C8', 'MCH25', 'R0.25', 19.952863126408122, 170.54713687359188], 'D11': ['D8', 'MCH25', 'R0.5', 20.93242953460398, 169.56757046539602], 'E10': ['E8', 'MCH25', 'R1', 22.70584719337278, 167.7941528066272], 'B7': ['F8', 'MCH25', 'R2', 18.77099086993087, 171.72900913006913], 'C9': ['G8', 'MCH25', 'R4', 21.83889004885966, 168.66110995114033], 'E5': ['C9', 'MCH50', 'R0.25', 30.864176064393018, 159.635823935607], 'G4': ['D9', 'MCH50', 'R0.5', 42.730687234932915, 147.76931276506707], 'C3': ['E9', 'MCH50', 'R1', 25.059413279995347, 165.44058672000466], 'E9': ['F9', 'MCH50', 'R2', 23.09721328014618, 167.40278671985382], 'D9': ['G9', 'MCH50', 'R4', 24.781359075873834, 165.71864092412616], 'C5': ['C10', 'MCH75', 'R0.25', 24.08153772859744, 166.41846227140257], 'D5': ['D10', 'MCH75', 'R0.5', 47.394095995482374, 143.10590400451764], 'G10': ['E10', 'MCH75', 'R1', 21.459187065901332, 169.04081293409865], 'G7': ['F10', 'MCH75', 'R2', 19.569891647312108, 170.93010835268788], 'D6': ['G10', 'MCH75', 'R4', 21.06404398623117, 169.43595601376882], 'B11': ['C11', 'MCH90', 'R0.25', 27.46615148321775, 163.03384851678226], 'D4': ['D11', 'MCH90', 'R0.5', 40.6563800332011, 149.84361996679888], 'E2': ['E11', 'MCH90', 'R1', 22.716846716682245, 167.78315328331774], 'C10': ['F11', 'MCH90', 'R2', 23.292211754035453, 167.20778824596454], 'B5': ['G11', 'MCH90', 'R4', 28.243527464786116, 162.25647253521387], 'B2': ['blank', 'blank', 'blank', 0, 190.5], 'B4': ['blank', 'blank', 'blank', 0, 190.5], 'B6': ['blank', 'blank', 'blank', 0, 190.5], 'B8': ['blank', 'blank', 'blank', 0, 190.5], 'C2': ['blank', 'blank', 'blank', 0, 190.5], 'E8': ['blank', 'blank', 'blank', 0, 190.5], 'F7': ['blank', 'blank', 'blank', 0, 190.5], 'F11': ['blank', 'blank', 'blank', 0, 190.5], 'G6': ['blank', 'blank', 'blank', 0, 190.5], 'G8': ['blank', 'blank', 'blank', 0, 190.5]}
iptg_volume = 9.5
metadata = {'protocolName': 'Burden_08_30_2024', 'author': 'Cameron <croots@utexas.edu>', 'description': 'Burden experiment on codon-specific strains', 'apiLevel': '2.18'}
