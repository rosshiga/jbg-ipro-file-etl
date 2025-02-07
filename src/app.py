from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os
import shutil
import time
import re
from datetime import datetime, timedelta
from webdriver_manager.firefox import GeckoDriverManager


# Function to read configuration from config.txt
def load_config(config_file="config.txt"):
    """Load configuration values from a config file."""
    config = {}
    with open(config_file, "r") as file:
        for line in file:
            key, value = line.strip().split("=", 1)
            config[key.strip()] = value.strip()
    return config


# Load configuration
config = load_config()
USERNAME = config.get("USERNAME", "")
PASSWORD = config.get("PASSWORD", "")
DESTINATION_DIRECTORY = config.get("DESTINATION_DIRECTORY", "")
DOWNLOAD_DIRECTORY = config.get("DOWNLOAD_DIRECTORY", "")

# Constants
URL = "https://jbg.partner.iprosystems.com/"
EXPECTED_TITLE = "Log in"
IMPLICIT_WAIT_TIME = 10
PAGE_LOAD_TIMEOUT = 20
EXPLICIT_WAIT_TIME = 10


def setup_driver():
    """Initialize and return a configured Selenium WebDriver instance."""
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    driver.implicitly_wait(IMPLICIT_WAIT_TIME)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver


def extract_file_names(driver):
    """Extract file names from the table and store them in a dictionary."""
    file_names = {}
    try:
        table_rows = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
            EC.presence_of_all_elements_located((By.XPATH, "//table/tbody/tr"))
        )
        time.sleep(1)
        for index, row in enumerate(table_rows, start=1):
            try:
                file_name_element = row.find_element(By.XPATH, "./td[2]")  # File name in second column
                file_name = file_name_element.text.strip()
                if file_name:
                    # Special case: Remove text outside parentheses if filename doesn't contain .csv
                    if not file_name.lower().endswith(".csv") and "(" in file_name and ")" in file_name:
                        match = re.search(r"\((.*?)\)", file_name)
                        if match:
                            file_name = match.group(1)
                    file_names[file_name] = row
            except Exception as e:
                print(f"Error extracting file name from row {index}: {e}")
                continue
    except Exception as e:
        print(f"Error extracting file names: {e}")
    return file_names


def download_missing_files(file_names):
    """Iterate through file names and download missing files. Return list of missing files."""
    missing_files = []
    for file_name, row in file_names.items():
        file_path = os.path.join(DESTINATION_DIRECTORY, file_name)
        if os.path.exists(file_path):
            print(f"File '{file_name}' already exists in destination. Skipping download.")
        else:
            print(f"File '{file_name}' not found. Initiating download...")
            try:
                row.find_element(By.XPATH, "./td[2]").click()
                print(f"Clicked to download '{file_name}'.")
                missing_files.append(file_name)
                time.sleep(2)  # Delay after initiating download
            except Exception as e:
                print(f"Error clicking to download '{file_name}': {e}")
    return missing_files


def move_downloaded_files(missing_files):
    """Move or copy only the missing downloaded files to the destination directory."""
    for file_name in missing_files:
        source_path = os.path.join(DOWNLOAD_DIRECTORY, file_name)
        destination_path = os.path.join(DESTINATION_DIRECTORY, file_name)

        if file_name.lower().endswith(".csv"):
            attempts = 0
            while attempts < 3:
                try:
                    if os.path.exists(source_path):
                        shutil.move(source_path, destination_path)
                        print(f"Moved '{file_name}' to destination.")
                        break
                    else:
                        print(f"File '{file_name}' not found in downloads. Retrying... ({attempts + 1}/3)")
                        time.sleep(5)
                        attempts += 1
                except Exception as e:
                    print(f"Error moving '{file_name}': {e}")
                    break
        else:
            print(f"Searching for a file containing '{file_name}' in recent downloads...")
            recent_files = [f for f in os.listdir(DOWNLOAD_DIRECTORY)
                            if os.path.isfile(os.path.join(DOWNLOAD_DIRECTORY, f)) and
                            datetime.fromtimestamp(
                                os.path.getmtime(os.path.join(DOWNLOAD_DIRECTORY, f))) > datetime.now() - timedelta(
                    hours=1)]

            matching_files = [f for f in recent_files if re.search(re.escape(file_name), f)]
            if matching_files:
                best_match = matching_files[0]
                shutil.copy(os.path.join(DOWNLOAD_DIRECTORY, best_match),
                            os.path.join(DESTINATION_DIRECTORY, file_name+'.csv'))
                print(f"Copied '{best_match}' to '{file_name}'.csv in destination.")


def main():
    """Main function to run the Selenium automation."""
    driver = setup_driver()

    try:
        driver.get(URL)
        WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
            EC.title_contains(EXPECTED_TITLE)
        )
        assert EXPECTED_TITLE in driver.title, f"Expected title '{EXPECTED_TITLE}' not found in page title '{driver.title}'"
        print("Test Passed: Page title is correct.")

        username_field = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.clear()
        username_field.send_keys(USERNAME)
        username_field.send_keys(Keys.RETURN)
        print(f"Entered username: {USERNAME}")

        password_field = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        password_field.clear()
        password_field.send_keys(PASSWORD)
        password_field.send_keys(Keys.RETURN)
        print("Entered password and pressed Return.")

        time.sleep(7)

        file_names = extract_file_names(driver)
        missing_files = download_missing_files(file_names)

        menu_button = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".mdi-menu"))
        )
        menu_button.click()
        print("Clicked on menu button.")
        time.sleep(1)  # Adding 1 second delay after clicking menu

        logout_button = WebDriverWait(driver, EXPLICIT_WAIT_TIME).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".v-btn__content > span"))
        )
        webdriver.ActionChains(driver).move_to_element(logout_button).perform()
        print("Hovered over logout button.")

        logout_button.click()
        print("Clicked on logout button.")

        move_downloaded_files(missing_files)

    except Exception as e:
        print(f"Error encountered: {e}")

    finally:
        driver.quit()
        print("WebDriver session closed.")


if __name__ == "__main__":
    main()
    time.sleep(5)
    print("Developed by Okimotocorp.com - https://github.com/rosshiga/jbg-ipro-file-etl")
