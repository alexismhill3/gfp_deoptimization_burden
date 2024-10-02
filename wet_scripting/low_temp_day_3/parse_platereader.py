import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'E3': ['C2', 'GFP10', 'R0.25', 18.69392982038717, 171.80607017961285], 'B8': ['D2', 'GFP10', 'R0.5', 17.14914670260788, 173.35085329739212], 'E6': ['E2', 'GFP10', 'R1', 21.989405484269057, 168.51059451573093], 'D2': ['F2', 'GFP10', 'R2', 22.082585358838923, 168.4174146411611], 'B11': ['G2', 'GFP10', 'R4', 20.790460473600376, 169.70953952639962], 'C3': ['C3', 'GFP25', 'R0.25', 17.4101490213863, 173.0898509786137], 'F3': ['D3', 'GFP25', 'R0.5', 16.685474298629043, 173.81452570137097], 'B9': ['E3', 'GFP25', 'R1', 19.0508150206494, 171.4491849793506], 'C5': ['F3', 'GFP25', 'R2', 23.323488312434463, 167.17651168756555], 'C9': ['G3', 'GFP25', 'R4', 15.942486148536709, 174.55751385146328], 'F6': ['C4', 'GFP50', 'R0.25', 17.117851898422142, 173.38214810157785], 'E11': ['D4', 'GFP50', 'R0.5', 22.30310572643579, 168.19689427356423], 'G11': ['E4', 'GFP50', 'R1', 23.24258057762914, 167.25741942237084], 'G2': ['F4', 'GFP50', 'R2', 21.515299695467153, 168.98470030453285], 'G9': ['G4', 'GFP50', 'R4', 17.626067278361546, 172.87393272163845], 'D7': ['C5', 'GFP75', 'R0.25', 21.070667110254778, 169.4293328897452], 'B4': ['D5', 'GFP75', 'R0.5', 17.579818475932033, 172.92018152406797], 'C11': ['E5', 'GFP75', 'R1', 17.092897429056798, 173.4071025709432], 'G8': ['F5', 'GFP75', 'R2', 18.200629150859797, 172.2993708491402], 'F8': ['G5', 'GFP75', 'R4', 17.827055713249084, 172.67294428675092], 'C4': ['C6', 'GFP90', 'R0.25', 15.100678895601535, 175.39932110439847], 'F2': ['D6', 'GFP90', 'R0.5', 17.867805513641144, 172.63219448635886], 'C10': ['E6', 'GFP90', 'R1', 17.639323691403174, 172.86067630859682], 'G3': ['F6', 'GFP90', 'R2', 19.144128205266696, 171.3558717947333], 'E2': ['G6', 'GFP90', 'R4', 14.200006049237137, 176.29999395076285], 'G7': ['C7', 'MCH10', 'R0.25', 30.79729523358231, 159.7027047664177], 'E9': ['D7', 'MCH10', 'R0.5', 19.62475503935079, 170.8752449606492], 'B2': ['E7', 'MCH10', 'R1', 20.095632722917355, 170.40436727708266], 'G5': ['F7', 'MCH10', 'R2', 21.72458188650354, 168.77541811349647], 'D5': ['G7', 'MCH10', 'R4', 18.753727649513944, 171.74627235048607], 'E7': ['C8', 'MCH25', 'R0.25', 16.035147261586083, 174.46485273841392], 'C2': ['D8', 'MCH25', 'R0.5', 17.416613371616144, 173.08338662838386], 'F7': ['E8', 'MCH25', 'R1', 17.136614686628036, 173.36338531337196], 'C6': ['F8', 'MCH25', 'R2', 15.947906387132713, 174.55209361286728], 'G10': ['G8', 'MCH25', 'R4', 15.723356734253668, 174.77664326574634], 'F9': ['C9', 'MCH50', 'R0.25', 13.823336826653135, 176.67666317334687], 'C7': ['D9', 'MCH50', 'R0.5', 15.30767985950352, 175.1923201404965], 'E10': ['E9', 'MCH50', 'R1', 15.634254018018598, 174.8657459819814], 'F5': ['F9', 'MCH50', 'R2', 15.115279770676281, 175.3847202293237], 'B10': ['G9', 'MCH50', 'R4', 13.823336826653135, 176.67666317334687], 'D8': ['C10', 'MCH75', 'R0.25', 14.899203065184919, 175.6007969348151], 'D4': ['D10', 'MCH75', 'R0.5', 14.480594771470749, 176.01940522852925], 'B5': ['E10', 'MCH75', 'R1', 16.00778131724418, 174.49221868275583], 'C8': ['F10', 'MCH75', 'R2', 13.694180930261366, 176.80581906973865], 'G6': ['G10', 'MCH75', 'R4', 13.335949092783512, 177.16405090721648], 'E5': ['C11', 'MCH90', 'R0.25', 12.47737379321832, 178.0226262067817], 'D3': ['D11', 'MCH90', 'R0.5', 14.552483167913241, 175.94751683208676], 'F4': ['E11', 'MCH90', 'R1', 12.769528144285875, 177.73047185571411], 'D10': ['F11', 'MCH90', 'R2', 12.717589573291066, 177.78241042670894], 'E8': ['G11', 'MCH90', 'R4', 12.166644712120203, 178.33335528787978], 'B3': ['blank', 'blank', 'blank', 0, 190.5], 'B6': ['blank', 'blank', 'blank', 0, 190.5], 'B7': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'D9': ['blank', 'blank', 'blank', 0, 190.5], 'D11': ['blank', 'blank', 'blank', 0, 190.5], 'E4': ['blank', 'blank', 'blank', 0, 190.5], 'F10': ['blank', 'blank', 'blank', 0, 190.5], 'F11': ['blank', 'blank', 'blank', 0, 190.5], 'G4': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_092524_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('LT3clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
