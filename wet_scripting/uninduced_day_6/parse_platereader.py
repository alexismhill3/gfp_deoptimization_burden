import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'E4': ['C2', 'GFP10', 'R0.25', 19.383064579703888, 171.1169354202961], 'C5': ['D2', 'GFP10', 'R0.5', 21.19636498455252, 169.30363501544747], 'D4': ['E2', 'GFP10', 'R1', 25.563416213026102, 164.9365837869739], 'F3': ['F2', 'GFP10', 'R2', 19.98602262742471, 170.51397737257528], 'D3': ['G2', 'GFP10', 'R4', 17.896440532179973, 172.60355946782002], 'C3': ['C3', 'GFP25', 'R0.25', 16.168925432110637, 174.33107456788937], 'C4': ['D3', 'GFP25', 'R0.5', 18.628588857259835, 171.87141114274016], 'G2': ['E3', 'GFP25', 'R1', 17.463305902452557, 173.03669409754744], 'E6': ['F3', 'GFP25', 'R2', 22.220685981988865, 168.27931401801112], 'G4': ['G3', 'GFP25', 'R4', 18.576939334547262, 171.92306066545274], 'B3': ['C4', 'GFP50', 'R0.25', 18.26584066387065, 172.23415933612935], 'F6': ['D4', 'GFP50', 'R0.5', 21.23475267503508, 169.26524732496492], 'G6': ['E4', 'GFP50', 'R1', 21.4975470627281, 169.0024529372719], 'F2': ['F4', 'GFP50', 'R2', 18.66565945934993, 171.83434054065006], 'E5': ['G4', 'GFP50', 'R4', 18.459951685604608, 172.0400483143954], 'D6': ['C5', 'GFP75', 'R0.25', 20.376764837364394, 170.1232351626356], 'B6': ['D5', 'GFP75', 'R0.5', 17.463305902452557, 173.03669409754744], 'C6': ['E5', 'GFP75', 'R1', 16.824336073783115, 173.67566392621688], 'C2': ['F5', 'GFP75', 'R2', 16.884904599144335, 173.61509540085567], 'E2': ['G5', 'GFP75', 'R4', 17.535125927068258, 172.96487407293174], 'G3': ['C6', 'GFP90', 'R0.25', 16.866688661979374, 173.63331133802063], 'B4': ['D6', 'GFP90', 'R0.5', 18.998339098708872, 171.50166090129113], 'G5': ['E6', 'GFP90', 'R1', 18.20204098851399, 172.297959011486], 'D5': ['F6', 'GFP90', 'R2', 18.710335841454434, 171.78966415854558], 'B2': ['G6', 'GFP90', 'R4', 14.966716206532023, 175.53328379346797], 'F10': ['C7', 'GFP10', 'R0.25', 20.26232262869863, 170.23767737130137], 'E10': ['D7', 'GFP10', 'R0.5', 20.940838786528243, 169.55916121347175], 'E11': ['E7', 'GFP10', 'R1', 26.031638244784755, 164.46836175521526], 'D7': ['F7', 'GFP10', 'R2', 21.16766659968283, 169.33233340031717], 'G7': ['G7', 'GFP10', 'R4', 17.707252074240934, 172.79274792575907], 'C7': ['C8', 'GFP25', 'R0.25', 16.915352694218093, 173.5846473057819], 'E9': ['D8', 'GFP25', 'R0.5', 18.68052638336931, 171.8194736166307], 'E8': ['E8', 'GFP25', 'R1', 17.55481513426886, 172.94518486573114], 'C11': ['F8', 'GFP25', 'R2', 21.487699301623543, 169.01230069837646], 'G9': ['G8', 'GFP25', 'R4', 18.380373306906105, 172.1196266930939], 'G8': ['C9', 'GFP50', 'R0.25', 19.060105788299, 171.439894211701], 'F9': ['D9', 'GFP50', 'R0.5', 20.773886127241536, 169.72611387275848], 'G10': ['E9', 'GFP50', 'R1', 21.129520861480493, 169.3704791385195], 'B11': ['F9', 'GFP50', 'R2', 18.65081396988508, 171.84918603011494], 'C8': ['G9', 'GFP50', 'R4', 18.591667406493034, 171.90833259350697], 'F8': ['C10', 'GFP75', 'R0.25', 19.479669195442824, 171.02033080455718], 'B8': ['D10', 'GFP75', 'R0.5', 18.194980571342615, 172.30501942865737], 'D10': ['E10', 'GFP75', 'R1', 16.8424605954963, 173.6575394045037], 'D11': ['F10', 'GFP75', 'R2', 17.056841625584312, 173.4431583744157], 'F11': ['G10', 'GFP75', 'R4', 18.518261836385857, 171.98173816361415], 'B9': ['C11', 'GFP90', 'R0.25', 16.59220933004488, 173.90779066995512], 'B10': ['D11', 'GFP90', 'R0.5', 14.745558478364828, 175.75444152163516], 'C9': ['E11', 'GFP90', 'R1', 17.848765933268403, 172.6512340667316], 'D8': ['F11', 'GFP90', 'R2', 17.848765933268403, 172.6512340667316], 'F7': ['G11', 'GFP90', 'R4', 15.005023068359858, 175.49497693164014], 'D2': ['blank', 'blank', 'blank', 0, 190.5], 'E3': ['blank', 'blank', 'blank', 0, 190.5], 'F4': ['blank', 'blank', 'blank', 0, 190.5], 'B5': ['blank', 'blank', 'blank', 0, 190.5], 'F5': ['blank', 'blank', 'blank', 0, 190.5], 'B7': ['blank', 'blank', 'blank', 0, 190.5], 'E7': ['blank', 'blank', 'blank', 0, 190.5], 'D9': ['blank', 'blank', 'blank', 0, 190.5], 'C10': ['blank', 'blank', 'blank', 0, 190.5], 'G11': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_100124_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('uninduced6clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
