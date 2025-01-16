import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time
import re
# ***************************
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import ElementClickInterceptedException

load_dotenv()
time.sleep(5)

GOOGLE_EDIT_FORMS_URL = os.environ["GOOGLE_EDIT_FORMS_URL"]
GOOGLE_FORMS_URL = os.environ["GOOGLE_FORMS_URL"]
ZILLOW_URL = os.environ["ZILLOW_URL"]

LISTINGS_URL_LIST = []
LISTINGS_PRICES_LIST = []
LISTINGS_ADDRESSES_LIST = []


# ***********************************

def reformat_address(addr):
    modified_address = "Your Mom's house..."

    # Define multiple regular expression patterns to match different address formats
    patterns = [
        re.compile(r'(\d{1,5} \w+ \w+),? (\w+),? (\w{2}) (\d{5})'),
        # Standard format
        re.compile(r'(\d{1,5} \w+ \w+), (\d{1,5} \w+ \w+), (\w+), (\w{2}) (\d{5})'),
        # Two street addresses
        re.compile(r'(\w+ \w+), (\d{1,5} \w+ \w+), (\w+), (\w{2}) (\d{5})'),
        # Named place, street address
        re.compile(r'(\w+ \w+), (\d{1,5} \w+ \w+), (\w+), (\w{2})'),
        # Named place, street address without ZIP
        re.compile(r'(\d{1,5} \w+ \w+), (\w+), (\w{2})')
        # Street address without ZIP
        ]
    for pattern in patterns:
        match = pattern.search(addr)

        if match:
            groups = match.groups()

            if len(groups) == 5:
                street, city, state, zip_code = groups[1], groups[2], groups[3], groups[4]
                modified_address = f"{street}, {city}, {state} - {zip_code}".strip(' -')

            elif len(groups) == 4:
                street, city, state, zip_code = groups[0], groups[1], groups[2], groups[3]
                modified_address = f"{street}, {city}, {state} - {zip_code}".strip(' -')

            elif len(groups) == 3:
                street, city, state = groups[0], groups[1], groups[2]
                zip_code = ''
                modified_address = f"{street}, {city}, {state} - {zip_code}".strip(' -')

            return modified_address

    # Handle cases where the address format is different
    parts = addr.split(',')

    if len(parts) >= 3:
        street = parts[0].strip()
        city = parts[1].strip()
        state_zip = parts[2].strip().split()

        if len(state_zip) == 2:
            state = state_zip[0]
            zip_code = state_zip[1]
            modified_address = f"{street}, {city}, {state} - {zip_code}"

        else:
            state = state_zip[0]
            zip_code = "UNKNOWN"
            modified_address = f"{street}, {city}, {state} - {zip_code}"

    return modified_address

# ***********************************


# Get all HTML from the empire website url👇
response = requests.get(ZILLOW_URL)
zillow_page = response.text

# Create BeautifulSoup scraper Object
soup = BeautifulSoup(zillow_page, "html.parser")

# Manage <a> to get 'href' from each, then '.append' them to GLOBAL list
a_tags = soup.select(".StyledPropertyCardDataWrapper a")
for tag in a_tags:
    link = tag.get("href")
    LISTINGS_URL_LIST.append(link)

# Manage the <span> containing the listings' prices, reformat the 'price'
# string, '.append' to GLOBAL list
prices = soup.select(".PropertyCardWrapper span")
for price in prices:
    price_text = price.get_text()
    # Use regex to extract only the numeric part of the price
    cleaned_price = re.sub(r'[^\d]', '', price_text.split('+')[0])
    formatted_price = "${:,.2f}".format(float(cleaned_price))
    LISTINGS_PRICES_LIST.append(formatted_price)


addresses = soup.select(".StyledPropertyCardDataWrapper address")
all_addresses = [address.get_text().replace(" | ", " ").strip() for address in addresses]
for dress in all_addresses:
    formatted_address = reformat_address(dress)
    LISTINGS_ADDRESSES_LIST.append(formatted_address)

# ****************************************************

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

# Iterate over the lists and input the data into the form
for i in range(len(LISTINGS_URL_LIST)):
    #  get the 'Google Form'
    driver.get(GOOGLE_FORMS_URL)
    # Add a delay to allow the page to load
    time.sleep(15)

    # Find all input elements of type 'text' with the specified class
    inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"].whsOnd.zHQkBf')

    # Add a delay
    time.sleep(8)

    inputs[0].send_keys(LISTINGS_ADDRESSES_LIST[i])
    inputs[1].send_keys(LISTINGS_PRICES_LIST[i])
    inputs[2].send_keys(LISTINGS_URL_LIST[i])

    # Add a delay
    time.sleep(4)

    # Submit the form (assuming there's a submit button)
    submit_button = driver.find_element(By.CSS_SELECTOR, '.uArJ5e.UQuaGc.Y5sE8d.VkkpIf.QvWxOd')
    submit_button.click()
    # Wait for the form to be submitted and the page to reload
    time.sleep(8)


# Once all listings are submitted
# Change the URL using JavaScript
# driver.execute_script(f"window.location.href='{GOOGLE_EDIT_FORMS_URL}'")
#
# # Add a delay to allow the page to load
# time.sleep(15)
#
# # Auto-click the 'Sheets' button to auto-generate a new 'Google Sheet'
# link_to_sheet_button = driver.find_element(By.CSS_SELECTOR, '.uArJ5e.cd29Sd.UQuaGc.kCyAyd.l3F1ye.M9Bg4d')
# link_to_sheet_button.click()
# # Wait for the form to be submitted and the page to reload
# time.sleep(8)

driver.quit()
