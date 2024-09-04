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
final_positions = {'D2': ['C2', 'GFP10', 'R0.25', 56.05497490318865, 134.44502509681135], 'C6': ['D2', 'GFP10', 'R0.5', 35.892861140300184, 154.60713885969983], 'F9': ['E2', 'GFP10', 'R1', 44.80863567809558, 145.69136432190442], 'E10': ['F2', 'GFP10', 'R2', 47.056490097762136, 143.44350990223785], 'C4': ['G2', 'GFP10', 'R4', 48.21754066561134, 142.28245933438865], 'B2': ['C3', 'GFP25', 'R0.25', 31.868721841202678, 158.63127815879733], 'B4': ['D3', 'GFP25', 'R0.5', 32.1527388768729, 158.3472611231271], 'G2': ['E3', 'GFP25', 'R1', 30.206222473853018, 160.29377752614698], 'D11': ['F3', 'GFP25', 'R2', 38.42156176727959, 152.0784382327204], 'C10': ['G3', 'GFP25', 'R4', 26.95935877745282, 163.54064122254718], 'F7': ['C4', 'GFP50', 'R0.25', 43.886219014310825, 146.61378098568917], 'F3': ['D4', 'GFP50', 'R0.5', 25.959595930974118, 164.5404040690259], 'B5': ['E4', 'GFP50', 'R1', 34.117405896201745, 156.38259410379825], 'F6': ['F4', 'GFP50', 'R2', 21.63638954177945, 168.86361045822053], 'B6': ['G4', 'GFP50', 'R4', 32.59970912891794, 157.90029087108206], 'C3': ['C5', 'GFP75', 'R0.25', 30.109263068303914, 160.3907369316961], 'D6': ['D5', 'GFP75', 'R0.5', 29.63366386714294, 160.86633613285707], 'E11': ['E5', 'GFP75', 'R1', 32.71339849566044, 157.78660150433956], 'E8': ['F5', 'GFP75', 'R2', 28.568679464291062, 161.93132053570895], 'D8': ['G5', 'GFP75', 'R4', 29.540342448038086, 160.95965755196193], 'F5': ['C6', 'GFP90', 'R0.25', 33.46022870596006, 157.03977129403995], 'D10': ['D6', 'GFP90', 'R0.5', 32.50932232502591, 157.99067767497408], 'D5': ['E6', 'GFP90', 'R1', 35.431896951017144, 155.06810304898286], 'B7': ['F6', 'GFP90', 'R2', 23.667153802885498, 166.8328461971145], 'D4': ['G6', 'GFP90', 'R4', 31.025468079996916, 159.47453192000307], 'E7': ['C7', 'MCH10', 'R0.25', 60.77646853532118, 129.7235314646788], 'G5': ['D7', 'MCH10', 'R0.5', 27.48063482924493, 163.01936517075507], 'E6': ['E7', 'MCH10', 'R1', 27.336480372234963, 163.16351962776503], 'D7': ['F7', 'MCH10', 'R2', 24.740833350421198, 165.7591666495788], 'G11': ['G7', 'MCH10', 'R4', 23.084707301350047, 167.41529269864995], 'C7': ['C8', 'MCH25', 'R0.25', 23.256410106877254, 167.24358989312276], 'F4': ['D8', 'MCH25', 'R0.5', 24.675750711148204, 165.8242492888518], 'E5': ['E8', 'MCH25', 'R1', 23.643291773979808, 166.8567082260202], 'F10': ['F8', 'MCH25', 'R2', 23.703039078656154, 166.79696092134384], 'C8': ['G8', 'MCH25', 'R4', 23.40729498645498, 167.09270501354501], 'C2': ['C9', 'MCH50', 'R0.25', 23.82343697625881, 166.67656302374118], 'F11': ['D9', 'MCH50', 'R0.5', 38.07842740037595, 152.42157259962406], 'B11': ['E9', 'MCH50', 'R1', 23.54832641939199, 166.951673580608], 'B3': ['F9', 'MCH50', 'R2', 22.454733367616612, 168.0452666323834], 'G4': ['G9', 'MCH50', 'R4', 23.454117390801738, 167.04588260919826], 'E2': ['C10', 'MCH75', 'R0.25', 30.402023894383568, 160.09797610561643], 'C5': ['D10', 'MCH75', 'R0.5', 41.26084073989592, 149.2391592601041], 'G3': ['E10', 'MCH75', 'R1', 23.221863454756424, 167.27813654524357], 'G6': ['F10', 'MCH75', 'R2', 22.273447538343582, 168.2265524616564], 'E9': ['G10', 'MCH75', 'R4', 22.815195484089404, 167.6848045159106], 'C11': ['C11', 'MCH90', 'R0.25', 37.469998822285824, 153.03000117771418], 'E4': ['D11', 'MCH90', 'R0.5', 30.323398333737583, 160.17660166626243], 'B9': ['E11', 'MCH90', 'R1', 29.63366386714294, 160.86633613285707], 'E3': ['F11', 'MCH90', 'R2', 32.02102936992113, 158.47897063007886], 'G9': ['G11', 'MCH90', 'R4', 27.806486383906353, 162.69351361609364], 'B8': ['blank', 'blank', 'blank', 0, 190.5], 'B10': ['blank', 'blank', 'blank', 0, 190.5], 'C9': ['blank', 'blank', 'blank', 0, 190.5], 'D3': ['blank', 'blank', 'blank', 0, 190.5], 'D9': ['blank', 'blank', 'blank', 0, 190.5], 'F2': ['blank', 'blank', 'blank', 0, 190.5], 'F8': ['blank', 'blank', 'blank', 0, 190.5], 'G7': ['blank', 'blank', 'blank', 0, 190.5], 'G8': ['blank', 'blank', 'blank', 0, 190.5], 'G10': ['blank', 'blank', 'blank', 0, 190.5]}
iptg_volume = 9.5
metadata = {'protocolName': 'Burden_08_28_2024', 'author': 'Cameron <croots@utexas.edu>', 'description': 'Burden experiment on codon-specific strains', 'apiLevel': '2.18'}
