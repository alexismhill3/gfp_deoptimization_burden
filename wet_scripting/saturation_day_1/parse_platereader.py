import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'C4': ['C2', 'GFP50', 'R0.25', 33.74187193601469, 156.7581280639853], 'D8': ['D2', 'GFP50', 'R0.5', 40.0864977074027, 150.4135022925973], 'C11': ['E2', 'GFP50', 'R1', 44.080077840040516, 146.41992215995947], 'D5': ['F2', 'GFP50', 'R2', 35.34378119424359, 155.1562188057564], 'B6': ['G2', 'GFP50', 'R4', 38.44360518628316, 152.05639481371685], 'C3': ['C3', 'GGG', 'R0.25', 21.753802404935364, 168.74619759506464], 'B3': ['D3', 'GGG', 'R0.5', 39.780493780481216, 150.7195062195188], 'F11': ['E3', 'GGG', 'R1', 46.80758812147772, 143.69241187852228], 'D2': ['F3', 'GGG', 'R2', 45.40290384302102, 145.09709615697898], 'B8': ['G3', 'GGG', 'R4', 32.12411104477278, 158.37588895522723], 'C2': ['C4', 'GGA', 'R0.25', 33.91265435011298, 156.58734564988703], 'F8': ['D4', 'GGA', 'R0.5', 42.989186362505606, 147.51081363749438], 'F7': ['E4', 'GGA', 'R1', 45.66815725527987, 144.83184274472012], 'G2': ['F4', 'GGA', 'R2', 41.579078888622064, 148.92092111137794], 'G9': ['G4', 'GGA', 'R4', 36.02242865472833, 154.47757134527166], 'C7': ['C5', 'GAG', 'R0.25', 37.94595419116421, 152.55404580883578], 'F9': ['D5', 'GAG', 'R0.5', 40.53690508498589, 149.9630949150141], 'C10': ['E5', 'GAG', 'R1', 35.211111051237, 155.288888948763], 'B10': ['F5', 'GAG', 'R2', 30.69450177726875, 159.80549822273125], 'E6': ['G5', 'GAG', 'R4', 32.775121399286306, 157.72487860071368], 'D9': ['C6', 'CTA', 'R0.25', 29.949681861973833, 160.55031813802617], 'G5': ['D6', 'CTA', 'R0.5', 38.317975039224784, 152.1820249607752], 'F3': ['E6', 'CTA', 'R1', 40.25854054596106, 150.24145945403893], 'C8': ['F6', 'CTA', 'R2', 37.85407381713513, 152.64592618286486], 'B9': ['G6', 'CTA', 'R4', 21.357560407786128, 169.14243959221386], 'B2': ['blank', 'blank', 'blank', 0, 190.5], 'B4': ['blank', 'blank', 'blank', 0, 190.5], 'B5': ['blank', 'blank', 'blank', 0, 190.5], 'B7': ['blank', 'blank', 'blank', 0, 190.5], 'B11': ['blank', 'blank', 'blank', 0, 190.5], 'C5': ['blank', 'blank', 'blank', 0, 190.5], 'C6': ['blank', 'blank', 'blank', 0, 190.5], 'C9': ['blank', 'blank', 'blank', 0, 190.5], 'D3': ['blank', 'blank', 'blank', 0, 190.5], 'D4': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'D7': ['blank', 'blank', 'blank', 0, 190.5], 'D10': ['blank', 'blank', 'blank', 0, 190.5], 'D11': ['blank', 'blank', 'blank', 0, 190.5], 'E2': ['blank', 'blank', 'blank', 0, 190.5], 'E3': ['blank', 'blank', 'blank', 0, 190.5], 'E4': ['blank', 'blank', 'blank', 0, 190.5], 'E5': ['blank', 'blank', 'blank', 0, 190.5], 'E7': ['blank', 'blank', 'blank', 0, 190.5], 'E8': ['blank', 'blank', 'blank', 0, 190.5], 'E9': ['blank', 'blank', 'blank', 0, 190.5], 'E10': ['blank', 'blank', 'blank', 0, 190.5], 'E11': ['blank', 'blank', 'blank', 0, 190.5], 'F2': ['blank', 'blank', 'blank', 0, 190.5], 'F4': ['blank', 'blank', 'blank', 0, 190.5], 'F5': ['blank', 'blank', 'blank', 0, 190.5], 'F6': ['blank', 'blank', 'blank', 0, 190.5], 'F10': ['blank', 'blank', 'blank', 0, 190.5], 'G3': ['blank', 'blank', 'blank', 0, 190.5], 'G4': ['blank', 'blank', 'blank', 0, 190.5], 'G6': ['blank', 'blank', 'blank', 0, 190.5], 'G7': ['blank', 'blank', 'blank', 0, 190.5], 'G8': ['blank', 'blank', 'blank', 0, 190.5], 'G10': ['blank', 'blank', 'blank', 0, 190.5], 'G11': ['blank', 'blank', 'blank', 0, 190.5]}


