import pandas as pd
from rich import print

day_1_key = {
    'B2': ['blank', 'blank'],
    'C2': ['GFP10', 'R0.25'],
    'D2': ['GFP10', 'R0.5'],
    'E2': ['GFP10', 'R1'],
    'F2': ['GFP10', 'R2'],
    'G2': ['GFP10', 'R4'],

    'B3': ['blank', 'blank'],
    'C3': ['GFP25', 'R0.25'],
    'D3': ['GFP25', 'R0.5'],
    'E3': ['GFP25', 'R1'],
    'F3': ['GFP25', 'R2'],
    'G3': ['GFP25', 'R4'],

    'B4': ['blank', 'blank'],
    'C4': ['GFP50', 'R0.25'],
    'D4': ['GFP50', 'R0.5'],
    'E4': ['GFP50', 'R1'],
    'F4': ['GFP50', 'R2'],
    'G4': ['GFP50', 'R4'],

    'B5': ['blank', 'blank'],
    'C5': ['GFP75', 'R0.25'],
    'D5': ['GFP75', 'R0.5'],
    'E5': ['GFP75', 'R1'],
    'F5': ['GFP75', 'R2'],
    'G5': ['GFP75', 'R4'],

    'B6': ['blank', 'blank'],
    'C6': ['GFP90', 'R0.25'],
    'D6': ['GFP90', 'R0.5'],
    'E6': ['GFP90', 'R1'],
    'F6': ['GFP90', 'R2'],
    'G6': ['GFP90', 'R4'],

    'B7': ['blank', 'blank'],
    'C7': ['MCH10', 'R0.25'],
    'D7': ['MCH10', 'R0.5'],
    'E7': ['MCH10', 'R1'],
    'F7': ['MCH10', 'R2'],
    'G7': ['MCH10', 'R4'],

    'B8': ['blank', 'blank'],
    'C8': ['MCH25', 'R0.25'],
    'D8': ['MCH25', 'R0.5'],
    'E8': ['MCH25', 'R1'],
    'F8': ['MCH25', 'R2'],
    'G8': ['MCH25', 'R4'],

    'B9': ['blank', 'blank'],
    'C9': ['MCH50', 'R0.25'],
    'D9': ['MCH50', 'R0.5'],
    'E9': ['MCH50', 'R1'],
    'F9': ['MCH50', 'R2'],
    'G9': ['MCH50', 'R4'],

    'B10': ['blank', 'blank'],
    'C10': ['MCH75', 'R0.25'],
    'D10': ['MCH75', 'R0.5'],
    'E10': ['MCH75', 'R1'],
    'F10': ['MCH75', 'R2'],
    'G10': ['MCH75', 'R4'],

    'B11': ['blank', 'blank'],
    'C11': ['MCH90', 'R0.25'],
    'D11': ['MCH90', 'R0.5'],
    'E11': ['MCH90', 'R1'],
    'F11': ['MCH90', 'R2'],
    'G11': ['MCH90', 'R4'],
}

day_2_key = day_1_key

day_3_key = day_1_key

day_4_key = {
    'B2': ['blank', 'blank'],
    'C2': ['GFP50', 'R0.25'],
    'D2': ['GFP50', 'R0.5'],
    'E2': ['GFP50', 'R1'],
    'F2': ['GFP50', 'R2'],
    'G2': ['GFP50', 'R4'],

    'B3': ['blank', 'blank'],
    'C3': ['GGG', 'R0.25'],
    'D3': ['GGG', 'R0.5'],
    'E3': ['GGG', 'R1'],
    'F3': ['GGG', 'R2'],
    'G3': ['GGG', 'R4'],

    'B4': ['blank', 'blank'],
    'C4': ['GGA', 'R0.25'],
    'D4': ['GGA', 'R0.5'],
    'E4': ['GGA', 'R1'],
    'F4': ['GGA', 'R2'],
    'G4': ['GGA', 'R4'],

    'B5': ['blank', 'blank'],
    'C5': ['GAG', 'R0.25'],
    'D5': ['GAG', 'R0.5'],
    'E5': ['GAG', 'R1'],
    'F5': ['GAG', 'R2'],
    'G5': ['GAG', 'R4'],

    'B6': ['blank', 'blank'],
    'C6': ['CTA', 'R0.25'],
    'D6': ['CTA', 'R0.5'],
    'E6': ['CTA', 'R1'],
    'F6': ['CTA', 'R2'],
    'G6': ['CTA', 'R4'],
}

