import pandas as pd
import os

# Directory containing the Excel files
input_directory = 'B&B'
# Output file name
output_file = 'merged_B&B_data.xlsx'

# List to hold DataFrames
dataframes = []

# Iterate through all Excel files in the directory
for file in os.listdir(input_directory):
    if file.endswith('.xlsx'):
        file_path = os.path.join(input_directory, file)
        # Read the Excel file
        df = pd.read_excel(file_path)
        dataframes.append(df)

# Concatenate all DataFrames
merged_df = pd.concat(dataframes, ignore_index=True)

# Save the merged DataFrame to a new Excel file
merged_df.to_excel(output_file, index=False)
print(f"Merged data saved to {output_file}.")