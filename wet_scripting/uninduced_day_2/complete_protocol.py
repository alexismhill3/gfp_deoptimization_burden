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
final_positions = {'C6': ['C2', 'GFP50', 'R0.25', 18.036841082087488, 172.46315891791252], 'E6': ['D2', 'GFP50', 'R0.5', 22.32008897721123, 168.17991102278876], 'B3': ['E2', 'GFP50', 'R1', 19.466732959836342, 171.03326704016365], 'F3': ['F2', 'GFP50', 'R2', 16.11558944981405, 174.38441055018595], 'G5': ['G2', 'GFP50', 'R4', 16.221491350370783, 174.2785086496292], 'G6': ['C3', 'GAG', 'R0.25', 19.211567922062915, 171.28843207793707], 'B6': ['D3', 'GAG', 'R0.5', 18.029908218211297, 172.4700917817887], 'D4': ['E3', 'GAG', 'R1', 19.08647754930039, 171.41352245069962], 'D3': ['F3', 'GAG', 'R2', 20.469252341582436, 170.03074765841757], 'B5': ['G3', 'GAG', 'R4', 17.906005469702997, 172.593994530297], 'E3': ['C4', 'GGA', 'R0.25', 16.863049331697663, 173.63695066830235], 'F2': ['D4', 'GGA', 'R0.5', 20.05781846591816, 170.44218153408184], 'G3': ['E4', 'GGA', 'R1', 20.5050493048543, 169.9949506951457], 'C3': ['F4', 'GGA', 'R2', 25.55505727160417, 164.94494272839583], 'B2': ['G4', 'GGA', 'R4', 18.765734047068293, 171.7342659529317], 'C5': ['C5', 'GGG', 'R0.25', 19.250995169094075, 171.24900483090593], 'C4': ['D5', 'GGG', 'R0.5', 18.397677793388027, 172.10232220661197], 'E5': ['E5', 'GGG', 'R1', 20.25707327627014, 170.24292672372985], 'E2': ['F5', 'GGG', 'R2', 17.892343310930894, 172.6076566890691], 'F5': ['G5', 'GGG', 'R4', 18.668629455913955, 171.83137054408604], 'D5': ['C6', 'CTA', 'R0.25', 18.63154927337497, 171.86845072662504], 'G2': ['D6', 'CTA', 'R0.5', 18.947683572126472, 171.55231642787354], 'F4': ['E6', 'CTA', 'R1', 19.929971014045194, 170.57002898595482], 'C2': ['F6', 'CTA', 'R2', 19.314418376851926, 171.18558162314807], 'G4': ['G6', 'CTA', 'R4', 15.270797901083116, 175.2292020989169], 'D8': ['C7', 'GFP50', 'R0.25', 16.96061860922678, 173.53938139077323], 'G9': ['D7', 'GFP50', 'R0.5', 20.640409028505143, 169.85959097149487], 'G10': ['E7', 'GFP50', 'R1', 18.470128626284094, 172.0298713737159], 'C9': ['F7', 'GFP50', 'R2', 15.60616259949516, 174.89383740050485], 'F8': ['G7', 'GFP50', 'R4', 15.806019348333471, 174.69398065166652], 'B11': ['C8', 'GAG', 'R0.25', 19.211567922062915, 171.28843207793707], 'C11': ['D8', 'GAG', 'R0.5', 17.146639206919797, 173.3533607930802], 'D10': ['E8', 'GAG', 'R1', 18.26868689936381, 172.23131310063619], 'D7': ['F8', 'GAG', 'R2', 19.410338249927996, 171.089661750072], 'F11': ['G8', 'GAG', 'R4', 18.521187287709992, 171.97881271229], 'F7': ['C9', 'GGA', 'R0.25', 15.811347174693832, 174.68865282530618], 'C10': ['D9', 'GGA', 'R0.5', 18.83355385433996, 171.66644614566005], 'D9': ['E9', 'GGA', 'R1', 19.172301843903526, 171.32769815609646], 'C7': ['F9', 'GGA', 'R2', 26.30022775082969, 164.1997722491703], 'B8': ['G9', 'GGA', 'R4', 18.470128626284094, 172.0298713737159], 'E9': ['C10', 'GGG', 'R0.25', 19.43446666584052, 171.06553333415948], 'B9': ['D10', 'GGG', 'R0.5', 17.97462837278839, 172.5253716272116], 'E7': ['E10', 'GGG', 'R1', 19.703903113521363, 170.79609688647864], 'C8': ['F10', 'GGG', 'R2', 17.40756462470755, 173.09243537529244], 'E10': ['G10', 'GGG', 'R4', 18.53582487220107, 171.96417512779894], 'G8': ['C11', 'CTA', 'R0.25', 18.871443265186592, 171.6285567348134], 'F9': ['D11', 'CTA', 'R0.5', 23.9499568448945, 166.5500431551055], 'B10': ['E11', 'CTA', 'R1', 19.703903113521363, 170.79609688647864], 'G7': ['F11', 'CTA', 'R2', 18.818440206647484, 171.6815597933525], 'B7': ['G11', 'CTA', 'R4', 15.554405142350797, 174.9455948576492], 'D2': ['blank', 'blank', 'blank', 0, 190.5], 'B4': ['blank', 'blank', 'blank', 0, 190.5], 'E4': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'F6': ['blank', 'blank', 'blank', 0, 190.5], 'E8': ['blank', 'blank', 'blank', 0, 190.5], 'F10': ['blank', 'blank', 'blank', 0, 190.5], 'D11': ['blank', 'blank', 'blank', 0, 190.5], 'E11': ['blank', 'blank', 'blank', 0, 190.5], 'G11': ['blank', 'blank', 'blank', 0, 190.5]}
iptg_volume = 9.5
metadata = {'protocolName': 'Burden_092724', 'author': 'Cameron <croots@utexas.edu>', 'description': 'Burden experiment on codon-specific strains', 'apiLevel': '2.18'}
induced_wells = ['B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6']
uninduced_wells = ['B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11']
