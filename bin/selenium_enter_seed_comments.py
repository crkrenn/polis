# import time

import os
import sys

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Check if the path to the .env file is provided as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python script.py <path_to_env_file>")
    sys.exit(1)

env_file_path = sys.argv[1]
load_dotenv(dotenv_path=env_file_path)
API_HOSTNAME = os.environ.get('API_HOSTNAME')

url = f'https://{API_HOSTNAME}/'
print(f"Please browse to {url}")

# driver = webdriver.Chrome(executable_path='/opt/homebrew/bin/chromedriver')
driver = webdriver.Chrome()

# Navigate to login page
driver.get(url)

# Wait for the user to manually authenticate
input("Please log in navigate to the correct conversation and then press Enter to continue...")

comments = ["FOO", "BAZ", "QUX"]

for comment in comments:
    textarea = driver.find_element(By.CSS_SELECTOR, 'textarea[data-test-id="seed_form"]')
    textarea.send_keys(comment)

    # Define the locator for the button
    # This works because currently there is only one button on the page
    button_locator = (By.TAG_NAME, 'button')
    # Wait for up to 10 seconds for the button to appear with the text "Submit"
    wait = WebDriverWait(driver, 10)
    wait.until(EC.text_to_be_present_in_element(button_locator, "Submit"))
    button = driver.find_element(*button_locator)
    button.click()

    # Define the locator for the button
    # This works because currently there is only one button on the page
    button_locator = (By.TAG_NAME, 'button')
    # Wait for up to 10 seconds for the button to appear with the text "Success!"
    wait = WebDriverWait(driver, 10)
    wait.until(EC.text_to_be_present_in_element(button_locator, "Success!"))


# Close the driver once done
driver.close()
