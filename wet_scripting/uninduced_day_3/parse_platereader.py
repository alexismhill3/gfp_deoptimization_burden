import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'B4': ['C2', 'GFP50', 'R0.25', 21.09436023202934, 169.40563976797065], 'G5': ['D2', 'GFP50', 'R0.5', 20.91562474356396, 169.58437525643603], 'E4': ['E2', 'GFP50', 'R1', 21.699452883129634, 168.80054711687038], 'E6': ['F2', 'GFP50', 'R2', 19.17935827364275, 171.32064172635725], 'D2': ['G2', 'GFP50', 'R4', 17.973940700103235, 172.52605929989676], 'G4': ['C3', 'GAG', 'R0.25', 18.38253605679702, 172.11746394320298], 'C6': ['D3', 'GAG', 'R0.5', 21.57964457684586, 168.92035542315415], 'E5': ['E3', 'GAG', 'R1', 28.212947419013833, 162.28705258098617], 'E3': ['F3', 'GAG', 'R2', 18.425865829066158, 172.07413417093383], 'F6': ['G3', 'GAG', 'R4', 19.393482123407814, 171.1065178765922], 'E2': ['C4', 'GGA', 'R0.25', 21.80031660318569, 168.69968339681432], 'C3': ['D4', 'GGA', 'R0.5', 21.649371704712944, 168.85062829528707], 'F3': ['E4', 'GGA', 'R1', 25.210278184694918, 165.28972181530509], 'C4': ['F4', 'GGA', 'R2', 22.829634569334157, 167.67036543066584], 'F2': ['G4', 'GGA', 'R4', 18.346580427064936, 172.15341957293506], 'D4': ['C5', 'GGG', 'R0.25', 22.287208844353696, 168.2127911556463], 'B6': ['D5', 'GGG', 'R0.5', 22.686078958839367, 167.81392104116063], 'G2': ['E5', 'GGG', 'R1', 23.031428709547267, 167.46857129045273], 'B3': ['F5', 'GGG', 'R2', 17.465256270748995, 173.034743729251], 'C5': ['G5', 'GGG', 'R4', 18.23955889267839, 172.2604411073216], 'C2': ['C6', 'CTA', 'R0.25', 20.89698914989257, 169.60301085010744], 'D6': ['D6', 'CTA', 'R0.5', 23.658798394235912, 166.8412016057641], 'B2': ['E6', 'CTA', 'R1', 24.3845278750076, 166.1154721249924], 'G6': ['F6', 'CTA', 'R2', 22.297803246157013, 168.202196753843], 'F5': ['G6', 'CTA', 'R4', 21.649371704712944, 168.85062829528707], 'D10': ['C7', 'GFP50', 'R0.25', 20.44159574500168, 170.05840425499832], 'D9': ['D7', 'GFP50', 'R0.5', 20.887681028253617, 169.6123189717464], 'F7': ['E7', 'GFP50', 'R1', 22.098191728749395, 168.40180827125062], 'F8': ['F7', 'GFP50', 'R2', 19.35346967852408, 171.14653032147592], 'E10': ['G7', 'GFP50', 'R4', 17.419848359526107, 173.0801516404739], 'E7': ['C8', 'GAG', 'R0.25', 18.608632925941983, 171.89136707405802], 'F9': ['D8', 'GAG', 'R0.5', 22.05662181509914, 168.44337818490087], 'B9': ['E8', 'GAG', 'R1', 29.10586985044504, 161.39413014955497], 'F11': ['F8', 'GAG', 'R2', 19.645303952997907, 170.8546960470021], 'C7': ['G8', 'GAG', 'R4', 19.828020681423308, 170.6719793185767], 'D11': ['C9', 'GGA', 'R0.25', 22.46871645696829, 168.03128354303172], 'D7': ['D9', 'GGA', 'R0.5', 21.95337806987589, 168.5466219301241], 'G8': ['E9', 'GGA', 'R1', 26.195934655633035, 164.30406534436696], 'E8': ['F9', 'GGA', 'R2', 28.626219733983422, 161.87378026601658], 'E9': ['G9', 'GGA', 'R4', 20.30882532997183, 170.19117467002818], 'B7': ['C10', 'GGG', 'R0.25', 22.46871645696829, 168.03128354303172], 'C11': ['D10', 'GGG', 'R0.5', 21.729615363014965, 168.77038463698503], 'C10': ['E10', 'GGG', 'R1', 20.887681028253617, 169.6123189717464], 'B8': ['F10', 'GGG', 'R2', 18.48396050323487, 172.01603949676513], 'G9': ['G10', 'GGG', 'R4', 19.250206368690215, 171.24979363130979], 'F10': ['C11', 'CTA', 'R0.25', 20.513121083680975, 169.98687891631903], 'G7': ['D11', 'CTA', 'R0.5', 24.071649290168633, 166.42835070983136], 'C8': ['E11', 'CTA', 'R1', 23.551873982809823, 166.9481260171902], 'D8': ['F11', 'CTA', 'R2', 21.840925128567314, 168.6590748714327], 'E11': ['G11', 'CTA', 'R4', 21.500505648243674, 168.9994943517563], 'D3': ['blank', 'blank', 'blank', 0, 190.5], 'G3': ['blank', 'blank', 'blank', 0, 190.5], 'F4': ['blank', 'blank', 'blank', 0, 190.5], 'B5': ['blank', 'blank', 'blank', 0, 190.5], 'D5': ['blank', 'blank', 'blank', 0, 190.5], 'C9': ['blank', 'blank', 'blank', 0, 190.5], 'B10': ['blank', 'blank', 'blank', 0, 190.5], 'G10': ['blank', 'blank', 'blank', 0, 190.5], 'B11': ['blank', 'blank', 'blank', 0, 190.5], 'G11': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_092824_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('uninduced3clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
