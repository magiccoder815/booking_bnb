import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import re  # Import regular expressions

def scrape_hotel_info(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try to find the score and reviews in different possible structures
    score_element = soup.find('div', class_='ac4a7896c7')
    reviews_element = soup.find('div', class_='abf093bdfe f45d8e4c32 d935416c47')

    # Assign default values
    score = 0.0
    reviews = 0

    # Check for score in both structures
    if score_element:
        score_text = score_element.text.strip()
        score_matches = re.findall(r'\d+\.\d+|\d+', score_text)  # Find both floats and integers
        if score_matches:
            score = float(score_matches[-1])  # Get the last numeric value (float or int)
    
    # Check for reviews in both structures
    if reviews_element:
        reviews_text = reviews_element.text.strip().split()[0].replace(',', '')
        if reviews_text:
            reviews = int(reviews_text)  # Remove commas before converting to int

    # Additional checks for nested elements
    if not score:
        # Try to find other structures if the previous ones failed
        nested_score_element = soup.find('div', class_='a3b8729ab1')

        if nested_score_element:
            score_text = nested_score_element.text.strip()
            score_matches = re.findall(r'\d+\.\d+|\d+', score_text)  # Find both floats and integers
            if score_matches:
                score = float(score_matches[-1])
    
    print(score, reviews)
    return score, reviews

# Load the Excel file
df = pd.read_excel('deduplicated_updated_without_score.xlsx')  # Replace with your file
df['Score'] = None  # Initialize the Score column
df['Reviews'] = None  # Initialize the Reviews column

try:
    # Loop through the links and scrape data
    for index, row in df.iterrows():
        link = row['Link']  # Adjust column name as needed
        hotel_info = scrape_hotel_info(link)
        if hotel_info:
            score, reviews = hotel_info
            df.at[index, 'Score'] = score
            df.at[index, 'Reviews'] = reviews
        print(f"Processed {index + 1}/{len(df)} links.")
        
except KeyboardInterrupt:
    # Save the updated DataFrame to a new Excel file on Ctrl+C
    df.to_excel('B&B_with_score_partial.xlsx', index=False)  # Save partial data
    print("\nData saved. Exiting program.")
    sys.exit(0)

# Save the updated DataFrame to a new Excel file at the end
df.to_excel('B&B_with_score.xlsx', index=False)  # Replace with your desired output file name
print("Data scraping complete. Final data saved.")