for well, data in well_encoding.items():
    if isinstance(data[2], float):
        data[2] = data[2]/4
    well_encoding[well] = [str(data[1]), str(data[2])]
    print(well_encoding[well])



def is_empty(row):
    if not any(row):
        return True
    else:
        return False

def parse_platereader(filename, categories):
    wb =  xl.load_workbook(filename)
    ws = wb.active
    in_data = False
    dataframes = []
    timepoints = []
    temperature = []
    start_time = None
    for row in ws.rows:
        row_values = [cell.value for cell in row]

        if row_values[0] == 'Start Time':
            start_time = row_values[1]
            continue

        if row_values[0] in categories:
            in_data = row_values[0]
            df = pd.DataFrame(columns=['time', 'well', 'iptg', 'rbs' 'temp',  'fluor', 'strain', in_data])
            continue

        if in_data and is_empty(row_values):
            in_data = False
            # Save the data
            dataframes.append(df)
            continue

        if in_data:
            well = row_values[0]
            if well == 'Cycle Nr.':
                continue
            elif well == 'Time [s]':
                timepoints = row_values[1:]
                # Round timepoints to nearest second
                timepoints = [round(timepoint) for timepoint in timepoints if timepoint is not None]
                continue
            elif well == 'Temp. [°C]':
                temperature = row_values[1:]
                temperature = [temp for temp in temperature if temp is not None]
                continue
            if well_encoding.get(well):
                values = row_values[1:]
                values = [value for value in values if value is not None]
                #print(len(timepoints), len(values), len(temperature))
                if 'blank' in well_encoding[well][0]:
                    fluor = 'blank'
                elif 'G' in well_encoding[well][0]:
                    fluor = 'GFP'
                elif 'M' in well_encoding[well][0]:
                    fluor = 'mCherry'
                else:
                    fluor = 'unknown'
                temp_dataframe = pd.DataFrame({'time': timepoints, 'well': well, 'iptg':'0.01875', 'rbs':well_encoding[well][1], 'temp': temperature, 'fluor':fluor, 'strain': well_encoding[well][0], in_data: values})
                df = pd.concat([df, temp_dataframe], ignore_index=True)
                continue

        continue

    merged_dataframe = pd.concat(dataframes, axis=1)
    merged_dataframe = merged_dataframe.replace('OVER', float('inf'))
    merged_dataframe = merged_dataframe.groupby(by=merged_dataframe.columns, axis=1).apply(lambda g: g.mean(axis=1) if isinstance(g.iloc[0,0], numbers.Number) else g.iloc[:,0]) # https://stackoverflow.com/questions/40311987/pandas-mean-of-columns-with-the-same-names

    # Fix order
    merged_dataframe = merged_dataframe[['time', 'well', 'iptg', 'strain', 'rbs', 'temp', 'OD660', 'fluor', 'mCherry', 'GFP']]


    # Find the average of the blanks at each timepoint
    blank_df = merged_dataframe[merged_dataframe['rbs'] == 'blank']
    blank_df = blank_df[['time', 'OD660', 'mCherry', 'GFP']]
    blank_df = blank_df.groupby(by='time').mean()
    blank_df = blank_df.reset_index()
    print(blank_df.head())

    # Subtract the blank from the other data
    merged_dataframe = merged_dataframe[merged_dataframe['rbs'] != 'blank']
    merged_dataframe = pd.merge(merged_dataframe, blank_df, on='time', suffixes=('', '_blank'))
    merged_dataframe['OD660'] = merged_dataframe['OD660'] - merged_dataframe['OD660_blank']
    merged_dataframe['mCherry'] = merged_dataframe['mCherry'] - merged_dataframe['mCherry_blank']
    merged_dataframe['GFP'] = merged_dataframe['GFP'] - merged_dataframe['GFP_blank']
    merged_dataframe = merged_dataframe.drop(columns=['OD660_blank', 'mCherry_blank', 'GFP_blank'])

    # Drop the blank from the table
    merged_dataframe = merged_dataframe[merged_dataframe.rbs != 'blank']


    #print(merged_dataframe.head())
    return merged_dataframe, start_time


def main():
    file = "cr_090424_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('sat1clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
