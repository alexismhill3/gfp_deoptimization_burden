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
final_positions = {'E4': ['C2', 'MCH10', 'R0.25', 42.15459120062498, 148.34540879937504], 'D2': ['D2', 'MCH10', 'R0.5', 21.9000744274361, 168.5999255725639], 'B5': ['E2', 'MCH10', 'R1', 21.31291482104403, 169.18708517895598], 'B4': ['F2', 'MCH10', 'R2', 17.386269903184708, 173.1137300968153], 'B2': ['G2', 'MCH10', 'R4', 16.716994923066572, 173.78300507693342], 'C2': ['C3', 'MCH25', 'R0.25', 15.314177636803569, 175.18582236319642], 'D4': ['D3', 'MCH25', 'R0.5', 15.029545313020218, 175.4704546869798], 'D5': ['E3', 'MCH25', 'R1', 15.98759190962245, 174.51240809037756], 'F2': ['F3', 'MCH25', 'R2', 20.84868358277926, 169.65131641722076], 'G4': ['G3', 'MCH25', 'R4', 20.92309128132677, 169.57690871867322], 'C6': ['C4', 'MCH50', 'R0.25', 13.28796471898788, 177.2120352810121], 'B3': ['D4', 'MCH50', 'R0.5', 13.84087772452074, 176.65912227547926], 'B6': ['E4', 'MCH50', 'R1', 16.716994923066572, 173.78300507693342], 'D3': ['F4', 'MCH50', 'R2', 16.00942132358338, 174.49057867641662], 'C5': ['G4', 'MCH50', 'R4', 12.224678224913049, 178.27532177508695], 'E6': ['C5', 'MCH75', 'R0.25', 13.375121058066568, 177.12487894193345], 'E2': ['D5', 'MCH75', 'R0.5', 17.001813177625767, 173.49818682237424], 'G5': ['E5', 'MCH75', 'R1', 14.755301775305183, 175.74469822469482], 'E3': ['F5', 'MCH75', 'R2', 12.650016140594028, 177.84998385940597], 'C4': ['G5', 'MCH75', 'R4', 13.011485656419913, 177.48851434358008], 'F4': ['C6', 'MCH90', 'R0.25', 13.707388598833766, 176.79261140116623], 'E5': ['D6', 'MCH90', 'R0.5', 13.401874240549713, 177.09812575945028], 'C3': ['E6', 'MCH90', 'R1', 12.656843769236994, 177.84315623076301], 'F5': ['F6', 'MCH90', 'R2', 12.975488020075549, 177.52451197992445], 'G3': ['G6', 'MCH90', 'R4', 11.920194798370863, 178.57980520162914], 'F11': ['C7', 'MCH10', 'R0.25', 49.28667505997688, 141.2133249400231], 'C7': ['D7', 'MCH10', 'R0.5', 23.478774831798223, 167.02122516820177], 'F10': ['E7', 'MCH10', 'R1', 20.876525753118045, 169.62347424688195], 'B8': ['F7', 'MCH10', 'R2', 18.778506664202258, 171.72149333579773], 'G7': ['G7', 'MCH10', 'R4', 19.05313555135886, 171.44686444864115], 'B9': ['C8', 'MCH25', 'R0.25', 16.581065511229383, 173.91893448877062], 'E8': ['D8', 'MCH25', 'R0.5', 14.46407186856152, 176.03592813143848], 'F8': ['E8', 'MCH25', 'R1', 15.719667643754843, 174.78033235624517], 'C10': ['F8', 'MCH25', 'R2', 23.53768899444123, 166.96231100555877], 'E9': ['G8', 'MCH25', 'R4', 21.798290668831644, 168.70170933116836], 'G9': ['C9', 'MCH50', 'R0.25', 13.755631020474501, 176.7443689795255], 'G10': ['D9', 'MCH50', 'R0.5', 14.379813970934546, 176.12018602906545], 'D7': ['E9', 'MCH50', 'R1', 16.418539171567733, 174.08146082843226], 'F7': ['F9', 'MCH50', 'R2', 15.394603825350991, 175.105396174649], 'B7': ['G9', 'MCH50', 'R4', 14.086137013384448, 176.41386298661556], 'E11': ['C10', 'MCH75', 'R0.25', 13.08408238970138, 177.4159176102986], 'B10': ['D10', 'MCH75', 'R0.5', 16.55180619507654, 173.94819380492345], 'G11': ['E10', 'MCH75', 'R1', 14.690596608325702, 175.8094033916743], 'E10': ['F10', 'MCH75', 'R2', 13.771787778762818, 176.7282122212372], 'F9': ['G10', 'MCH75', 'R4', 13.124355920146758, 177.37564407985323], 'C11': ['C11', 'MCH90', 'R0.25', 13.348474473637035, 177.15152552636297], 'D9': ['D11', 'MCH90', 'R0.5', 13.401874240549713, 177.09812575945028], 'B11': ['E11', 'MCH90', 'R1', 13.939606417919356, 176.56039358208065], 'E7': ['F11', 'MCH90', 'R2', 12.373027767561293, 178.1269722324387], 'D11': ['G11', 'MCH90', 'R4', 13.022323389317444, 177.47767661068255], 'G2': ['blank', 'blank', 'blank', 0, 190.5], 'F3': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'F6': ['blank', 'blank', 'blank', 0, 190.5], 'G6': ['blank', 'blank', 'blank', 0, 190.5], 'C8': ['blank', 'blank', 'blank', 0, 190.5], 'D8': ['blank', 'blank', 'blank', 0, 190.5], 'G8': ['blank', 'blank', 'blank', 0, 190.5], 'C9': ['blank', 'blank', 'blank', 0, 190.5], 'D10': ['blank', 'blank', 'blank', 0, 190.5]}
iptg_volume = 9.5
metadata = {'protocolName': 'Burden_100224', 'author': 'Cameron <croots@utexas.edu>', 'description': 'Burden experiment on codon-specific strains', 'apiLevel': '2.18'}
induced_wells = ['B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6']
uninduced_wells = ['B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11']