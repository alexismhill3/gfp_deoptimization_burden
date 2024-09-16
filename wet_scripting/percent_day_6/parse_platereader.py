import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'C6': ['C2', 'GFP10', 'R0.25', 56.43268450918091, 134.06731549081908], 'D7': ['D2', 'GFP10', 'R0.5', 35.79971024158715, 154.70028975841285], 'E5': ['E2', 'GFP10', 'R1', 43.06418248441604, 147.43581751558395], 'F9': ['F2', 'GFP10', 'R2', 46.20352392897618, 144.29647607102382], 'D2': ['G2', 'GFP10', 'R4', 35.636503363362465, 154.86349663663754], 'D5': ['C3', 'GFP25', 'R0.25', 32.910813305993585, 157.5891866940064], 'D4': ['D3', 'GFP25', 'R0.5', 30.935425422848628, 159.56457457715138], 'C4': ['E3', 'GFP25', 'R1', 27.09329385786714, 163.40670614213286], 'G8': ['F3', 'GFP25', 'R2', 38.19005146739254, 152.30994853260745], 'G5': ['G3', 'GFP25', 'R4', 33.71518895270709, 156.78481104729292], 'E10': ['C4', 'GFP50', 'R0.25', 43.99324512725053, 146.50675487274947], 'D8': ['D4', 'GFP50', 'R0.5', 32.3657451944015, 158.13425480559852], 'F6': ['E4', 'GFP50', 'R1', 32.63600186189126, 157.86399813810874], 'B8': ['F4', 'GFP50', 'R2', 47.70745759621089, 142.79254240378913], 'G7': ['G4', 'GFP50', 'R4', 40.428584327713274, 150.07141567228672], 'E2': ['C5', 'GFP75', 'R0.25', 35.024418521861335, 155.47558147813868], 'B2': ['D5', 'GFP75', 'R0.5', 33.331817401341326, 157.1681825986587], 'F2': ['E5', 'GFP75', 'R1', 34.58535448101346, 155.91464551898653], 'G10': ['F5', 'GFP75', 'R2', 35.79971024158715, 154.70028975841285], 'F4': ['G5', 'GFP75', 'R4', 30.85402341689735, 159.64597658310265], 'G3': ['C6', 'GFP90', 'R0.25', 35.636503363362465, 154.86349663663754], 'G11': ['D6', 'GFP90', 'R0.5', 39.84470399903818, 150.6552960009618], 'F3': ['E6', 'GFP90', 'R1', 39.0160568880121, 151.4839431119879], 'E8': ['F6', 'GFP90', 'R2', 36.61010225768831, 153.8898977423117], 'B5': ['G6', 'GFP90', 'R4', 29.66365269039431, 160.83634730960569], 'C10': ['C7', 'MCH10', 'R0.25', 55.0418974674318, 135.4581025325682], 'G6': ['D7', 'MCH10', 'R0.5', 33.35552295729257, 157.14447704270742], 'E3': ['E7', 'MCH10', 'R1', 25.025987800819582, 165.4740121991804], 'B9': ['F7', 'MCH10', 'R2', 26.814476478236713, 163.6855235217633], 'B7': ['G7', 'MCH10', 'R4', 25.543923211172554, 164.95607678882743], 'C3': ['C8', 'MCH25', 'R0.25', 27.474198339428625, 163.02580166057137], 'E6': ['D8', 'MCH25', 'R0.5', 26.937681024461664, 163.56231897553835], 'G9': ['E8', 'MCH25', 'R1', 25.06611152867458, 165.43388847132542], 'D11': ['F8', 'MCH25', 'R2', 23.508195528549187, 166.99180447145082], 'E4': ['G8', 'MCH25', 'R4', 21.67238121532383, 168.82761878467616], 'F7': ['C9', 'MCH50', 'R0.25', 34.8681886120874, 155.6318113879126], 'D3': ['D9', 'MCH50', 'R0.5', 39.14631400474312, 151.35368599525688], 'C9': ['E9', 'MCH50', 'R1', 25.782640295420915, 164.71735970457908], 'G2': ['F9', 'MCH50', 'R2', 27.587320251602332, 162.91267974839766], 'D6': ['G9', 'MCH50', 'R4', 25.25507498223827, 165.24492501776172], 'B6': ['C10', 'MCH75', 'R0.25', 35.854446603443066, 154.64555339655692], 'F11': ['D10', 'MCH75', 'R0.5', 40.014673241189556, 150.48532675881046], 'E9': ['E10', 'MCH75', 'R1', 25.543923211172554, 164.95607678882743], 'C5': ['F10', 'MCH75', 'R2', 19.906286122315215, 170.5937138776848], 'C11': ['G10', 'MCH75', 'R4', 23.567257617291396, 166.9327423827086], 'F8': ['C11', 'MCH90', 'R0.25', 35.314509559898845, 155.18549044010115], 'D9': ['D11', 'MCH90', 'R0.5', 64.7717118450412, 125.7282881549588], 'B10': ['E11', 'MCH90', 'R1', 24.199576406279437, 166.30042359372055], 'B3': ['F11', 'MCH90', 'R2', 28.701548949680156, 161.79845105031984], 'C7': ['G11', 'MCH90', 'R4', 26.999711157473698, 163.5002888425263], 'B4': ['blank', 'blank', 'blank', 0, 190.5], 'B11': ['blank', 'blank', 'blank', 0, 190.5], 'C2': ['blank', 'blank', 'blank', 0, 190.5], 'C8': ['blank', 'blank', 'blank', 0, 190.5], 'D10': ['blank', 'blank', 'blank', 0, 190.5], 'E7': ['blank', 'blank', 'blank', 0, 190.5], 'E11': ['blank', 'blank', 'blank', 0, 190.5], 'F5': ['blank', 'blank', 'blank', 0, 190.5], 'F10': ['blank', 'blank', 'blank', 0, 190.5], 'G4': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_082924_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('per2clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
