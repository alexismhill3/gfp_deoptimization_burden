import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'D2': ['C2', 'GFP10', 'R0.25', 56.05497490318865, 134.44502509681135], 'C6': ['D2', 'GFP10', 'R0.5', 35.892861140300184, 154.60713885969983], 'F9': ['E2', 'GFP10', 'R1', 44.80863567809558, 145.69136432190442], 'E10': ['F2', 'GFP10', 'R2', 47.056490097762136, 143.44350990223785], 'C4': ['G2', 'GFP10', 'R4', 48.21754066561134, 142.28245933438865], 'B2': ['C3', 'GFP25', 'R0.25', 31.868721841202678, 158.63127815879733], 'B4': ['D3', 'GFP25', 'R0.5', 32.1527388768729, 158.3472611231271], 'G2': ['E3', 'GFP25', 'R1', 30.206222473853018, 160.29377752614698], 'D11': ['F3', 'GFP25', 'R2', 38.42156176727959, 152.0784382327204], 'C10': ['G3', 'GFP25', 'R4', 26.95935877745282, 163.54064122254718], 'F7': ['C4', 'GFP50', 'R0.25', 43.886219014310825, 146.61378098568917], 'F3': ['D4', 'GFP50', 'R0.5', 25.959595930974118, 164.5404040690259], 'B5': ['E4', 'GFP50', 'R1', 34.117405896201745, 156.38259410379825], 'F6': ['F4', 'GFP50', 'R2', 21.63638954177945, 168.86361045822053], 'B6': ['G4', 'GFP50', 'R4', 32.59970912891794, 157.90029087108206], 'C3': ['C5', 'GFP75', 'R0.25', 30.109263068303914, 160.3907369316961], 'D6': ['D5', 'GFP75', 'R0.5', 29.63366386714294, 160.86633613285707], 'E11': ['E5', 'GFP75', 'R1', 32.71339849566044, 157.78660150433956], 'E8': ['F5', 'GFP75', 'R2', 28.568679464291062, 161.93132053570895], 'D8': ['G5', 'GFP75', 'R4', 29.540342448038086, 160.95965755196193], 'F5': ['C6', 'GFP90', 'R0.25', 33.46022870596006, 157.03977129403995], 'D10': ['D6', 'GFP90', 'R0.5', 32.50932232502591, 157.99067767497408], 'D5': ['E6', 'GFP90', 'R1', 35.431896951017144, 155.06810304898286], 'B7': ['F6', 'GFP90', 'R2', 23.667153802885498, 166.8328461971145], 'D4': ['G6', 'GFP90', 'R4', 31.025468079996916, 159.47453192000307], 'E7': ['C7', 'MCH10', 'R0.25', 60.77646853532118, 129.7235314646788], 'G5': ['D7', 'MCH10', 'R0.5', 27.48063482924493, 163.01936517075507], 'E6': ['E7', 'MCH10', 'R1', 27.336480372234963, 163.16351962776503], 'D7': ['F7', 'MCH10', 'R2', 24.740833350421198, 165.7591666495788], 'G11': ['G7', 'MCH10', 'R4', 23.084707301350047, 167.41529269864995], 'C7': ['C8', 'MCH25', 'R0.25', 23.256410106877254, 167.24358989312276], 'F4': ['D8', 'MCH25', 'R0.5', 24.675750711148204, 165.8242492888518], 'E5': ['E8', 'MCH25', 'R1', 23.643291773979808, 166.8567082260202], 'F10': ['F8', 'MCH25', 'R2', 23.703039078656154, 166.79696092134384], 'C8': ['G8', 'MCH25', 'R4', 23.40729498645498, 167.09270501354501], 'C2': ['C9', 'MCH50', 'R0.25', 23.82343697625881, 166.67656302374118], 'F11': ['D9', 'MCH50', 'R0.5', 38.07842740037595, 152.42157259962406], 'B11': ['E9', 'MCH50', 'R1', 23.54832641939199, 166.951673580608], 'B3': ['F9', 'MCH50', 'R2', 22.454733367616612, 168.0452666323834], 'G4': ['G9', 'MCH50', 'R4', 23.454117390801738, 167.04588260919826], 'E2': ['C10', 'MCH75', 'R0.25', 30.402023894383568, 160.09797610561643], 'C5': ['D10', 'MCH75', 'R0.5', 41.26084073989592, 149.2391592601041], 'G3': ['E10', 'MCH75', 'R1', 23.221863454756424, 167.27813654524357], 'G6': ['F10', 'MCH75', 'R2', 22.273447538343582, 168.2265524616564], 'E9': ['G10', 'MCH75', 'R4', 22.815195484089404, 167.6848045159106], 'C11': ['C11', 'MCH90', 'R0.25', 37.469998822285824, 153.03000117771418], 'E4': ['D11', 'MCH90', 'R0.5', 30.323398333737583, 160.17660166626243], 'B9': ['E11', 'MCH90', 'R1', 29.63366386714294, 160.86633613285707], 'E3': ['F11', 'MCH90', 'R2', 32.02102936992113, 158.47897063007886], 'G9': ['G11', 'MCH90', 'R4', 27.806486383906353, 162.69351361609364], 'B8': ['blank', 'blank', 'blank', 0, 190.5], 'B10': ['blank', 'blank', 'blank', 0, 190.5], 'C9': ['blank', 'blank', 'blank', 0, 190.5], 'D3': ['blank', 'blank', 'blank', 0, 190.5], 'D9': ['blank', 'blank', 'blank', 0, 190.5], 'F2': ['blank', 'blank', 'blank', 0, 190.5], 'F8': ['blank', 'blank', 'blank', 0, 190.5], 'G7': ['blank', 'blank', 'blank', 0, 190.5], 'G8': ['blank', 'blank', 'blank', 0, 190.5], 'G10': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_082824_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('per1clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