day_5_key = {
    'B2': ['blank', 'blank'],
    'C2': ['GFP50', 'R0.25'],
    'D2': ['GFP50', 'R0.5'],
    'E2': ['GFP50', 'R1'],
    'F2': ['GFP50', 'R2'],
    'G2': ['GFP50', 'R4'],

    'B3': ['blank', 'blank'],
    'C3': ['GGG', 'R0.25'],
    'D3': ['GGG', 'R0.5'],
    'E3': ['GGG', 'R1'],
    'F3': ['GGG', 'R2'],
    'G3': ['GGG', 'R4'],

    'B4': ['blank', 'blank'],
    'C4': ['GAG', 'R0.25'],
    'D4': ['GAG', 'R0.5'],
    'E4': ['GAG', 'R1'],
    'F4': ['GAG', 'R2'],
    'G4': ['GAG', 'R4'],

    'B5': ['blank', 'blank'],
    'C5': ['GGA', 'R0.25'],
    'D5': ['GGA', 'R0.5'],
    'E5': ['GGA', 'R1'],
    'F5': ['GGA', 'R2'],
    'G5': ['GGA', 'R4'],

    'B6': ['blank', 'blank'],
    'C6': ['CTA', 'R0.25'],
    'D6': ['CTA', 'R0.5'],
    'E6': ['CTA', 'R1'],
    'F6': ['CTA', 'R2'],
    'G6': ['CTA', 'R4'],
}

day_6_key = {
    'B2': ['blank', 'blank'],
    'C2': ['GFP50', 'R0.25'],
    'D2': ['GFP50', 'R0.5'],
    'E2': ['GFP50', 'R1'],
    'F2': ['GFP50', 'R2'],
    'G2': ['GFP50', 'R4'],

    'B3': ['blank', 'blank'],
    'C3': ['GGG', 'R0.25'],
    'D3': ['GGG', 'R0.5'],
    'E3': ['GGG', 'R1'],
    'F3': ['GGG', 'R2'],
    'G3': ['GGG', 'R4'],

    'B4': ['blank', 'blank'],
    'C4': ['GGA', 'R0.25'],
    'D4': ['GGA', 'R0.5'],
    'E4': ['GGA', 'R1'],
    'F4': ['GGA', 'R2'],
    'G4': ['GGA', 'R4'],

    'B5': ['blank', 'blank'],
    'C5': ['GAG', 'R0.25'],
    'D5': ['GAG', 'R0.5'],
    'E5': ['GAG', 'R1'],
    'F5': ['GAG', 'R2'],
    'G5': ['GAG', 'R4'],

    'B6': ['blank', 'blank'],
    'C6': ['CTA', 'R0.25'],
    'D6': ['CTA', 'R0.5'],
    'E6': ['CTA', 'R1'],
    'F6': ['CTA', 'R2'],
    'G6': ['CTA', 'R4'],
}

day_7_key = {
    'B2': ['blank', 'blank'],
    'C2': ['GFP10', 'R0.25'],
    'D2': ['GFP10', 'R0.5'],
    'E2': ['GFP10', 'R1'],
    'F2': ['GFP10', 'R2'],
    'G2': ['GFP10', 'R4'],

    'B3': ['blank', 'blank'],
    'C3': ['GFP25', 'R0.25'],
    'D3': ['GFP25', 'R0.5'],
    'E3': ['GFP25', 'R1'],
    'F3': ['GFP25', 'R2'],
    'G3': ['GFP25', 'R4'],

    'B4': ['blank', 'blank'],
    'C4': ['GFP50', 'R0.25'],
    'D4': ['GFP50', 'R0.5'],
    'E4': ['GFP50', 'R1'],
    'F4': ['GFP50', 'R2'],
    'G4': ['GFP50', 'R4'],

    'B5': ['blank', 'blank'],
    'C5': ['GFP75', 'R0.25'],
    'D5': ['GFP75', 'R0.5'],
    'E5': ['GFP75', 'R1'],
    'F5': ['GFP75', 'R2'],
    'G5': ['GFP75', 'R4'],

    'B6': ['blank', 'blank'],
    'C6': ['GFP90', 'R0.25'],
    'D6': ['GFP90', 'R0.5'],
    'E6': ['GFP90', 'R1'],
    'F6': ['GFP90', 'R2'],
    'G6': ['GFP90', 'R4'],
}

day_8_key = day_7_key

day_9_key = day_7_key

day_1_file = "../../wet_scripting/percent_day_1/cr_082824_pre.csv"
day_2_file = "../../wet_scripting/percent_day_2/cr_082924_pre.csv"
day_3_file = "../../wet_scripting/percent_day_3/cr_083024_pre.csv"
day_4_file = "../../wet_scripting/saturation_day_1/cr_090424_pre.csv"
day_5_file = "../../wet_scripting/saturation_day_2/cr_090524_pre.csv"
day_6_file = "../../wet_scripting/saturation_day_3/cr_090624_pre.csv"
day_7_file = "../../wet_scripting/percent_day_4/cr_091224_pre.csv"
day_8_file = "../../wet_scripting/percent_day_5/cr_091324_pre.csv"
day_9_file = "../../wet_scripting/percent_day_6/cr_091424_pre.csv"

