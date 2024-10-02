import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'C5': ['C2', 'GFP10', 'R0.25', 21.560795748136297, 168.9392042518637], 'G8': ['D2', 'GFP10', 'R0.5', 17.31118836608703, 173.18881163391296], 'G5': ['E2', 'GFP10', 'R1', 23.913322789418682, 166.5866772105813], 'F8': ['F2', 'GFP10', 'R2', 20.478190126312423, 170.02180987368757], 'F2': ['G2', 'GFP10', 'R4', 20.292130279312843, 170.20786972068714], 'F3': ['C3', 'GFP25', 'R0.25', 17.279298013507784, 173.2207019864922], 'E3': ['D3', 'GFP25', 'R0.5', 19.474816522059754, 171.02518347794023], 'E9': ['E3', 'GFP25', 'R1', 18.638953962748037, 171.86104603725195], 'C9': ['F3', 'GFP25', 'R2', 23.671932078720214, 166.8280679212798], 'E5': ['G3', 'GFP25', 'R4', 16.559404062124, 173.940595937876], 'F5': ['C4', 'GFP50', 'R0.25', 17.616796877538818, 172.88320312246117], 'G10': ['D4', 'GFP50', 'R0.5', 18.233176098097736, 172.26682390190226], 'C7': ['E4', 'GFP50', 'R1', 25.036673236711888, 165.4633267632881], 'E2': ['F4', 'GFP50', 'R2', 24.577479287862943, 165.92252071213704], 'B4': ['G4', 'GFP50', 'R4', 18.477405540415074, 172.02259445958492], 'B8': ['C5', 'GFP75', 'R0.25', 18.76573538967418, 171.73426461032582], 'C11': ['D5', 'GFP75', 'R0.5', 18.325792276582515, 172.17420772341748], 'G4': ['E5', 'GFP75', 'R1', 17.65659003749864, 172.84340996250137], 'E11': ['F5', 'GFP75', 'R2', 17.663238723918987, 172.836761276081], 'D3': ['G5', 'GFP75', 'R4', 16.380120438187678, 174.11987956181233], 'B10': ['C6', 'GFP90', 'R0.25', 16.06590552770781, 174.4340944722922], 'C8': ['D6', 'GFP90', 'R0.5', 17.260221652028388, 173.23977834797162], 'D11': ['E6', 'GFP90', 'R1', 18.01605557954129, 172.4839444204587], 'G3': ['F6', 'GFP90', 'R2', 18.254467178987547, 172.24553282101246], 'C3': ['G6', 'GFP90', 'R4', 16.351567097328047, 174.14843290267194], 'D2': ['C7', 'MCH10', 'R0.25', 28.316849905931395, 162.1831500940686], 'G7': ['D7', 'MCH10', 'R0.5', 24.487650582587335, 166.01234941741268], 'C6': ['E7', 'MCH10', 'R1', 21.964689154932184, 168.5353108450678], 'E7': ['F7', 'MCH10', 'R2', 24.34781888993494, 166.15218111006507], 'D10': ['G7', 'MCH10', 'R4', 25.779805688928054, 164.72019431107194], 'E4': ['C8', 'MCH25', 'R0.25', 16.718782409643612, 173.7812175903564], 'B3': ['D8', 'MCH25', 'R0.5', 17.689887594039167, 172.81011240596084], 'E10': ['E8', 'MCH25', 'R1', 19.728768843520225, 170.7712311564798], 'G11': ['F8', 'MCH25', 'R2', 21.06688352925484, 169.43311647074515], 'F9': ['G8', 'MCH25', 'R4', 18.462857874802886, 172.0371421251971], 'E8': ['C9', 'MCH50', 'R0.25', 14.701187551642303, 175.7988124483577], 'B2': ['D9', 'MCH50', 'R0.5', 15.026175149236831, 175.47382485076318], 'F4': ['E9', 'MCH50', 'R1', 17.381758187495784, 173.1182418125042], 'D8': ['F9', 'MCH50', 'R2', 16.323113129919943, 174.17688687008007], 'D6': ['G9', 'MCH50', 'R4', 14.632390565043545, 175.86760943495645], 'D5': ['C10', 'MCH75', 'R0.25', 15.864831010266537, 174.63516898973347], 'B7': ['D10', 'MCH75', 'R0.5', 13.965756668053631, 176.53424333194636], 'E6': ['E10', 'MCH75', 'R1', 17.912844580036403, 172.5871554199636], 'B5': ['F10', 'MCH75', 'R2', 15.538946470807463, 174.96105352919253], 'G2': ['G10', 'MCH75', 'R4', 13.62891922604114, 176.87108077395885], 'F10': ['C11', 'MCH90', 'R0.25', 12.58991202337768, 177.91008797662232], 'C4': ['D11', 'MCH90', 'R0.5', 16.28344320064099, 174.216556799359], 'D7': ['E11', 'MCH90', 'R1', 13.805434251608764, 176.69456574839123], 'D4': ['F11', 'MCH90', 'R2', 13.056036368061545, 177.44396363193846], 'G6': ['G11', 'MCH90', 'R4', 12.654453617151365, 177.84554638284862], 'B6': ['blank', 'blank', 'blank', 0, 190.5], 'B9': ['blank', 'blank', 'blank', 0, 190.5], 'B11': ['blank', 'blank', 'blank', 0, 190.5], 'C2': ['blank', 'blank', 'blank', 0, 190.5], 'C10': ['blank', 'blank', 'blank', 0, 190.5], 'D9': ['blank', 'blank', 'blank', 0, 190.5], 'F6': ['blank', 'blank', 'blank', 0, 190.5], 'F7': ['blank', 'blank', 'blank', 0, 190.5], 'F11': ['blank', 'blank', 'blank', 0, 190.5], 'G9': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_092424_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('LT2clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
