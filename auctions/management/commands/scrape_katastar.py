import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Scrape data from the Katastar public access page using Selenium"

    def handle(self, *args, **kwargs):
        url = "https://katastar.rgz.gov.rs/eKatastarPublic/PublicAccess.aspx"

        # Set up Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_getOpstinaKO_dropOpstina"))
            )
            
            # Initialize the data structure
            data = {"municipalities": []}
            
            while True:
                try:
                    # Get the municipalities dropdown
                    select_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_getOpstinaKO_dropOpstina"))
                    )
                    select = Select(select_element)
                    total_options = len(select.options)

                    # Skip the first option if it's a placeholder
                    start_index = 1 if select.options[0].get_attribute("value") == "" else 0

                    for index in range(start_index, total_options):
                        # Re-fetch the dropdown before each selection
                        select_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_getOpstinaKO_dropOpstina"))
                        )
                        select = Select(select_element)

                        # Get municipality information
                        municipality_option = select.options[index]
                        municipality_name = municipality_option.text
                        municipality_value = municipality_option.get_attribute("value")

                        # Create municipality entry
                        municipality_entry = {
                            "name": municipality_name,
                            "value": municipality_value,
                            "cadastral_municipalities": []
                        }

                        # Select the municipality
                        select.select_by_index(index)

                        # Wait for the table to update
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH, "//table[@id='ContentPlaceHolder1_getOpstinaKO_GridView']/tbody/tr"))
                        )
                        time.sleep(2)

                        # Extract table rows
                        rows = driver.find_elements(By.XPATH, "//table[@id='ContentPlaceHolder1_getOpstinaKO_GridView']/tbody/tr")

                        # Process cadastral municipalities
                        for row in rows[1:]:  # Skip header row
                            columns = row.find_elements(By.TAG_NAME, "td")
                            if len(columns) >= 2:  # Ensure we have enough columns
                                cadastral_entry = {
                                    "name": columns[1].text.strip(),  # Name is in second column
                                    "value": columns[2].text.strip()  # Value/code is in first column
                                }
                                municipality_entry["cadastral_municipalities"].append(cadastral_entry)

                        # Add municipality to the main data structure
                        data["municipalities"].append(municipality_entry)
                        
                        self.stdout.write(f"Processed municipality: {municipality_name}")

                    # Exit loop after processing all options
                    break

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"An error occurred during processing: {e}"))
                    break

            # Save the data to a JSON file
            with open('katastar_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.stdout.write(self.style.SUCCESS("Data successfully saved to katastar_data.json"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
        finally:
            driver.quit()