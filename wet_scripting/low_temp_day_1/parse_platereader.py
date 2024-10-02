import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'E11': ['C2', 'GFP10', 'R0.25', 22.28932739277357, 168.21067260722643], 'G10': ['D2', 'GFP10', 'R0.5', 18.766486328064854, 171.73351367193516], 'E7': ['E2', 'GFP10', 'R1', 27.440441610365212, 163.0595583896348], 'F6': ['F2', 'GFP10', 'R2', 28.014095439235927, 162.48590456076408], 'B7': ['G2', 'GFP10', 'R4', 27.06046609310986, 163.43953390689015], 'C11': ['C3', 'GFP25', 'R0.25', 22.01727515647429, 168.48272484352572], 'B6': ['D3', 'GFP25', 'R0.5', 22.28932739277357, 168.21067260722643], 'C6': ['E3', 'GFP25', 'R1', 20.577921987621377, 169.92207801237862], 'G8': ['F3', 'GFP25', 'R2', 26.951615133748568, 163.54838486625144], 'C9': ['G3', 'GFP25', 'R4', 20.8431253692568, 169.6568746307432], 'E4': ['C4', 'GFP50', 'R0.25', 21.03004285023948, 169.46995714976052], 'F9': ['D4', 'GFP50', 'R0.5', 26.63025385305647, 163.86974614694353], 'D11': ['E4', 'GFP50', 'R1', 27.029275540388987, 163.470724459611], 'B8': ['F4', 'GFP50', 'R2', 25.528630823040093, 164.9713691769599], 'F3': ['G4', 'GFP50', 'R4', 20.04153491573178, 170.45846508426823], 'D3': ['C5', 'GFP75', 'R0.25', 21.863321484242118, 168.6366785157579], 'C7': ['D5', 'GFP75', 'R0.5', 20.301791281708354, 170.19820871829165], 'F8': ['E5', 'GFP75', 'R1', 21.65137072150179, 168.8486292784982], 'D5': ['F5', 'GFP75', 'R2', 19.981765771796713, 170.51823422820328], 'G7': ['G5', 'GFP75', 'R4', 18.00291816845077, 172.49708183154922], 'F4': ['C6', 'GFP90', 'R0.25', 17.492615505192514, 173.0073844948075], 'B11': ['D6', 'GFP90', 'R0.5', 21.365341804599762, 169.13465819540025], 'G4': ['E6', 'GFP90', 'R1', 20.08444617887977, 170.41555382112023], 'E10': ['F6', 'GFP90', 'R2', 22.96601679927361, 167.5339832007264], 'C8': ['G6', 'GFP90', 'R4', 19.947771039395313, 170.55222896060468], 'D8': ['C7', 'MCH10', 'R0.25', 36.32373057498434, 154.17626942501568], 'B4': ['D7', 'MCH10', 'R0.5', 23.793224060362054, 166.70677593963794], 'G5': ['E7', 'MCH10', 'R1', 29.812611617987123, 160.68738838201287], 'E9': ['F7', 'MCH10', 'R2', 24.098860720995006, 166.401139279005], 'F7': ['G7', 'MCH10', 'R4', 25.349258860234336, 165.15074113976567], 'G9': ['C8', 'MCH25', 'R0.25', 21.83278996203352, 168.66721003796647], 'G3': ['D8', 'MCH25', 'R0.5', 21.115253755368006, 169.384746244632], 'D2': ['E8', 'MCH25', 'R1', 20.523891873880125, 169.97610812611987], 'D7': ['F8', 'MCH25', 'R2', 29.254739775227854, 161.24526022477215], 'F10': ['G8', 'MCH25', 'R4', 19.157421469661756, 171.34257853033824], 'F2': ['C9', 'MCH50', 'R0.25', 16.912303307538394, 173.5876966924616], 'C2': ['D9', 'MCH50', 'R0.5', 18.42731385281783, 172.07268614718217], 'B2': ['E9', 'MCH50', 'R1', 22.048325203035745, 168.45167479696426], 'E2': ['F9', 'MCH50', 'R2', 20.532878520445035, 169.96712147955498], 'G6': ['G9', 'MCH50', 'R4', 17.41467486333191, 173.08532513666808], 'B3': ['C10', 'MCH75', 'R0.25', 15.617074876931152, 174.88292512306884], 'B10': ['D10', 'MCH75', 'R0.5', 17.886202393000225, 172.61379760699978], 'C5': ['E10', 'MCH75', 'R1', 25.487013939107644, 165.01298606089236], 'E5': ['F10', 'MCH75', 'R2', 18.333671299969044, 172.16632870003096], 'B5': ['G10', 'MCH75', 'R4', 15.050766851572881, 175.4492331484271], 'G11': ['C11', 'MCH90', 'R0.25', 16.138324716887993, 174.361675283112], 'C4': ['D11', 'MCH90', 'R0.5', 17.466557242966907, 173.0334427570331], 'F11': ['E11', 'MCH90', 'R1', 16.91840499954035, 173.58159500045966], 'G2': ['F11', 'MCH90', 'R2', 14.794397631797418, 175.7056023682026], 'F5': ['G11', 'MCH90', 'R4', 15.336211170638524, 175.16378882936147], 'B9': ['blank', 'blank', 'blank', 0, 190.5], 'C3': ['blank', 'blank', 'blank', 0, 190.5], 'C10': ['blank', 'blank', 'blank', 0, 190.5], 'D4': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'D9': ['blank', 'blank', 'blank', 0, 190.5], 'D10': ['blank', 'blank', 'blank', 0, 190.5], 'E3': ['blank', 'blank', 'blank', 0, 190.5], 'E6': ['blank', 'blank', 'blank', 0, 190.5], 'E8': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_092324_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('LT1clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
