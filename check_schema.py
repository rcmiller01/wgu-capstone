import pandas as pd

df = pd.read_parquet('data/processed/processed_data.parquet')
print('Columns and dtypes:')
for col in df.columns:
    print(f'  {col}: {df[col].dtype}')

print(f'\nTotal columns: {len(df.columns)}')
print(f'Total rows: {len(df)}')
