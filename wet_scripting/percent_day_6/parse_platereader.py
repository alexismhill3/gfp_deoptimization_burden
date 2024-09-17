import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'F7': ['C2', 'GFP10', 'R0.25', 47.17481362999709, 143.3251863700029], 'B11': ['D2', 'GFP10', 'R0.5', 39.70639884673175, 150.79360115326824], 'C8': ['E2', 'GFP10', 'R1', 48.998329694314705, 141.5016703056853], 'E6': ['F2', 'GFP10', 'R2', 38.28044269286634, 152.21955730713367], 'C4': ['G2', 'GFP10', 'R4', 46.47364423808254, 144.02635576191744], 'C2': ['C3', 'GFP25', 'R0.25', 37.12888079141033, 153.37111920858968], 'F2': ['D3', 'GFP25', 'R0.5', 37.070187288317605, 153.4298127116824], 'E7': ['E3', 'GFP25', 'R1', 27.472584202806605, 163.02741579719338], 'E3': ['F3', 'GFP25', 'R2', 47.5574924582221, 142.9425075417779], 'D5': ['G3', 'GFP25', 'R4', 35.68802154117749, 154.81197845882252], 'F10': ['C4', 'GFP50', 'R0.25', 22.898739065417278, 167.6012609345827], 'F6': ['D4', 'GFP50', 'R0.5', 44.19638361264782, 146.30361638735218], 'G10': ['E4', 'GFP50', 'R1', 43.29874355833708, 147.2012564416629], 'E8': ['F4', 'GFP50', 'R2', 41.98102391059883, 148.51897608940118], 'D7': ['G4', 'GFP50', 'R4', 27.864305315195022, 162.63569468480497], 'D4': ['C5', 'GFP75', 'R0.25', 30.372489082688148, 160.12751091731184], 'F11': ['D5', 'GFP75', 'R0.5', 37.30607735943837, 153.19392264056162], 'G11': ['E5', 'GFP75', 'R1', 36.953355225353405, 153.5466447746466], 'C6': ['F5', 'GFP75', 'R2', 30.4513697553894, 160.0486302446106], 'C7': ['G5', 'GFP75', 'R4', 28.577383595834586, 161.9226164041654], 'D6': ['C6', 'GFP90', 'R0.25', 39.07781821531417, 151.42218178468585], 'B7': ['D6', 'GFP90', 'R0.5', 33.98145236440644, 156.51854763559356], 'B3': ['E6', 'GFP90', 'R1', 36.60724472385309, 153.89275527614691], 'B4': ['F6', 'GFP90', 'R2', 37.158292908772374, 153.34170709122762], 'F4': ['G6', 'GFP90', 'R4', 35.68802154117749, 154.81197845882252], 'B2': ['blank', 'blank', 'blank', 0, 190.5], 'B5': ['blank', 'blank', 'blank', 0, 190.5], 'B6': ['blank', 'blank', 'blank', 0, 190.5], 'B8': ['blank', 'blank', 'blank', 0, 190.5], 'B9': ['blank', 'blank', 'blank', 0, 190.5], 'B10': ['blank', 'blank', 'blank', 0, 190.5], 'C3': ['blank', 'blank', 'blank', 0, 190.5], 'C5': ['blank', 'blank', 'blank', 0, 190.5], 'C9': ['blank', 'blank', 'blank', 0, 190.5], 'C10': ['blank', 'blank', 'blank', 0, 190.5], 'C11': ['blank', 'blank', 'blank', 0, 190.5], 'D2': ['blank', 'blank', 'blank', 0, 190.5], 'D3': ['blank', 'blank', 'blank', 0, 190.5], 'D8': ['blank', 'blank', 'blank', 0, 190.5], 'D9': ['blank', 'blank', 'blank', 0, 190.5], 'D10': ['blank', 'blank', 'blank', 0, 190.5], 'D11': ['blank', 'blank', 'blank', 0, 190.5], 'E2': ['blank', 'blank', 'blank', 0, 190.5], 'E4': ['blank', 'blank', 'blank', 0, 190.5], 'E5': ['blank', 'blank', 'blank', 0, 190.5], 'E9': ['blank', 'blank', 'blank', 0, 190.5], 'E10': ['blank', 'blank', 'blank', 0, 190.5], 'E11': ['blank', 'blank', 'blank', 0, 190.5], 'F3': ['blank', 'blank', 'blank', 0, 190.5], 'F5': ['blank', 'blank', 'blank', 0, 190.5], 'F8': ['blank', 'blank', 'blank', 0, 190.5], 'F9': ['blank', 'blank', 'blank', 0, 190.5], 'G2': ['blank', 'blank', 'blank', 0, 190.5], 'G3': ['blank', 'blank', 'blank', 0, 190.5], 'G4': ['blank', 'blank', 'blank', 0, 190.5], 'G5': ['blank', 'blank', 'blank', 0, 190.5], 'G6': ['blank', 'blank', 'blank', 0, 190.5], 'G7': ['blank', 'blank', 'blank', 0, 190.5], 'G8': ['blank', 'blank', 'blank', 0, 190.5], 'G9': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_091424_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('per6clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
