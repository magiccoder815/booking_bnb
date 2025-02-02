import pandas as pd
import numpy as np
import re

# Load the Excel file
file_path = 'updated_data.xlsx'
df = pd.read_excel(file_path)

# Change the column order
new_order = ['City', 'Name', 'Property Type', 'Address', 'Phone', 'Email', 'Link']
df = df[new_order]

# Remove duplicates based on the 'Name' column
df = df.drop_duplicates(subset='Name')

# Replace empty cells with "N/A"
df.fillna("N/A", inplace=True)

# Function to format and validate phone numbers
def format_phone_number(phone):
    # If the phone number is "N/A", return "N/A"
    if phone == "N/A":
        return "N/A"  
    
    # Normalize the phone number by removing spaces, parentheses, and dashes
    normalized_phone = re.sub(r'[^\d+]', '', str(phone).strip())
    
    # Check if it starts with '+39' and has the correct length
    if normalized_phone.startswith('+39') and len(normalized_phone) == 13:
        # Format as +39 XXX XXX XXXX
        return f"{normalized_phone[:3]} {normalized_phone[3:6]} {normalized_phone[6:]}"
    elif normalized_phone.startswith('0') and len(normalized_phone) == 11:
        # Format from local to international
        return f"+39 {normalized_phone[1:4]} {normalized_phone[4:7]} {normalized_phone[7:]}"
    
    return "N/A"  # Incomplete or non-Italian numbers will be replaced with "N/A"

# Apply the formatting function to 'Phone' column
df['Phone'] = df['Phone'].apply(format_phone_number)

# Save the modified DataFrame back to Excel
df.to_excel('updated_data_cleaned.xlsx', index=False)