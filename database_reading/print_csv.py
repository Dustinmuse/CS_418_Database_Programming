import pandas as pd

data = pd.read_csv('Crime_Incidents_in_2024.csv')
print(f'Number of Rows: {len(data)}')
print(f'Number of Columns: {len(data.columns)}')