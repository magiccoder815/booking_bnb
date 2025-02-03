import pandas as pd

def format_phone_number(phone):
    # Check if the phone number is NaN
    if pd.isna(phone):
        return None  # Return None for NaN values
    
    # Remove all non-digit characters
    cleaned_number = ''.join(filter(str.isdigit, phone))
    
    # If the cleaned number has less than 10 digits, add 39
    if len(cleaned_number) <= 10:
        cleaned_number = '39' + cleaned_number
    
    # If the formatted number has less than 12 digits, return None
    if len(cleaned_number) < 12:
        return None
    
    # If it has more than 12 digits, cut to the first 12 digits
    cleaned_number = cleaned_number[:12]

    # Format the cleaned number as "+39 XXX XXX XXXX"
    formatted_number = f"+39 {cleaned_number[2:5]} {cleaned_number[5:8]} {cleaned_number[8:]}"
    
    return formatted_number

# Load the Excel file
df = pd.read_excel('updated_data.xlsx')  # Replace with your file
df['Formatted Phone'] = df['Phone'].apply(format_phone_number)  # Apply formatting function

# Save the updated DataFrame to a new Excel file
df.to_excel('formatted_phone_numbers.xlsx', index=False)  # Replace with your desired output file name