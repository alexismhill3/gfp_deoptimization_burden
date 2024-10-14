import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'F6': ['C2', 'MCH10', 'R0.25', 42.60646974842882, 147.89353025157118], 'E5': ['D2', 'MCH10', 'R0.5', 23.038216074932638, 167.46178392506735], 'B5': ['E2', 'MCH10', 'R1', 21.585603118473912, 168.9143968815261], 'C6': ['F2', 'MCH10', 'R2', 19.76618440495498, 170.73381559504503], 'D3': ['G2', 'MCH10', 'R4', 18.394069792833548, 172.10593020716647], 'F2': ['C3', 'MCH25', 'R0.25', 16.107288057883935, 174.39271194211608], 'C5': ['D3', 'MCH25', 'R0.5', 19.358262118753537, 171.14173788124646], 'C3': ['E3', 'MCH25', 'R1', 26.044646347609294, 164.4553536523907], 'G2': ['F3', 'MCH25', 'R2', 21.15716422057784, 169.34283577942216], 'D2': ['G3', 'MCH25', 'R4', 21.695438641357896, 168.8045613586421], 'E3': ['C4', 'MCH50', 'R0.25', 14.14902846462644, 176.35097153537356], 'G3': ['D4', 'MCH50', 'R0.5', 15.634776096507085, 174.8652239034929], 'B3': ['E4', 'MCH50', 'R1', 16.3089232915383, 174.1910767084617], 'F5': ['F4', 'MCH50', 'R2', 18.102979811154135, 172.39702018884586], 'G4': ['G4', 'MCH50', 'R4', 14.885489694571104, 175.6145103054289], 'E6': ['C5', 'MCH75', 'R0.25', 14.708103432091235, 175.79189656790876], 'F3': ['D5', 'MCH75', 'R0.5', 15.92678605491683, 174.57321394508318], 'B6': ['E5', 'MCH75', 'R1', 17.219032164971413, 173.28096783502858], 'B2': ['F5', 'MCH75', 'R2', 15.293204614682802, 175.2067953853172], 'F4': ['G5', 'MCH75', 'R4', 13.803401813950348, 176.69659818604964], 'B4': ['C6', 'MCH90', 'R0.25', 13.844146945821048, 176.65585305417895], 'C2': ['D6', 'MCH90', 'R0.5', 14.885489694571104, 175.6145103054289], 'D4': ['E6', 'MCH90', 'R1', 15.081741646542229, 175.41825835345776], 'G6': ['F6', 'MCH90', 'R2', 14.30001879063297, 176.19998120936702], 'C4': ['G6', 'MCH90', 'R4', 13.997015450772729, 176.50298454922728], 'G9': ['C7', 'MCH10', 'R0.25', 43.11564493504888, 147.38435506495114], 'D9': ['D7', 'MCH10', 'R0.5', 24.341497852061604, 166.1585021479384], 'B9': ['E7', 'MCH10', 'R1', 22.13573667159755, 168.36426332840244], 'E7': ['F7', 'MCH10', 'R2', 19.74953751282787, 170.75046248717211], 'F10': ['G7', 'MCH10', 'R4', 18.315057200947912, 172.1849427990521], 'C11': ['C8', 'MCH25', 'R0.25', 16.263679657017203, 174.2363203429828], 'E9': ['D8', 'MCH25', 'R0.5', 19.239150542449373, 171.26084945755062], 'G7': ['E8', 'MCH25', 'R1', 24.215820523054887, 166.2841794769451], 'D10': ['F8', 'MCH25', 'R2', 20.165619319430625, 170.33438068056938], 'E10': ['G8', 'MCH25', 'R4', 21.516285492890937, 168.98371450710906], 'D11': ['C9', 'MCH50', 'R0.25', 13.5717349266368, 176.9282650733632], 'G11': ['D9', 'MCH50', 'R0.5', 15.393593454002161, 175.10640654599783], 'F11': ['E9', 'MCH50', 'R1', 15.233597946659817, 175.2664020533402], 'C7': ['F9', 'MCH50', 'R2', 17.219032164971413, 173.28096783502858], 'B7': ['G9', 'MCH50', 'R4', 14.625545754446092, 175.87445424555392], 'C10': ['C10', 'MCH75', 'R0.25', 14.378932409865758, 176.12106759013423], 'G8': ['D10', 'MCH75', 'R0.5', 15.562148210877282, 174.9378517891227], 'F9': ['E10', 'MCH75', 'R1', 16.662356636963153, 173.83764336303685], 'G10': ['F10', 'MCH75', 'R2', 14.698884206617391, 175.80111579338262], 'D8': ['G10', 'MCH75', 'R4', 13.393454535655305, 177.1065454643447], 'F8': ['C11', 'MCH90', 'R0.25', 13.38199052962407, 177.11800947037594], 'C8': ['D11', 'MCH90', 'R0.5', 13.963677993467458, 176.53632200653254], 'B8': ['E11', 'MCH90', 'R1', 14.46764082296816, 176.03235917703185], 'B11': ['F11', 'MCH90', 'R2', 13.901594694057664, 176.59840530594232], 'E11': ['G11', 'MCH90', 'R4', 13.926361896068547, 176.57363810393144], 'E2': ['blank', 'blank', 'blank', 0, 190.5], 'E4': ['blank', 'blank', 'blank', 0, 190.5], 'D5': ['blank', 'blank', 'blank', 0, 190.5], 'G5': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'D7': ['blank', 'blank', 'blank', 0, 190.5], 'F7': ['blank', 'blank', 'blank', 0, 190.5], 'E8': ['blank', 'blank', 'blank', 0, 190.5], 'C9': ['blank', 'blank', 'blank', 0, 190.5], 'B10': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_100424_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('uninduced9clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
