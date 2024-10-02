import pandas as pd
import openpyxl as xl
from rich import print
import numbers

well_encoding = {'C6': ['C2', 'GFP50', 'R0.25', 18.036841082087488, 172.46315891791252], 'E6': ['D2', 'GFP50', 'R0.5', 22.32008897721123, 168.17991102278876], 'B3': ['E2', 'GFP50', 'R1', 19.466732959836342, 171.03326704016365], 'F3': ['F2', 'GFP50', 'R2', 16.11558944981405, 174.38441055018595], 'G5': ['G2', 'GFP50', 'R4', 16.221491350370783, 174.2785086496292], 'G6': ['C3', 'GAG', 'R0.25', 19.211567922062915, 171.28843207793707], 'B6': ['D3', 'GAG', 'R0.5', 18.029908218211297, 172.4700917817887], 'D4': ['E3', 'GAG', 'R1', 19.08647754930039, 171.41352245069962], 'D3': ['F3', 'GAG', 'R2', 20.469252341582436, 170.03074765841757], 'B5': ['G3', 'GAG', 'R4', 17.906005469702997, 172.593994530297], 'E3': ['C4', 'GGA', 'R0.25', 16.863049331697663, 173.63695066830235], 'F2': ['D4', 'GGA', 'R0.5', 20.05781846591816, 170.44218153408184], 'G3': ['E4', 'GGA', 'R1', 20.5050493048543, 169.9949506951457], 'C3': ['F4', 'GGA', 'R2', 25.55505727160417, 164.94494272839583], 'B2': ['G4', 'GGA', 'R4', 18.765734047068293, 171.7342659529317], 'C5': ['C5', 'GGG', 'R0.25', 19.250995169094075, 171.24900483090593], 'C4': ['D5', 'GGG', 'R0.5', 18.397677793388027, 172.10232220661197], 'E5': ['E5', 'GGG', 'R1', 20.25707327627014, 170.24292672372985], 'E2': ['F5', 'GGG', 'R2', 17.892343310930894, 172.6076566890691], 'F5': ['G5', 'GGG', 'R4', 18.668629455913955, 171.83137054408604], 'D5': ['C6', 'CTA', 'R0.25', 18.63154927337497, 171.86845072662504], 'G2': ['D6', 'CTA', 'R0.5', 18.947683572126472, 171.55231642787354], 'F4': ['E6', 'CTA', 'R1', 19.929971014045194, 170.57002898595482], 'C2': ['F6', 'CTA', 'R2', 19.314418376851926, 171.18558162314807], 'G4': ['G6', 'CTA', 'R4', 15.270797901083116, 175.2292020989169], 'D8': ['C7', 'GFP50', 'R0.25', 16.96061860922678, 173.53938139077323], 'G9': ['D7', 'GFP50', 'R0.5', 20.640409028505143, 169.85959097149487], 'G10': ['E7', 'GFP50', 'R1', 18.470128626284094, 172.0298713737159], 'C9': ['F7', 'GFP50', 'R2', 15.60616259949516, 174.89383740050485], 'F8': ['G7', 'GFP50', 'R4', 15.806019348333471, 174.69398065166652], 'B11': ['C8', 'GAG', 'R0.25', 19.211567922062915, 171.28843207793707], 'C11': ['D8', 'GAG', 'R0.5', 17.146639206919797, 173.3533607930802], 'D10': ['E8', 'GAG', 'R1', 18.26868689936381, 172.23131310063619], 'D7': ['F8', 'GAG', 'R2', 19.410338249927996, 171.089661750072], 'F11': ['G8', 'GAG', 'R4', 18.521187287709992, 171.97881271229], 'F7': ['C9', 'GGA', 'R0.25', 15.811347174693832, 174.68865282530618], 'C10': ['D9', 'GGA', 'R0.5', 18.83355385433996, 171.66644614566005], 'D9': ['E9', 'GGA', 'R1', 19.172301843903526, 171.32769815609646], 'C7': ['F9', 'GGA', 'R2', 26.30022775082969, 164.1997722491703], 'B8': ['G9', 'GGA', 'R4', 18.470128626284094, 172.0298713737159], 'E9': ['C10', 'GGG', 'R0.25', 19.43446666584052, 171.06553333415948], 'B9': ['D10', 'GGG', 'R0.5', 17.97462837278839, 172.5253716272116], 'E7': ['E10', 'GGG', 'R1', 19.703903113521363, 170.79609688647864], 'C8': ['F10', 'GGG', 'R2', 17.40756462470755, 173.09243537529244], 'E10': ['G10', 'GGG', 'R4', 18.53582487220107, 171.96417512779894], 'G8': ['C11', 'CTA', 'R0.25', 18.871443265186592, 171.6285567348134], 'F9': ['D11', 'CTA', 'R0.5', 23.9499568448945, 166.5500431551055], 'B10': ['E11', 'CTA', 'R1', 19.703903113521363, 170.79609688647864], 'G7': ['F11', 'CTA', 'R2', 18.818440206647484, 171.6815597933525], 'B7': ['G11', 'CTA', 'R4', 15.554405142350797, 174.9455948576492], 'D2': ['blank', 'blank', 'blank', 0, 190.5], 'B4': ['blank', 'blank', 'blank', 0, 190.5], 'E4': ['blank', 'blank', 'blank', 0, 190.5], 'D6': ['blank', 'blank', 'blank', 0, 190.5], 'F6': ['blank', 'blank', 'blank', 0, 190.5], 'E8': ['blank', 'blank', 'blank', 0, 190.5], 'F10': ['blank', 'blank', 'blank', 0, 190.5], 'D11': ['blank', 'blank', 'blank', 0, 190.5], 'E11': ['blank', 'blank', 'blank', 0, 190.5], 'G11': ['blank', 'blank', 'blank', 0, 190.5]}


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
    file = "cr_092724_post.xlsx"

    categories = ['mCherry', 'GFP', 'OD660']

    data = parse_platereader(file, categories)

    # write clean data as a csv
    data[0].to_csv('uninduced2clean.csv', index=False)

    data[0].head()


if __name__ == '__main__':
    main()


# EOF
