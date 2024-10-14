import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'E4': ['C2', 'MCH10', 'R0.25', 42.15459120062498, 148.34540879937504], 'D2': ['D2', 'MCH10', 'R0.5', 21.9000744274361, 168.5999255725639], 'B5': ['E2', 'MCH10', 'R1', 21.31291482104403, 169.18708517895598], 'B4': ['F2', 'MCH10', 'R2', 17.386269903184708, 173.1137300968153], 'B2': ['G2', 'MCH10', 'R4', 16.716994923066572, 173.78300507693342], 'C2': ['C3', 'MCH25', 'R0.25', 15.314177636803569, 175.18582236319642], 'D4': ['D3', 'MCH25', 'R0.5', 15.029545313020218, 175.4704546869798], 'D5': ['E3', 'MCH25', 'R1', 15.98759190962245, 174.51240809037756], 'F2': ['F3', 'MCH25', 'R2', 20.84868358277926, 169.65131641722076], 'G4': ['G3', 'MCH25', 'R4', 20.92309128132677, 169.57690871867322], 'C6': ['C4', 'MCH50', 'R0.25', 13.28796471898788, 177.2120352810121], 'B3': ['D4', 'MCH50', 'R0.5', 13.84087772452074, 176.65912227547926], 'B6': ['E4', 'MCH50', 'R1', 16.716994923066572, 173.78300507693342], 'D3': ['F4', 'MCH50', 'R2', 16.00942132358338, 174.49057867641662], 'C5': ['G4', 'MCH50', 'R4', 12.224678224913049, 178.27532177508695], 'E6': ['C5', 'MCH75', 'R0.25', 13.375121058066568, 177.12487894193345], 'E2': ['D5', 'MCH75', 'R0.5', 17.001813177625767, 173.49818682237424], 'G5': ['E5', 'MCH75', 'R1', 14.755301775305183, 175.74469822469482], 'E3': ['F5', 'MCH75', 'R2', 12.650016140594028, 177.84998385940597], 'C4': ['G5', 'MCH75', 'R4', 13.011485656419913, 177.48851434358008], 'F4': ['C6', 'MCH90', 'R0.25', 13.707388598833766, 176.79261140116623], 'E5': ['D6', 'MCH90', 'R0.5', 13.401874240549713, 177.09812575945028], 'C3': ['E6', 'MCH90', 'R1', 12.656843769236994, 177.84315623076301], 'F5': ['F6', 'MCH90', 'R2', 12.975488020075549, 177.52451197992445], 'G3': ['G6', 'MCH90', 'R4', 11.920194798370863, 178.57980520162914], 'F11': ['C7', 'MCH10', 'R0.25', 49.28667505997688, 141.2133249400231], 'C7': ['D7', 'MCH10', 'R0.5', 23.478774831798223, 167.02122516820177], 'F10': ['E7', 'MCH10', 'R1', 20.876525753118045, 169.62347424688195], 'B8': ['F7', 'MCH10', 'R2', 18.778506664202258, 171.72149333579773], 'G7': ['G7', 'MCH10', 'R4', 19.05313555135886, 171.44686444864115], 'B9': ['C8', 'MCH25', 'R0.25', 16.581065511229383, 173.91893448877062], 'E8': ['D8', 'MCH25', 'R0.5', 14.46407186856152, 176.03592813143848], 'F8': ['E8', 'MCH25', 'R1', 15.719667643754843, 174.78033235624517], 'C10': ['F8', 'MCH25', 'R2', 23.53768899444123, 166.96231100555877], 'E9': ['G8', 'MCH25', 'R4', 21.798290668831644, 168.70170933116836], 'G9': ['C9', 'MCH50', 'R0.25', 13.755631020474501, 176.7443689795255], 'G10': ['D9', 'MCH50', 'R0.5', 14.379813970934546, 176.12018602906545], 'D7': ['E9', 'MCH50', 'R1', 16.418539171567733, 174.08146082843226], 'F7': ['F9', 'MCH50', 'R2', 15.394603825350991, 175.105396174649], 'B7': ['G9', 'MCH50', 'R4', 14.086137013384448, 176.41386298661556], 'E11': ['C10', 'MCH75', 'R0.25', 13.08408238970138, 177.4159176102986], 'B10': ['D10', 'MCH75', 'R0.5', 16.55180619507654, 173.94819380492345], 'G11': ['E10', 'MCH75', 'R1', 14.690596608325702, 175.8094033916743], 'E10': ['F10', 'MCH75', 'R2', 13.771787778762818, 176.7282122212372], 'F9': ['G10', 'MCH75', 'R4', 13.124355920146758, 177.37564407985323], 'C11': ['C11', 'MCH90', 'R0.25', 13.348474473637035, 177.15152552636297], 'D9': ['D11', 'MCH90', 'R0.5', 13.401874240549713, 177.09812575945028], 'B11': ['E11', 'MCH90', 'R1', 13.939606417919356, 176.56039358208065], 'E7': ['F11', 'MCH90', 'R2', 12.373027767561293, 178.1269722324387], 'D11': ['G11', 'MCH90', 'R4', 13.022323389317444, 177.47767661068255], 'G2': ['blank', 'blank', 'blank', 0, 190.5], 'F3': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'F6': ['blank', 'blank', 'blank', 0, 190.5], 'G6': ['blank', 'blank', 'blank', 0, 190.5], 'C8': ['blank', 'blank', 'blank', 0, 190.5], 'D8': ['blank', 'blank', 'blank', 0, 190.5], 'G8': ['blank', 'blank', 'blank', 0, 190.5], 'C9': ['blank', 'blank', 'blank', 0, 190.5], 'D10': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_100224_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('uninduced7clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
