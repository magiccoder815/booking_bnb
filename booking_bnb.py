from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re
import os
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

# Function to print elapsed time
def print_elapsed_time(start_time):
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

# List of cities
cities = [
    "Rome", "Florence", "Pisa", "Forte dei Marmi", "Viareggio",
    "Naples", "Pompei", "Amalfi", "Sorrento", "Capri", "Ischia",
    "Bologna"
]

# Initialize the Chrome driver
options = webdriver.ChromeOptions()
options.add_argument("--lang=en")  # Set language to English
# options.add_argument("--headless")  # Disable headless mode to visually debug if needed
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Create the directory for saving files
output_directory = 'B&B'
os.makedirs(output_directory, exist_ok=True)

# Record start time
start_time = time.time()

# Function to scrape address and property type
def scrape_address_property(link):
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract address
        address_element = soup.select_one('div[tabindex="0"].a53cbfa6de.f17adf7576')
        address = "N/A"  # Default value
        if address_element:
            address = re.sub(r"(Italy.*)", "Italy", address_element.get_text(strip=True))
        
        # Extract property type
        property_element = soup.select_one('a.bui_breadcrumb__link_masked')
        property_type = "N/A"  # Default value
        if property_element:
            property_text = property_element.get_text(strip=True)
            # Extract property type from the text
            match = re.search(r"\((.*?)\)", property_text)
            if match:
                property_type = match.group(1) 

        return address, property_type
    except Exception as e:
        print(f"Error scraping address and property type for {link}: {e}")
        return "N/A", "N/A"

# Function to wait for the sign-in modal and dismiss it
def dismiss_sign_in_modal(driver):
    try:
        print("Waiting for Sign-in modal to appear...")
        # Wait until the modal is visible
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Dismiss sign-in info."]'))
        )
        close_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Dismiss sign-in info."]')
        close_button.click()
        print("Sign-in modal dismissed.")
    except TimeoutException:
        print("Sign-in modal did not appear.")
    except NoSuchElementException:
        print("Sign-in modal close button not found.")
    except Exception as e:
        print(f"Error dismissing the modal: {e}")

for city in cities:
    # Handle special cases for formatted city names and English names
    formatted_city = city.replace(" ", "-").replace("ʼ", "")  # Format for URL
    italian_city = city  # Default to the original name

    # Construct the URL
    url = f"https://www.booking.com/bed-and-breakfast/city/it/{formatted_city}.html"
    
    driver.get(url)
    time.sleep(3)  # Allow time for the page to load
    print_elapsed_time(start_time)

    # Click on the "All B&Bs in {italian_city}" link
    try:
        all_bbs_link = driver.find_element(By.LINK_TEXT, f"All B&Bs in {italian_city}")
        all_bbs_link.click()
        time.sleep(3)  # Allow time for the new page to load
        print_elapsed_time(start_time)
    except NoSuchElementException:
        print(f"'All B&Bs' link not found for {city}.")
        continue

    # Wait for the sign-in modal and dismiss it
    dismiss_sign_in_modal(driver)

    # Click on the "Bed and Breakfasts" filter
    try:
        bed_and_breakfasts_filter = driver.find_element(By.XPATH, "//div[@data-testid='filters-group-label-content' and contains(text(), 'B&Bs')]")
        bed_and_breakfasts_filter.click()
        time.sleep(5)
    except NoSuchElementException:
        print("B&B filter not found.")
        continue

    # Get the number of properties from the <h1> element
    try:
        # Locate the h1 element containing the properties count
        h1_element = driver.find_element(By.CSS_SELECTOR, 'h1[aria-live="assertive"]')
        properties_text = h1_element.get_attribute('aria-label')
        
        # Use regex to extract the total number of properties
        total_properties = int(re.search(r'(\d{1,3}(?:,\d{3})*)', properties_text).group(1).replace(',', ''))
        
        print(f"Total properties found in {city}: {total_properties}")
        print_elapsed_time(start_time)
    except NoSuchElementException:
        print(f"Total properties header not found for {city}.")
        continue
    except Exception as e:
        print(f"Error extracting total properties for {city}: {e}")

    # Scrape hotel names, links, addresses, property types, and city
    hotels = []

    # Initialize a counter for "Load more results" clicks
    load_more_count = 0

    # Load more results until all are loaded
    while True:
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Allow time for content to load

        try:
            # Attempt to find the "Load more results" button
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[.//span[text()="Load more results"]]'))
            )
            
            # Click the button if it exists
            load_more_button.click()
            load_more_count += 1  # Increment the click counter
            time.sleep(2)  # Wait for new results to load
            print_elapsed_time(start_time)

        except (NoSuchElementException, TimeoutException):
            print("No more 'Load more results' button found or an error occurred.")
            break  # Exit loop if no more button

    # Print the number of times the button was clicked
    print(f"'Load more results' button clicked {load_more_count} times.")

    # After all results are loaded, scrape hotel data
    hotel_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="property-card"]')
    for hotel in hotel_elements:
        link_element = hotel.find_element(By.CSS_SELECTOR, 'a[data-testid="title-link"]')
        name = hotel.find_element(By.CSS_SELECTOR, 'div[data-testid="title"]').text
        link = link_element.get_attribute('href')
        print(f"\nName: {name}")
        # Scrape address and property type using the defined function
        address, property_type = scrape_address_property(link)

        hotels.append({
            'City': city,
            'Name': name,
            'Property Type': property_type,
            'Address': address,
            'Link': link
        })

    # Create a DataFrame for the current city and save it to the B&B folder
    df = pd.DataFrame(hotels)
    file_name = os.path.join(output_directory, f'B&B_{formatted_city}.xlsx')
    df.to_excel(file_name, index=False)
    print(f"Data saved to {file_name}")
    print_elapsed_time(start_time)

# Close the WebDriver
driver.quit()

# Final elapsed time
print_elapsed_time(start_time)