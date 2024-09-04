import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'B10': ['C2', 'GFP10', 'R0.25', 29.265693233885802, 161.2343067661142], 'C7': ['D2', 'GFP10', 'R0.5', 32.28775999357144, 158.21224000642854], 'F2': ['E2', 'GFP10', 'R1', 29.102258550270943, 161.39774144972907], 'F3': ['F2', 'GFP10', 'R2', 38.42471098813522, 152.07528901186478], 'F8': ['G2', 'GFP10', 'R4', 24.344026099267424, 166.1559739007326], 'G11': ['C3', 'GFP25', 'R0.25', 34.881155419596425, 155.61884458040356], 'C8': ['D3', 'GFP25', 'R0.5', 33.800232133563995, 156.699767866436], 'G3': ['E3', 'GFP25', 'R1', 33.319977783515945, 157.18002221648405], 'E4': ['F3', 'GFP25', 'R2', 43.97262257780853, 146.52737742219148], 'E3': ['G3', 'GFP25', 'R4', 32.556713820666666, 157.94328617933334], 'C6': ['C4', 'GFP50', 'R0.25', 39.963529640784934, 150.53647035921506], 'D7': ['D4', 'GFP50', 'R0.5', 43.083963321661564, 147.41603667833843], 'B3': ['E4', 'GFP50', 'R1', 47.73173522747044, 142.76826477252956], 'D2': ['F4', 'GFP50', 'R2', 27.163908071537886, 163.3360919284621], 'D8': ['G4', 'GFP50', 'R4', 30.286194357714564, 160.21380564228542], 'E6': ['C5', 'GFP75', 'R0.25', 26.062012950958508, 164.43798704904148], 'F6': ['D5', 'GFP75', 'R0.5', 19.859925188844983, 170.64007481115502], 'C4': ['E5', 'GFP75', 'R1', 24.281011722987746, 166.21898827701224], 'D3': ['F5', 'GFP75', 'R2', 29.43097394247606, 161.06902605752393], 'F5': ['G5', 'GFP75', 'R4', 21.293563356171234, 169.20643664382877], 'F9': ['C6', 'GFP90', 'R0.25', 32.08894366346964, 158.41105633653035], 'C11': ['D6', 'GFP90', 'R0.5', 28.57041797321417, 161.92958202678582], 'B9': ['E6', 'GFP90', 'R1', 31.849245466190073, 158.65075453380993], 'G5': ['F6', 'GFP90', 'R2', 30.864176064393018, 159.635823935607], 'E7': ['G6', 'GFP90', 'R4', 29.729462010300022, 160.7705379897], 'G9': ['C7', 'MCH10', 'R0.25', 29.449454083441474, 161.05054591655852], 'F4': ['D7', 'MCH10', 'R0.5', 30.014848591514337, 160.48515140848565], 'F10': ['E7', 'MCH10', 'R1', 22.423599868222016, 168.07640013177797], 'E11': ['F7', 'MCH10', 'R2', 25.453814706578097, 165.0461852934219], 'G2': ['G7', 'MCH10', 'R4', 22.232272147938676, 168.2677278520613], 'D10': ['C8', 'MCH25', 'R0.25', 19.952863126408122, 170.54713687359188], 'D11': ['D8', 'MCH25', 'R0.5', 20.93242953460398, 169.56757046539602], 'E10': ['E8', 'MCH25', 'R1', 22.70584719337278, 167.7941528066272], 'B7': ['F8', 'MCH25', 'R2', 18.77099086993087, 171.72900913006913], 'C9': ['G8', 'MCH25', 'R4', 21.83889004885966, 168.66110995114033], 'E5': ['C9', 'MCH50', 'R0.25', 30.864176064393018, 159.635823935607], 'G4': ['D9', 'MCH50', 'R0.5', 42.730687234932915, 147.76931276506707], 'C3': ['E9', 'MCH50', 'R1', 25.059413279995347, 165.44058672000466], 'E9': ['F9', 'MCH50', 'R2', 23.09721328014618, 167.40278671985382], 'D9': ['G9', 'MCH50', 'R4', 24.781359075873834, 165.71864092412616], 'C5': ['C10', 'MCH75', 'R0.25', 24.08153772859744, 166.41846227140257], 'D5': ['D10', 'MCH75', 'R0.5', 47.394095995482374, 143.10590400451764], 'G10': ['E10', 'MCH75', 'R1', 21.459187065901332, 169.04081293409865], 'G7': ['F10', 'MCH75', 'R2', 19.569891647312108, 170.93010835268788], 'D6': ['G10', 'MCH75', 'R4', 21.06404398623117, 169.43595601376882], 'B11': ['C11', 'MCH90', 'R0.25', 27.46615148321775, 163.03384851678226], 'D4': ['D11', 'MCH90', 'R0.5', 40.6563800332011, 149.84361996679888], 'E2': ['E11', 'MCH90', 'R1', 22.716846716682245, 167.78315328331774], 'C10': ['F11', 'MCH90', 'R2', 23.292211754035453, 167.20778824596454], 'B5': ['G11', 'MCH90', 'R4', 28.243527464786116, 162.25647253521387], 'B2': ['blank', 'blank', 'blank', 0, 190.5], 'B4': ['blank', 'blank', 'blank', 0, 190.5], 'B6': ['blank', 'blank', 'blank', 0, 190.5], 'B8': ['blank', 'blank', 'blank', 0, 190.5], 'C2': ['blank', 'blank', 'blank', 0, 190.5], 'E8': ['blank', 'blank', 'blank', 0, 190.5], 'F7': ['blank', 'blank', 'blank', 0, 190.5], 'F11': ['blank', 'blank', 'blank', 0, 190.5], 'G6': ['blank', 'blank', 'blank', 0, 190.5], 'G8': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_083024_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('per3clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
