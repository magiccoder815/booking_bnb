import pandas as pd

# Load the Excel file
file_path = 'updated_without_score.xlsx'  # Replace with your file path
df = pd.read_excel(file_path)

# Remove duplicates based on 'City' and 'Name' columns
deduplicated_df = df.drop_duplicates(subset=['City', 'Name'])

# Replace empty cells with 'N/A'
deduplicated_df.fillna('N/A', inplace=True)

# Save the deduplicated DataFrame to a new Excel file
deduplicated_df.to_excel('deduplicated_updated_without_score.xlsx', index=False)