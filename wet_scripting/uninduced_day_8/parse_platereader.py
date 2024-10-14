import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'C2': ['C2', 'MCH10', 'R0.25', 27.860996999415473, 162.63900300058452], 'D5': ['D2', 'MCH10', 'R0.5', 17.445766416606087, 173.0542335833939], 'C5': ['E2', 'MCH10', 'R1', 18.239557888551968, 172.26044211144804], 'G4': ['F2', 'MCH10', 'R2', 16.92328693077799, 173.57671306922202], 'F2': ['G2', 'MCH10', 'R4', 17.76291556254009, 172.7370844374599], 'B2': ['C3', 'MCH25', 'R0.25', 14.301762036746293, 176.19823796325372], 'G6': ['D3', 'MCH25', 'R0.5', 14.925279915715873, 175.57472008428414], 'E6': ['E3', 'MCH25', 'R1', 16.288532923322464, 174.21146707667754], 'C3': ['F3', 'MCH25', 'R2', 17.95329967994791, 172.54670032005208], 'G5': ['G3', 'MCH25', 'R4', 14.939541995057052, 175.56045800494294], 'E2': ['C4', 'MCH50', 'R0.25', 13.944579715030098, 176.5554202849699], 'B5': ['D4', 'MCH50', 'R0.5', 14.44269320900728, 176.05730679099273], 'F5': ['E4', 'MCH50', 'R1', 15.395615044749775, 175.10438495525023], 'B4': ['F4', 'MCH50', 'R2', 16.165023948462036, 174.33497605153798], 'C6': ['G4', 'MCH50', 'R4', 14.491780420711079, 176.00821957928892], 'B6': ['C5', 'MCH75', 'R0.25', 13.526330912272686, 176.9736690877273], 'D4': ['D5', 'MCH75', 'R0.5', 13.53023252308804, 176.96976747691195], 'D3': ['E5', 'MCH75', 'R1', 15.52300301716614, 174.97699698283387], 'D2': ['F5', 'MCH75', 'R2', 14.411626741517267, 176.08837325848273], 'F6': ['G5', 'MCH75', 'R4', 12.569330502485968, 177.93066949751403], 'F4': ['C6', 'MCH90', 'R0.25', 15.107975877959396, 175.3920241220406], 'G3': ['D6', 'MCH90', 'R0.5', 13.095772032384808, 177.40422796761518], 'E5': ['E6', 'MCH90', 'R1', 13.139799579491168, 177.36020042050882], 'C4': ['F6', 'MCH90', 'R2', 13.239950529678563, 177.26004947032143], 'G2': ['G6', 'MCH90', 'R4', 13.004990650235673, 177.49500934976433], 'D11': ['C7', 'MCH10', 'R0.25', 29.47165746064017, 161.02834253935984], 'C8': ['D7', 'MCH10', 'R0.5', 16.076369684775496, 174.4236303152245], 'E7': ['E7', 'MCH10', 'R1', 16.97228041211798, 173.52771958788202], 'G7': ['F7', 'MCH10', 'R2', 17.33614297525623, 173.16385702474378], 'F8': ['G7', 'MCH10', 'R4', 16.564667788922602, 173.9353322110774], 'E11': ['C8', 'MCH25', 'R0.25', 14.788799571787784, 175.7112004282122], 'D7': ['D8', 'MCH25', 'R0.5', 14.659373870265213, 175.8406261297348], 'F11': ['E8', 'MCH25', 'R1', 15.736545608397146, 174.76345439160286], 'B7': ['F8', 'MCH25', 'R2', 18.476678697312593, 172.0233213026874], 'C10': ['G8', 'MCH25', 'R4', 14.953832778089456, 175.54616722191054], 'G11': ['C9', 'MCH50', 'R0.25', 13.796905111353306, 176.7030948886467], 'G10': ['D9', 'MCH50', 'R0.5', 14.189266245592014, 176.31073375440798], 'B10': ['E9', 'MCH50', 'R1', 14.64106879197645, 175.85893120802356], 'C7': ['F9', 'MCH50', 'R2', 16.01051330045207, 174.48948669954794], 'G9': ['G9', 'MCH50', 'R4', 13.92801522573821, 176.57198477426178], 'C9': ['C10', 'MCH75', 'R0.25', 12.802642165458172, 177.69735783454183], 'D9': ['D10', 'MCH75', 'R0.5', 17.878020667302565, 172.62197933269744], 'B9': ['E10', 'MCH75', 'R1', 15.19116340541395, 175.30883659458604], 'E8': ['F10', 'MCH75', 'R2', 14.849670723387028, 175.65032927661298], 'F10': ['G10', 'MCH75', 'R4', 13.3873379084534, 177.1126620915466], 'C11': ['C11', 'MCH90', 'R0.25', 14.518697258782343, 175.98130274121766], 'E10': ['D11', 'MCH90', 'R0.5', 12.311964682382639, 178.18803531761736], 'B11': ['E11', 'MCH90', 'R1', 12.760842499341459, 177.73915750065854], 'D10': ['F11', 'MCH90', 'R2', 12.225314917862475, 178.27468508213752], 'F7': ['G11', 'MCH90', 'R4', 12.539086674022748, 177.96091332597726], 'B3': ['blank', 'blank', 'blank', 0, 190.5], 'E3': ['blank', 'blank', 'blank', 0, 190.5], 'F3': ['blank', 'blank', 'blank', 0, 190.5], 'E4': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'B8': ['blank', 'blank', 'blank', 0, 190.5], 'D8': ['blank', 'blank', 'blank', 0, 190.5], 'G8': ['blank', 'blank', 'blank', 0, 190.5], 'E9': ['blank', 'blank', 'blank', 0, 190.5], 'F9': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_100324_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('uninduced8clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