files = [day_1_file,
    day_2_file,
    day_3_file,
    day_4_file,
    day_5_file,
    day_6_file,
    day_7_file,
    day_8_file,
    day_9_file]

keys = [day_1_key,
    day_2_key,
    day_3_key,
    day_4_key,
    day_5_key,
    day_6_key,
    day_7_key,
    day_8_key,
    day_9_key]


def parse_platereader(filename):
    """Parse the output of a Teccan plate reader and make the data tidy"""
    with open(filename, "r") as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    dataframe = pd.DataFrame(columns=["time", "well", "label", "value", "temperature"])
    datasets = []
    reading_dataset = [None, None]
    start_time = None
    for i, line in enumerate(lines):
        line = line.split(",")
        if line[0].startswith("End Time:"):
            continue
        elif line[0].startswith("Start Time:"):
            start_time = i
        elif start_time and any(line) > 0 and not any(reading_dataset):
            reading_dataset[0] = i
        elif start_time and any(line) == 0 and any(reading_dataset):
            reading_dataset[1] = i  # Exclusive
            datasets.append(reading_dataset)
            reading_dataset = [None, None]

    def filter_function(test_value):
        if test_value == "":
            return False
        else:
            return True

    for dataset in datasets:
        data = lines[dataset[0] : dataset[1]]
        label = data.pop(0).split(",")[0]

        if data[0].startswith("Cycle"):
            cycle = data.pop(0).split(",")[1:]

        times = list(filter(filter_function, data.pop(0).split(",")[1:]))
        temperature = list(filter(filter_function, data.pop(0).split(",")[1:]))
        data = list(filter(filter_function, [line.split(",") for line in data]))

        for line in data:
            well = str(line.pop(0))
            line = list(filter(filter_function, line))
            for i, value in enumerate(line):
                adding_frame = pd.DataFrame(
                    {
                        "time": round(float(times[i])),
                        "well": well,
                        "label": label,
                        "value": float(value),
                        "temperature": float(temperature[i]),
                    },
                    index=[0],
                )

                dataframe = pd.concat([dataframe, adding_frame])
    return dataframe

def associate_wells(dfs, keys):
    associated_dataframes = []
    for experiment, pairing in enumerate(zip(dfs, keys)):
        original_df = pairing[0]
        key_dict = pairing[1]
        key_df = pd.DataFrame.from_dict(key_dict, orient='index')
        merged_df = original_df.merge(key_df, left_on='well', right_index=True, how='left')
        merged_df['experiment'] = experiment+1
        merged_df.rename(columns={0: 'cds', 1: 'rbs'}, inplace=True)
        associated_dataframes.append(merged_df)
    return associated_dataframes

def simplify(dataframes):
    simplified_dfs = []
    for dataframe in dataframes:
        # Pivot table
        dataframe = dataframe.pivot(index=["well", "time", "rbs", "cds", "experiment"], columns="label", values="value").reset_index()

        # Grab blanks
        blank_df = dataframe[dataframe['rbs'] == 'blank']
        blank_df = blank_df[['time', 'OD660', 'mCherry', 'GFP']]
        blank_df = blank_df.groupby(by='time').mean()
        blank_df = blank_df.reset_index()
        # Subtract blanks from columns
        # Subtract the blank from the other data
        dataframe = dataframe[dataframe['rbs'] != 'blank']
        dataframe = pd.merge(dataframe, blank_df, on='time', suffixes=('', '_blank'))
        dataframe['OD660'] = dataframe['OD660'] - dataframe['OD660_blank']
        dataframe['mCherry'] = dataframe['mCherry'] - dataframe['mCherry_blank']
        dataframe['GFP'] = dataframe['GFP'] - dataframe['GFP_blank']
        dataframe = dataframe.drop(columns=['OD660_blank', 'mCherry_blank', 'GFP_blank'])

        # Drop the blank from the table
        dataframe = dataframe[dataframe.rbs != 'blank']
        simplified_dfs.append(dataframe)
    return simplified_dfs

dataframes = [parse_platereader(filename) for filename in files]
associated_dataframes = associate_wells(dataframes, keys)
simplified_dfs = simplify(associated_dataframes)

mega_df = pd.concat(simplified_dfs, axis=0, ignore_index=True)
print(mega_df.head())

mega_df.to_csv("../experimental_pre_induction.csv")
