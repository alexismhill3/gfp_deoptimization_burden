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
final_positions = {'F3': ['C2', 'GFP50', 'R0.25', 14.621897663935487, 175.8781023360645], 'E2': ['D2', 'GFP50', 'R0.5', 18.555626726630983, 171.94437327336902], 'E5': ['E2', 'GFP50', 'R1', 17.761570270277886, 172.7384297297221], 'F2': ['F2', 'GFP50', 'R2', 19.82634322856933, 170.67365677143067], 'B3': ['G2', 'GFP50', 'R4', 14.603686000536465, 175.89631399946353], 'F6': ['C3', 'GAG', 'R0.25', 18.45341427815058, 172.04658572184942], 'E4': ['D3', 'GAG', 'R0.5', 19.859925000877546, 170.64007499912245], 'D5': ['E3', 'GAG', 'R1', 16.505207549378056, 173.99479245062196], 'F4': ['F3', 'GAG', 'R2', 19.902061274100294, 170.5979387258997], 'C6': ['G3', 'GAG', 'R4', 16.940403444705485, 173.55959655529452], 'G3': ['C4', 'GGA', 'R0.25', 14.886433620150964, 175.61356637984903], 'D2': ['D4', 'GGA', 'R0.5', 21.01684944530203, 169.48315055469797], 'B4': ['E4', 'GGA', 'R1', 20.747235378349544, 169.75276462165044], 'G2': ['F4', 'GGA', 'R2', 26.97641640870943, 163.52358359129056], 'B2': ['G4', 'GGA', 'R4', 17.741412811419032, 172.75858718858098], 'D4': ['C5', 'GGG', 'R0.25', 17.707921184867722, 172.79207881513227], 'F5': ['D5', 'GGG', 'R0.5', 16.202998748468232, 174.29700125153175], 'G6': ['E5', 'GGG', 'R1', 24.547890438958515, 165.95210956104148], 'B6': ['F5', 'GGG', 'R2', 19.264438078410702, 171.2355619215893], 'G5': ['G5', 'GGG', 'R4', 17.354103345549927, 173.14589665445007], 'C3': ['C6', 'CTA', 'R0.25', 18.352323862076737, 172.14767613792327], 'B5': ['D6', 'CTA', 'R0.5', 25.412440890883087, 165.0875591091169], 'D3': ['E6', 'CTA', 'R1', 25.032662516049925, 165.46733748395008], 'C2': ['F6', 'CTA', 'R2', 22.137827220314364, 168.36217277968564], 'C5': ['G6', 'CTA', 'R4', 15.339220719624647, 175.16077928037535], 'D11': ['C7', 'GFP50', 'R0.25', 16.545968458671815, 173.9540315413282], 'B7': ['D7', 'GFP50', 'R0.5', 18.644140704072292, 171.8558592959277], 'B10': ['E7', 'GFP50', 'R1', 17.842654178576506, 172.6573458214235], 'F8': ['F7', 'GFP50', 'R2', 20.0638265923785, 170.4361734076215], 'F9': ['G7', 'GFP50', 'R4', 15.993043517710165, 174.50695648228984], 'B9': ['C8', 'GAG', 'R0.25', 19.264438078410702, 171.2355619215893], 'B11': ['D8', 'GAG', 'R0.5', 20.430910141315163, 170.06908985868483], 'C8': ['E8', 'GAG', 'R1', 17.562045511662518, 172.93795448833748], 'G11': ['F8', 'GAG', 'R2', 24.281011442016972, 166.21898855798304], 'G10': ['G8', 'GAG', 'R4', 17.33486154819291, 173.16513845180708], 'D8': ['C9', 'GGA', 'R0.25', 15.693367658871935, 174.80663234112808], 'C7': ['D9', 'GGA', 'R0.5', 20.236970086109295, 170.2630299138907], 'F11': ['E9', 'GGA', 'R1', 21.216501986481937, 169.28349801351806], 'D10': ['F9', 'GGA', 'R2', 28.657702342556888, 161.8422976574431], 'D9': ['G9', 'GGA', 'R4', 19.537282578730437, 170.96271742126956], 'E10': ['C10', 'GGG', 'R0.25', 18.202748015877653, 172.29725198412234], 'G8': ['D10', 'GGG', 'R0.5', 16.60454579867784, 173.89545420132217], 'G7': ['E10', 'GGG', 'R1', 25.18049898308185, 165.31950101691814], 'F7': ['F10', 'GGG', 'R2', 18.65155408086203, 171.84844591913796], 'D7': ['G10', 'GGG', 'R4', 17.667896577888893, 172.83210342211112], 'C9': ['C11', 'CTA', 'R0.25', 19.099691597263448, 171.40030840273656], 'E7': ['D11', 'CTA', 'R0.5', 24.193336652005872, 166.30666334799412], 'B8': ['E11', 'CTA', 'R1', 25.18049898308185, 165.31950101691814], 'C11': ['F11', 'CTA', 'R2', 20.14137297672495, 170.35862702327506], 'E11': ['G11', 'CTA', 'R4', 15.274278701790985, 175.225721298209], 'E3': ['blank', 'blank', 'blank', 0, 190.5], 'C4': ['blank', 'blank', 'blank', 0, 190.5], 'G4': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'E6': ['blank', 'blank', 'blank', 0, 190.5], 'E8': ['blank', 'blank', 'blank', 0, 190.5], 'E9': ['blank', 'blank', 'blank', 0, 190.5], 'G9': ['blank', 'blank', 'blank', 0, 190.5], 'C10': ['blank', 'blank', 'blank', 0, 190.5], 'F10': ['blank', 'blank', 'blank', 0, 190.5]}
iptg_volume = 9.5
metadata = {'protocolName': 'Burden_092624', 'author': 'Cameron <croots@utexas.edu>', 'description': 'Burden experiment on codon-specific strains', 'apiLevel': '2.18'}
induced_wells = ['B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6']
uninduced_wells = ['B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'B9', 'C9', 'D9', 'E9', 'F9', 'G9', 'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'B11', 'C11', 'D11', 'E11', 'F11', 'G11']