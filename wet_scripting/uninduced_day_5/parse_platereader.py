import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'D6': ['C2', 'GFP10', 'R0.25', 13.8777375165995, 176.6222624834005], 'F4': ['D2', 'GFP10', 'R0.5', 16.091814163887513, 174.4081858361125], 'F2': ['E2', 'GFP10', 'R1', 14.227142638846612, 176.2728573611534], 'F6': ['F2', 'GFP10', 'R2', 17.277388337785492, 173.22261166221452], 'C3': ['G2', 'GFP10', 'R4', 15.155819963629385, 175.3441800363706], 'B2': ['C3', 'GFP25', 'R0.25', 14.78786763947348, 175.7121323605265], 'D3': ['D3', 'GFP25', 'R0.5', 15.714401138453551, 174.78559886154645], 'G2': ['E3', 'GFP25', 'R1', 17.01414841536383, 173.48585158463618], 'F5': ['F3', 'GFP25', 'R2', 17.52922787204852, 172.97077212795148], 'C5': ['G3', 'GFP25', 'R4', 15.563180561231112, 174.93681943876888], 'B6': ['C4', 'GFP50', 'R0.25', 16.186222733764055, 174.31377726623595], 'D2': ['D4', 'GFP50', 'R0.5', 16.20299945746767, 174.29700054253232], 'E2': ['E4', 'GFP50', 'R1', 17.548903828856606, 172.9510961711434], 'F3': ['F4', 'GFP50', 'R2', 17.11347918905961, 173.3865208109404], 'B4': ['G4', 'GFP50', 'R4', 13.869529583785376, 176.63047041621462], 'C4': ['C5', 'GFP75', 'R0.25', 22.72785476876215, 167.77214523123786], 'C6': ['D5', 'GFP75', 'R0.5', 15.063334357812694, 175.4366656421873], 'D5': ['E5', 'GFP75', 'R1', 13.57644838734372, 176.92355161265627], 'E3': ['F5', 'GFP75', 'R2', 13.250424140085542, 177.24957585991444], 'D4': ['G5', 'GFP75', 'R4', 12.418895659495716, 178.08110434050428], 'B5': ['C6', 'GFP90', 'R0.25', 12.742813482781473, 177.7571865172185], 'C2': ['D6', 'GFP90', 'R0.5', 14.069234494599595, 176.43076550540042], 'G4': ['E6', 'GFP90', 'R1', 15.131372252148184, 175.3686277478518], 'G5': ['F6', 'GFP90', 'R2', 13.76370444749255, 176.73629555250744], 'E4': ['G6', 'GFP90', 'R4', 13.521651222357342, 176.97834877764265], 'E10': ['C7', 'GFP10', 'R0.25', 15.62019633775193, 174.87980366224807], 'B8': ['D7', 'GFP10', 'R0.5', 16.304386252275215, 174.1956137477248], 'D8': ['E7', 'GFP10', 'R1', 14.331479546209982, 176.16852045379002], 'B10': ['F7', 'GFP10', 'R2', 17.938193970449976, 172.56180602955], 'D10': ['G7', 'GFP10', 'R4', 14.924330703668037, 175.57566929633197], 'G11': ['C8', 'GFP25', 'R0.25', 15.204953155468981, 175.29504684453102], 'B11': ['D8', 'GFP25', 'R0.5', 15.594227250168313, 174.9057727498317], 'G10': ['E8', 'GFP25', 'R1', 17.601590299511212, 172.8984097004888], 'C11': ['F8', 'GFP25', 'R2', 17.56862400647386, 172.93137599352613], 'F10': ['G8', 'GFP25', 'R4', 15.30418296478777, 175.19581703521223], 'E11': ['C9', 'GFP50', 'R0.25', 20.646769740296627, 169.85323025970337], 'G8': ['D9', 'GFP50', 'R0.5', 16.113927661986054, 174.38607233801395], 'D9': ['E9', 'GFP50', 'R1', 17.36695449654471, 173.1330455034553], 'E9': ['F9', 'GFP50', 'R2', 17.52267772023051, 172.97732227976948], 'G9': ['G9', 'GFP50', 'R4', 14.309617062526382, 176.19038293747363], 'F9': ['C10', 'GFP75', 'R0.25', 23.373467210332077, 167.12653278966792], 'C9': ['D10', 'GFP75', 'R0.5', 15.160718404806484, 175.3392815951935], 'B7': ['E10', 'GFP75', 'R1', 13.440279878437094, 177.05972012156292], 'F7': ['F10', 'GFP75', 'R2', 13.83271432521209, 176.6672856747879], 'D11': ['G10', 'GFP75', 'R4', 12.585520518866716, 177.9144794811333], 'E8': ['C11', 'GFP90', 'R0.25', 12.548480387584565, 177.95151961241544], 'F11': ['D11', 'GFP90', 'R0.5', 14.002030239800966, 176.49796976019903], 'D7': ['E11', 'GFP90', 'R1', 14.986323579616665, 175.51367642038335], 'B9': ['F11', 'GFP90', 'R2', 14.626457577239691, 175.8735424227603], 'C10': ['G11', 'GFP90', 'R4', 13.467294623022758, 177.03270537697725], 'B3': ['blank', 'blank', 'blank', 0, 190.5], 'G3': ['blank', 'blank', 'blank', 0, 190.5], 'E5': ['blank', 'blank', 'blank', 0, 190.5], 'E6': ['blank', 'blank', 'blank', 0, 190.5], 'G6': ['blank', 'blank', 'blank', 0, 190.5], 'C7': ['blank', 'blank', 'blank', 0, 190.5], 'E7': ['blank', 'blank', 'blank', 0, 190.5], 'G7': ['blank', 'blank', 'blank', 0, 190.5], 'C8': ['blank', 'blank', 'blank', 0, 190.5], 'F8': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_093024_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('uninduced5clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
