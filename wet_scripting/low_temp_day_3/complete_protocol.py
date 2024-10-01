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
final_positions = {'E3': ['C2', 'GFP10', 'R0.25', 18.69392982038717, 171.80607017961285], 'B8': ['D2', 'GFP10', 'R0.5', 17.14914670260788, 173.35085329739212], 'E6': ['E2', 'GFP10', 'R1', 21.989405484269057, 168.51059451573093], 'D2': ['F2', 'GFP10', 'R2', 22.082585358838923, 168.4174146411611], 'B11': ['G2', 'GFP10', 'R4', 20.790460473600376, 169.70953952639962], 'C3': ['C3', 'GFP25', 'R0.25', 17.4101490213863, 173.0898509786137], 'F3': ['D3', 'GFP25', 'R0.5', 16.685474298629043, 173.81452570137097], 'B9': ['E3', 'GFP25', 'R1', 19.0508150206494, 171.4491849793506], 'C5': ['F3', 'GFP25', 'R2', 23.323488312434463, 167.17651168756555], 'C9': ['G3', 'GFP25', 'R4', 15.942486148536709, 174.55751385146328], 'F6': ['C4', 'GFP50', 'R0.25', 17.117851898422142, 173.38214810157785], 'E11': ['D4', 'GFP50', 'R0.5', 22.30310572643579, 168.19689427356423], 'G11': ['E4', 'GFP50', 'R1', 23.24258057762914, 167.25741942237084], 'G2': ['F4', 'GFP50', 'R2', 21.515299695467153, 168.98470030453285], 'G9': ['G4', 'GFP50', 'R4', 17.626067278361546, 172.87393272163845], 'D7': ['C5', 'GFP75', 'R0.25', 21.070667110254778, 169.4293328897452], 'B4': ['D5', 'GFP75', 'R0.5', 17.579818475932033, 172.92018152406797], 'C11': ['E5', 'GFP75', 'R1', 17.092897429056798, 173.4071025709432], 'G8': ['F5', 'GFP75', 'R2', 18.200629150859797, 172.2993708491402], 'F8': ['G5', 'GFP75', 'R4', 17.827055713249084, 172.67294428675092], 'C4': ['C6', 'GFP90', 'R0.25', 15.100678895601535, 175.39932110439847], 'F2': ['D6', 'GFP90', 'R0.5', 17.867805513641144, 172.63219448635886], 'C10': ['E6', 'GFP90', 'R1', 17.639323691403174, 172.86067630859682], 'G3': ['F6', 'GFP90', 'R2', 19.144128205266696, 171.3558717947333], 'E2': ['G6', 'GFP90', 'R4', 14.200006049237137, 176.29999395076285], 'G7': ['C7', 'MCH10', 'R0.25', 30.79729523358231, 159.7027047664177], 'E9': ['D7', 'MCH10', 'R0.5', 19.62475503935079, 170.8752449606492], 'B2': ['E7', 'MCH10', 'R1', 20.095632722917355, 170.40436727708266], 'G5': ['F7', 'MCH10', 'R2', 21.72458188650354, 168.77541811349647], 'D5': ['G7', 'MCH10', 'R4', 18.753727649513944, 171.74627235048607], 'E7': ['C8', 'MCH25', 'R0.25', 16.035147261586083, 174.46485273841392], 'C2': ['D8', 'MCH25', 'R0.5', 17.416613371616144, 173.08338662838386], 'F7': ['E8', 'MCH25', 'R1', 17.136614686628036, 173.36338531337196], 'C6': ['F8', 'MCH25', 'R2', 15.947906387132713, 174.55209361286728], 'G10': ['G8', 'MCH25', 'R4', 15.723356734253668, 174.77664326574634], 'F9': ['C9', 'MCH50', 'R0.25', 13.823336826653135, 176.67666317334687], 'C7': ['D9', 'MCH50', 'R0.5', 15.30767985950352, 175.1923201404965], 'E10': ['E9', 'MCH50', 'R1', 15.634254018018598, 174.8657459819814], 'F5': ['F9', 'MCH50', 'R2', 15.115279770676281, 175.3847202293237], 'B10': ['G9', 'MCH50', 'R4', 13.823336826653135, 176.67666317334687], 'D8': ['C10', 'MCH75', 'R0.25', 14.899203065184919, 175.6007969348151], 'D4': ['D10', 'MCH75', 'R0.5', 14.480594771470749, 176.01940522852925], 'B5': ['E10', 'MCH75', 'R1', 16.00778131724418, 174.49221868275583], 'C8': ['F10', 'MCH75', 'R2', 13.694180930261366, 176.80581906973865], 'G6': ['G10', 'MCH75', 'R4', 13.335949092783512, 177.16405090721648], 'E5': ['C11', 'MCH90', 'R0.25', 12.47737379321832, 178.0226262067817], 'D3': ['D11', 'MCH90', 'R0.5', 14.552483167913241, 175.94751683208676], 'F4': ['E11', 'MCH90', 'R1', 12.769528144285875, 177.73047185571411], 'D10': ['F11', 'MCH90', 'R2', 12.717589573291066, 177.78241042670894], 'E8': ['G11', 'MCH90', 'R4', 12.166644712120203, 178.33335528787978], 'B3': ['blank', 'blank', 'blank', 0, 190.5], 'B6': ['blank', 'blank', 'blank', 0, 190.5], 'B7': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'D9': ['blank', 'blank', 'blank', 0, 190.5], 'D11': ['blank', 'blank', 'blank', 0, 190.5], 'E4': ['blank', 'blank', 'blank', 0, 190.5], 'F10': ['blank', 'blank', 'blank', 0, 190.5], 'F11': ['blank', 'blank', 'blank', 0, 190.5], 'G4': ['blank', 'blank', 'blank', 0, 190.5]}
iptg_volume = 9.5
metadata = {'protocolName': 'Burden_092524', 'author': 'Cameron <croots@utexas.edu>', 'description': 'Burden experiment on codon-specific strains', 'apiLevel': '2.18'}
