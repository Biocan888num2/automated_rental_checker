import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

load_dotenv()
time.sleep(5)

GOOGLE_EDIT_FORMS_URL = os.environ["GOOGLE_EDIT_FORMS_URL"]

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

# Once all listings are submitted
# Change the URL using JavaScript
driver.execute_script(f"window.location.href='{GOOGLE_EDIT_FORMS_URL}'")

# Add a delay to allow the page to load
time.sleep(15)

# Auto-click the 'Sheets' button to auto-generate a new 'Google Sheet'
link_to_sheet_button = driver.find_element(By.CSS_SELECTOR, '.uArJ5e.cd29Sd.UQuaGc.kCyAyd.l3F1ye.M9Bg4d')
link_to_sheet_button.click()
# Wait for the form to be submitted and the page to reload
time.sleep(8)

driver.quit()