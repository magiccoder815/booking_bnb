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

# List of cities
cities = [
    "Venice", "Verona", "Padova", "Vicenza", "Bassano del Grappa", 
    "Cortina dʼAmpezzo",
    "Milan", "Como", "Bergamo", "Brescia", "Mantova", 
    "Sirmione", "Pavia", "Cremona", "Lecco",
    "Rome", "Tivoli", "Viterbo", "Ostia Antica"
    "Fiumicino", "Gaeta", "Anzio",
    "Florence", "Pisa", "Siena", "Lucca", 
    "Forte dei Marmi", "Viareggio",
    "Naples", "Pompei", "Amalfi", "Sorrento", 
    "Capri", "Ischia", "Procida", "Caserta",
    "Bologna", "Rimini", "Ferrara", "Modena", 
    "Parma", "Ravenna", "Cesenatico", "Riccione",
    "Palermo", "Catania", "Taormina", "Siracusa", 
    "Agrigento", "Cefalù", "Ragusa", "Trapani",
    "Bari", "Lecce", "Alberobello", "Ostuni", 
    "Polignano a Mare", "Monopoli", "Gallipoli", "Otranto",
    "Cinque Terre", "Portofino", "Sanremo", "Alassio",
    "Turin", "Alba", "Asti",
    "Trento", "Bolzano", "Madonna di Campiglio", "Riva del Garda",
    "Olbia", "Cagliari",
    "Ancona", "Urbino", "San Benedetto del Tronto", "Macerata",
    "Perugia",
    "Trieste", "Udine",
    "Aosta", "Courmayeur", "Cervinia", "La Thuile", 
    "Gressoney-Saint-Jean", "Saint Vincent", "Cogne", 
    "Champoluc", "Antey-Saint-André"
]

# Initialize the Chrome driver
options = webdriver.ChromeOptions()
options.add_argument("--lang=en")  # Set language to English
# options.add_argument("--headless")  # Disable headless mode to visually debug if needed
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Create the directory for saving files
output_directory = 'B&B'
os.makedirs(output_directory, exist_ok=True)

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
        print("Sign-in modal dismissed by clicking the close button.")
    except TimeoutException:
        print("Sign-in modal did not appear.")
    except NoSuchElementException:
        print("Sign-in modal close button not found.")
    except Exception as e:
        print(f"Error dismissing the modal: {e}")

for city in cities:
    # Handle special cases for formatted city names and English names
    if city == "Siracusa":
        formatted_city = "Siracusa"
        italian_city = "Syracuse"
    elif city == "Antey-Saint-André":
        formatted_city = "Antey-Saint-Andre"
        italian_city = "Antey-Saint-André"
    elif city == "Cefalù":
        formatted_city = "Cefalu"
        italian_city = "Cefalù"
    else:
        formatted_city = city  # Use the city name as is
        italian_city = city  # Default to the original name

    # Construct the URL
    formatted_city_for_url = formatted_city.replace(" ", "-").replace("ʼ", "")  # Format for URL
    url = f"https://www.booking.com/bed-and-breakfast/city/it/{formatted_city_for_url}.html"
    
    driver.get(url)
    time.sleep(3)  # Allow time for the page to load

    # Click on the "All B&Bs in {english_city}" link
    try:
        all_bbs_link = driver.find_element(By.LINK_TEXT, f"All B&Bs in {italian_city}")
        all_bbs_link.click()
        time.sleep(3)  # Allow time for the new page to load
    except NoSuchElementException:
        print(f"'All B&Bs' link not found for {city}.")
        continue

    # Wait for the sign-in modal and dismiss it
    dismiss_sign_in_modal(driver)

    # Click on the "Bed and Breakfasts" filter
    try:
        bed_and_breakfasts_filter = driver.find_element(By.XPATH, "//div[@data-testid='filters-group-label-content' and contains(text(), 'Bed and Breakfasts')]")
        bed_and_breakfasts_filter.click()
        time.sleep(5)
    except NoSuchElementException:
        print("Bed and Breakfasts filter not found.")
        continue

    # Get the number of properties from the <h1> element
    try:
        h1_element = driver.find_element(By.CSS_SELECTOR, 'h1[aria-label]')
        properties_text = h1_element.get_attribute('aria-label')
        total_properties = int(re.search(r'(\d+) properties found', properties_text).group(1))
        print(f"Total properties found in {city}: {total_properties}")
    except Exception as e:
        print(f"Error retrieving number of properties: {e}")
        continue

    # Scrape hotel names, links, addresses, property types, and city
    hotels = []

    if total_properties <= 25:
        # Scrape exactly that number
        hotel_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="property-card"]')
        print(f"Number of hotels found in {city}: {len(hotel_elements)}")

        for hotel in hotel_elements[:total_properties]:
            link_element = hotel.find_element(By.CSS_SELECTOR, 'a[data-testid="title-link"]')
            name = hotel.find_element(By.CSS_SELECTOR, 'div[data-testid="title"]').text
            link = link_element.get_attribute('href')

            # Scrape address and property type using the defined function
            address, property_type = scrape_address_property(link)

            hotels.append({
                'City': city,
                'Name': name,
                'Property Type': property_type,
                'Address': address,
                'Link': link
            })
    else:
        # Use "Load more results" logic to scrape all hotels
        loaded_hotels = 0

        while loaded_hotels < total_properties:
            # Load more hotels on the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Allow time for content to load

            # Click the "Load more results" button if available
            try:
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[.//span[text()="Load more results"]]'))
                )
                load_more_button.click()
                time.sleep(2)  # Wait for the new results to load
            except Exception as e:
                print("No 'Load more results' button found or an error occurred. Scraping all available hotels.")
                break  # Exit loop if no more button

        # After the loop, scrape all loaded hotels
        hotel_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="property-card"]')
        for hotel in hotel_elements[loaded_hotels:]:
            link_element = hotel.find_element(By.CSS_SELECTOR, 'a[data-testid="title-link"]')
            name = hotel.find_element(By.CSS_SELECTOR, 'div[data-testid="title"]').text
            link = link_element.get_attribute('href')

            # Scrape address and property type using the defined function
            address, property_type = scrape_address_property(link)

            hotels.append({
                'City': city,
                'Name': name,
                'Property Type': property_type,
                'Address': address,
                'Link': link
            })
            loaded_hotels += 1
            
            if loaded_hotels >= total_properties:
                break  # Stop if we have reached the total properties

    # Create a DataFrame for the current city and save it to the B&B folder
    df = pd.DataFrame(hotels)
    file_name = os.path.join(output_directory, f'B&B_{formatted_city}.xlsx')
    df.to_excel(file_name, index=False)
    print(f"Data saved to {file_name}")

# Close the WebDriver
driver.quit()