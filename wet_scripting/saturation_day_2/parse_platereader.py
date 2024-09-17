import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'B9': ['C2', 'GFP50', 'R0.25', 35.97821422153068, 154.52178577846934], 'G7': ['D2', 'GFP50', 'R0.5', 44.30493006211805, 146.19506993788195], 'C8': ['E2', 'GFP50', 'R1', 31.254963538150903, 159.2450364618491], 'D7': ['F2', 'GFP50', 'R2', 38.39325627573057, 152.10674372426942], 'E3': ['G2', 'GFP50', 'R4', 35.73152517104582, 154.7684748289542], 'E11': ['C3', 'GGG', 'R0.25', 27.274484218505503, 163.2255157814945], 'G8': ['D3', 'GGG', 'R0.5', 23.269099511759265, 167.23090048824074], 'E9': ['E3', 'GGG', 'R1', 40.656380295782, 149.84361970421799], 'D2': ['F3', 'GGG', 'R2', 36.56728688700437, 153.93271311299563], 'D5': ['G3', 'GGG', 'R4', 34.344756762897404, 156.15524323710258], 'B6': ['C4', 'GAG', 'R0.25', 30.443463844268443, 160.05653615573155], 'D3': ['D4', 'GAG', 'R0.5', 26.563886571724133, 163.93611342827586], 'D10': ['E4', 'GAG', 'R1', 31.806047765634915, 158.6939522343651], 'G2': ['F4', 'GAG', 'R2', 41.33721248906455, 149.16278751093546], 'E4': ['G4', 'GAG', 'R4', 30.502862869594967, 159.99713713040504], 'F10': ['C5', 'GGA', 'R0.25', 27.627943522151995, 162.872056477848], 'E5': ['D5', 'GGA', 'R0.5', 39.39291038704897, 151.10708961295103], 'E7': ['E5', 'GGA', 'R1', 35.92309960394024, 154.57690039605976], 'C2': ['F5', 'GGA', 'R2', 32.99183881838078, 157.50816118161922], 'G6': ['G5', 'GGA', 'R4', 39.5590439028979, 150.94095609710212], 'E2': ['C6', 'CTA', 'R0.25', 35.92309960394024, 154.57690039605976], 'D9': ['D6', 'CTA', 'R0.5', 40.37637814720547, 150.12362185279454], 'G5': ['E6', 'CTA', 'R1', 39.5590439028979, 150.94095609710212], 'G11': ['F6', 'CTA', 'R2', 38.55104339343743, 151.94895660656258], 'B5': ['G6', 'CTA', 'R4', 26.699987595685553, 163.80001240431446], 'B2': ['blank', 'blank', 'blank', 0, 190.5], 'B3': ['blank', 'blank', 'blank', 0, 190.5], 'B4': ['blank', 'blank', 'blank', 0, 190.5], 'B7': ['blank', 'blank', 'blank', 0, 190.5], 'B8': ['blank', 'blank', 'blank', 0, 190.5], 'B10': ['blank', 'blank', 'blank', 0, 190.5], 'B11': ['blank', 'blank', 'blank', 0, 190.5], 'C3': ['blank', 'blank', 'blank', 0, 190.5], 'C4': ['blank', 'blank', 'blank', 0, 190.5], 'C5': ['blank', 'blank', 'blank', 0, 190.5], 'C6': ['blank', 'blank', 'blank', 0, 190.5], 'C7': ['blank', 'blank', 'blank', 0, 190.5], 'C9': ['blank', 'blank', 'blank', 0, 190.5], 'C10': ['blank', 'blank', 'blank', 0, 190.5], 'C11': ['blank', 'blank', 'blank', 0, 190.5], 'D4': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'D8': ['blank', 'blank', 'blank', 0, 190.5], 'D11': ['blank', 'blank', 'blank', 0, 190.5], 'E6': ['blank', 'blank', 'blank', 0, 190.5], 'E8': ['blank', 'blank', 'blank', 0, 190.5], 'E10': ['blank', 'blank', 'blank', 0, 190.5], 'F2': ['blank', 'blank', 'blank', 0, 190.5], 'F3': ['blank', 'blank', 'blank', 0, 190.5], 'F4': ['blank', 'blank', 'blank', 0, 190.5], 'F5': ['blank', 'blank', 'blank', 0, 190.5], 'F6': ['blank', 'blank', 'blank', 0, 190.5], 'F7': ['blank', 'blank', 'blank', 0, 190.5], 'F8': ['blank', 'blank', 'blank', 0, 190.5], 'F9': ['blank', 'blank', 'blank', 0, 190.5], 'F11': ['blank', 'blank', 'blank', 0, 190.5], 'G3': ['blank', 'blank', 'blank', 0, 190.5], 'G4': ['blank', 'blank', 'blank', 0, 190.5], 'G9': ['blank', 'blank', 'blank', 0, 190.5], 'G10': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_090524_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('sat2clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
