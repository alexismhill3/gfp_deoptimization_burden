import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'F3': ['C2', 'GFP50', 'R0.25', 14.621897663935487, 175.8781023360645], 'E2': ['D2', 'GFP50', 'R0.5', 18.555626726630983, 171.94437327336902], 'E5': ['E2', 'GFP50', 'R1', 17.761570270277886, 172.7384297297221], 'F2': ['F2', 'GFP50', 'R2', 19.82634322856933, 170.67365677143067], 'B3': ['G2', 'GFP50', 'R4', 14.603686000536465, 175.89631399946353], 'F6': ['C3', 'GAG', 'R0.25', 18.45341427815058, 172.04658572184942], 'E4': ['D3', 'GAG', 'R0.5', 19.859925000877546, 170.64007499912245], 'D5': ['E3', 'GAG', 'R1', 16.505207549378056, 173.99479245062196], 'F4': ['F3', 'GAG', 'R2', 19.902061274100294, 170.5979387258997], 'C6': ['G3', 'GAG', 'R4', 16.940403444705485, 173.55959655529452], 'G3': ['C4', 'GGA', 'R0.25', 14.886433620150964, 175.61356637984903], 'D2': ['D4', 'GGA', 'R0.5', 21.01684944530203, 169.48315055469797], 'B4': ['E4', 'GGA', 'R1', 20.747235378349544, 169.75276462165044], 'G2': ['F4', 'GGA', 'R2', 26.97641640870943, 163.52358359129056], 'B2': ['G4', 'GGA', 'R4', 17.741412811419032, 172.75858718858098], 'D4': ['C5', 'GGG', 'R0.25', 17.707921184867722, 172.79207881513227], 'F5': ['D5', 'GGG', 'R0.5', 16.202998748468232, 174.29700125153175], 'G6': ['E5', 'GGG', 'R1', 24.547890438958515, 165.95210956104148], 'B6': ['F5', 'GGG', 'R2', 19.264438078410702, 171.2355619215893], 'G5': ['G5', 'GGG', 'R4', 17.354103345549927, 173.14589665445007], 'C3': ['C6', 'CTA', 'R0.25', 18.352323862076737, 172.14767613792327], 'B5': ['D6', 'CTA', 'R0.5', 25.412440890883087, 165.0875591091169], 'D3': ['E6', 'CTA', 'R1', 25.032662516049925, 165.46733748395008], 'C2': ['F6', 'CTA', 'R2', 22.137827220314364, 168.36217277968564], 'C5': ['G6', 'CTA', 'R4', 15.339220719624647, 175.16077928037535], 'D11': ['C7', 'GFP50', 'R0.25', 16.545968458671815, 173.9540315413282], 'B7': ['D7', 'GFP50', 'R0.5', 18.644140704072292, 171.8558592959277], 'B10': ['E7', 'GFP50', 'R1', 17.842654178576506, 172.6573458214235], 'F8': ['F7', 'GFP50', 'R2', 20.0638265923785, 170.4361734076215], 'F9': ['G7', 'GFP50', 'R4', 15.993043517710165, 174.50695648228984], 'B9': ['C8', 'GAG', 'R0.25', 19.264438078410702, 171.2355619215893], 'B11': ['D8', 'GAG', 'R0.5', 20.430910141315163, 170.06908985868483], 'C8': ['E8', 'GAG', 'R1', 17.562045511662518, 172.93795448833748], 'G11': ['F8', 'GAG', 'R2', 24.281011442016972, 166.21898855798304], 'G10': ['G8', 'GAG', 'R4', 17.33486154819291, 173.16513845180708], 'D8': ['C9', 'GGA', 'R0.25', 15.693367658871935, 174.80663234112808], 'C7': ['D9', 'GGA', 'R0.5', 20.236970086109295, 170.2630299138907], 'F11': ['E9', 'GGA', 'R1', 21.216501986481937, 169.28349801351806], 'D10': ['F9', 'GGA', 'R2', 28.657702342556888, 161.8422976574431], 'D9': ['G9', 'GGA', 'R4', 19.537282578730437, 170.96271742126956], 'E10': ['C10', 'GGG', 'R0.25', 18.202748015877653, 172.29725198412234], 'G8': ['D10', 'GGG', 'R0.5', 16.60454579867784, 173.89545420132217], 'G7': ['E10', 'GGG', 'R1', 25.18049898308185, 165.31950101691814], 'F7': ['F10', 'GGG', 'R2', 18.65155408086203, 171.84844591913796], 'D7': ['G10', 'GGG', 'R4', 17.667896577888893, 172.83210342211112], 'C9': ['C11', 'CTA', 'R0.25', 19.099691597263448, 171.40030840273656], 'E7': ['D11', 'CTA', 'R0.5', 24.193336652005872, 166.30666334799412], 'B8': ['E11', 'CTA', 'R1', 25.18049898308185, 165.31950101691814], 'C11': ['F11', 'CTA', 'R2', 20.14137297672495, 170.35862702327506], 'E11': ['G11', 'CTA', 'R4', 15.274278701790985, 175.225721298209], 'E3': ['blank', 'blank', 'blank', 0, 190.5], 'C4': ['blank', 'blank', 'blank', 0, 190.5], 'G4': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'E6': ['blank', 'blank', 'blank', 0, 190.5], 'E8': ['blank', 'blank', 'blank', 0, 190.5], 'E9': ['blank', 'blank', 'blank', 0, 190.5], 'G9': ['blank', 'blank', 'blank', 0, 190.5], 'C10': ['blank', 'blank', 'blank', 0, 190.5], 'F10': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_092624_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('uninduced1clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
