import glob
import yaml
import pandas as pd
import os

# Path to root folder containing month-wise directories
path = r"C:\Users\sojay\DS\Project\Data-Driven Stock Analysis\Files\data\**\*.yaml"

files = glob.glob(path, recursive=True)

all_records = []

for file in files:
    with open(file, "r") as f:
        data = yaml.safe_load(f)
        
        # If file contains list of records
        for record in data:
            all_records.append(record)


df = pd.DataFrame(all_records)

# Field to group CSVs by
group_field = "Ticker"                 

# Output folder for CSVs
output_path = r"C:\Users\sojay\DS\Project\Data-Driven Stock Analysis\output_csv"
os.makedirs(output_path, exist_ok=True)

# Create separate CSV per Ticker
for Ticker, group_df in df.groupby(group_field):
    filename = f"{Ticker}.csv"
    group_df.to_csv(os.path.join(output_path, filename), index=False)

print("CSV files created successfully!")
