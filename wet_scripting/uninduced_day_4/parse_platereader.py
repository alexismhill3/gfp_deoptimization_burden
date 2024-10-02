import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'C4': ['C2', 'GFP10', 'R0.25', 20.794146437318396, 169.7058535626816], 'F3': ['D2', 'GFP10', 'R0.5', 20.81260172690734, 169.68739827309267], 'F6': ['E2', 'GFP10', 'R1', 23.971990967137664, 166.52800903286234], 'F2': ['F2', 'GFP10', 'R2', 23.72942037040878, 166.77057962959123], 'E3': ['G2', 'GFP10', 'R4', 29.50688835797418, 160.9931116420258], 'G5': ['C3', 'GFP25', 'R0.25', 21.628406745248864, 168.87159325475113], 'B2': ['D3', 'GFP25', 'R0.5', 21.688417216166474, 168.81158278383353], 'B4': ['E3', 'GFP25', 'R1', 21.708494777586196, 168.7915052224138], 'D2': ['F3', 'GFP25', 'R2', 29.731347478178204, 160.7686525218218], 'C5': ['G3', 'GFP25', 'R4', 18.756728981997732, 171.74327101800228], 'C3': ['C4', 'GFP50', 'R0.25', 22.575787147970335, 167.92421285202965], 'F4': ['D4', 'GFP50', 'R0.5', 25.141355058472953, 165.35864494152705], 'B3': ['E4', 'GFP50', 'R1', 22.67401395504883, 167.82598604495118], 'D6': ['F4', 'GFP50', 'R2', 21.548907470150187, 168.9510925298498], 'D5': ['G4', 'GFP50', 'R4', 19.51370955206452, 170.9862904479355], 'F5': ['C5', 'GFP75', 'R0.25', 33.80266568649569, 156.6973343135043], 'D3': ['D5', 'GFP75', 'R0.5', 22.29674414249521, 168.2032558575048], 'G4': ['E5', 'GFP75', 'R1', 19.8355674518022, 170.6644325481978], 'B5': ['F5', 'GFP75', 'R2', 20.255323227489423, 170.2446767725106], 'E4': ['G5', 'GFP75', 'R4', 17.36759818383736, 173.13240181616266], 'E5': ['C6', 'GFP90', 'R0.25', 25.400055360958113, 165.0999446390419], 'G6': ['D6', 'GFP90', 'R0.5', 20.794146437318396, 169.7058535626816], 'E6': ['E6', 'GFP90', 'R1', 20.10769480656539, 170.3923051934346], 'G2': ['F6', 'GFP90', 'R2', 19.652712250113524, 170.84728774988648], 'C2': ['G6', 'GFP90', 'R4', 17.25260209218054, 173.24739790781945], 'F8': ['C7', 'GFP10', 'R0.25', 21.50937953128232, 168.99062046871768], 'F9': ['D7', 'GFP10', 'R0.5', 19.777018699378864, 170.72298130062114], 'G9': ['E7', 'GFP10', 'R1', 22.586660990543734, 167.91333900945625], 'C8': ['F7', 'GFP10', 'R2', 22.67401395504883, 167.82598604495118], 'E8': ['G7', 'GFP10', 'R4', 28.025812266375866, 162.47418773362415], 'E9': ['C8', 'GFP25', 'R0.25', 20.14223727591188, 170.3577627240881], 'G10': ['D8', 'GFP25', 'R0.5', 19.660952021166384, 170.8390479788336], 'B11': ['E8', 'GFP25', 'R1', 21.198283927854593, 169.3017160721454], 'F11': ['F8', 'GFP25', 'R2', 29.285795710959988, 161.21420428904003], 'G11': ['G8', 'GFP25', 'R4', 18.65971732225879, 171.84028267774121], 'C11': ['C9', 'GFP50', 'R0.25', 20.8681646744055, 169.6318353255945], 'D11': ['D9', 'GFP50', 'R0.5', 21.658368921561603, 168.8416310784384], 'B9': ['E9', 'GFP50', 'R1', 20.557177526037755, 169.94282247396225], 'D8': ['F9', 'GFP50', 'R2', 21.539012608526317, 168.96098739147368], 'C9': ['G9', 'GFP50', 'R4', 19.304876787607125, 171.19512321239287], 'G7': ['C10', 'GFP75', 'R0.25', 32.179210247336684, 158.3207897526633], 'D10': ['D10', 'GFP75', 'R0.5', 21.35269867209543, 169.1473013279046], 'D7': ['E10', 'GFP75', 'R1', 18.779258849173967, 171.72074115082603], 'B8': ['F10', 'GFP75', 'R2', 18.454141942878113, 172.04585805712188], 'D9': ['G10', 'GFP75', 'R4', 17.341910786781444, 173.15808921321855], 'F10': ['C11', 'GFP90', 'R0.25', 20.980182561159463, 169.51981743884053], 'F7': ['D11', 'GFP90', 'R0.5', 19.32078220724424, 171.17921779275576], 'B7': ['E11', 'GFP90', 'R1', 19.01528499529385, 171.48471500470615], 'G8': ['F11', 'GFP90', 'R2', 18.461404963612768, 172.03859503638722], 'C7': ['G11', 'GFP90', 'R4', 16.68784832068627, 173.81215167931373], 'E2': ['blank', 'blank', 'blank', 0, 190.5], 'G3': ['blank', 'blank', 'blank', 0, 190.5], 'D4': ['blank', 'blank', 'blank', 0, 190.5], 'B6': ['blank', 'blank', 'blank', 0, 190.5], 'C6': ['blank', 'blank', 'blank', 0, 190.5], 'E7': ['blank', 'blank', 'blank', 0, 190.5], 'B10': ['blank', 'blank', 'blank', 0, 190.5], 'C10': ['blank', 'blank', 'blank', 0, 190.5], 'E10': ['blank', 'blank', 'blank', 0, 190.5], 'E11': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_092924_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('uninduced4clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
