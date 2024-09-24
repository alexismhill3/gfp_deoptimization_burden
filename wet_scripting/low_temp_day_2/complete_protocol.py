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
final_positions = {'C5': ['C2', 'GFP10', 'R0.25', 21.560795748136297, 168.9392042518637], 'G8': ['D2', 'GFP10', 'R0.5', 17.31118836608703, 173.18881163391296], 'G5': ['E2', 'GFP10', 'R1', 23.913322789418682, 166.5866772105813], 'F8': ['F2', 'GFP10', 'R2', 20.478190126312423, 170.02180987368757], 'F2': ['G2', 'GFP10', 'R4', 20.292130279312843, 170.20786972068714], 'F3': ['C3', 'GFP25', 'R0.25', 17.279298013507784, 173.2207019864922], 'E3': ['D3', 'GFP25', 'R0.5', 19.474816522059754, 171.02518347794023], 'E9': ['E3', 'GFP25', 'R1', 18.638953962748037, 171.86104603725195], 'C9': ['F3', 'GFP25', 'R2', 23.671932078720214, 166.8280679212798], 'E5': ['G3', 'GFP25', 'R4', 16.559404062124, 173.940595937876], 'F5': ['C4', 'GFP50', 'R0.25', 17.616796877538818, 172.88320312246117], 'G10': ['D4', 'GFP50', 'R0.5', 18.233176098097736, 172.26682390190226], 'C7': ['E4', 'GFP50', 'R1', 25.036673236711888, 165.4633267632881], 'E2': ['F4', 'GFP50', 'R2', 24.577479287862943, 165.92252071213704], 'B4': ['G4', 'GFP50', 'R4', 18.477405540415074, 172.02259445958492], 'B8': ['C5', 'GFP75', 'R0.25', 18.76573538967418, 171.73426461032582], 'C11': ['D5', 'GFP75', 'R0.5', 18.325792276582515, 172.17420772341748], 'G4': ['E5', 'GFP75', 'R1', 17.65659003749864, 172.84340996250137], 'E11': ['F5', 'GFP75', 'R2', 17.663238723918987, 172.836761276081], 'D3': ['G5', 'GFP75', 'R4', 16.380120438187678, 174.11987956181233], 'B10': ['C6', 'GFP90', 'R0.25', 16.06590552770781, 174.4340944722922], 'C8': ['D6', 'GFP90', 'R0.5', 17.260221652028388, 173.23977834797162], 'D11': ['E6', 'GFP90', 'R1', 18.01605557954129, 172.4839444204587], 'G3': ['F6', 'GFP90', 'R2', 18.254467178987547, 172.24553282101246], 'C3': ['G6', 'GFP90', 'R4', 16.351567097328047, 174.14843290267194], 'D2': ['C7', 'MCH10', 'R0.25', 28.316849905931395, 162.1831500940686], 'G7': ['D7', 'MCH10', 'R0.5', 24.487650582587335, 166.01234941741268], 'C6': ['E7', 'MCH10', 'R1', 21.964689154932184, 168.5353108450678], 'E7': ['F7', 'MCH10', 'R2', 24.34781888993494, 166.15218111006507], 'D10': ['G7', 'MCH10', 'R4', 25.779805688928054, 164.72019431107194], 'E4': ['C8', 'MCH25', 'R0.25', 16.718782409643612, 173.7812175903564], 'B3': ['D8', 'MCH25', 'R0.5', 17.689887594039167, 172.81011240596084], 'E10': ['E8', 'MCH25', 'R1', 19.728768843520225, 170.7712311564798], 'G11': ['F8', 'MCH25', 'R2', 21.06688352925484, 169.43311647074515], 'F9': ['G8', 'MCH25', 'R4', 18.462857874802886, 172.0371421251971], 'E8': ['C9', 'MCH50', 'R0.25', 14.701187551642303, 175.7988124483577], 'B2': ['D9', 'MCH50', 'R0.5', 15.026175149236831, 175.47382485076318], 'F4': ['E9', 'MCH50', 'R1', 17.381758187495784, 173.1182418125042], 'D8': ['F9', 'MCH50', 'R2', 16.323113129919943, 174.17688687008007], 'D6': ['G9', 'MCH50', 'R4', 14.632390565043545, 175.86760943495645], 'D5': ['C10', 'MCH75', 'R0.25', 15.864831010266537, 174.63516898973347], 'B7': ['D10', 'MCH75', 'R0.5', 13.965756668053631, 176.53424333194636], 'E6': ['E10', 'MCH75', 'R1', 17.912844580036403, 172.5871554199636], 'B5': ['F10', 'MCH75', 'R2', 15.538946470807463, 174.96105352919253], 'G2': ['G10', 'MCH75', 'R4', 13.62891922604114, 176.87108077395885], 'F10': ['C11', 'MCH90', 'R0.25', 12.58991202337768, 177.91008797662232], 'C4': ['D11', 'MCH90', 'R0.5', 16.28344320064099, 174.216556799359], 'D7': ['E11', 'MCH90', 'R1', 13.805434251608764, 176.69456574839123], 'D4': ['F11', 'MCH90', 'R2', 13.056036368061545, 177.44396363193846], 'G6': ['G11', 'MCH90', 'R4', 12.654453617151365, 177.84554638284862], 'B6': ['blank', 'blank', 'blank', 0, 190.5], 'B9': ['blank', 'blank', 'blank', 0, 190.5], 'B11': ['blank', 'blank', 'blank', 0, 190.5], 'C2': ['blank', 'blank', 'blank', 0, 190.5], 'C10': ['blank', 'blank', 'blank', 0, 190.5], 'D9': ['blank', 'blank', 'blank', 0, 190.5], 'F6': ['blank', 'blank', 'blank', 0, 190.5], 'F7': ['blank', 'blank', 'blank', 0, 190.5], 'F11': ['blank', 'blank', 'blank', 0, 190.5], 'G9': ['blank', 'blank', 'blank', 0, 190.5]}
iptg_volume = 9.5
metadata = {'protocolName': 'Burden_092424', 'author': 'Cameron <croots@utexas.edu>', 'description': 'Burden experiment on codon-specific strains', 'apiLevel': '2.18'}
