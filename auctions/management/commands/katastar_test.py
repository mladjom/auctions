import json
import time
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

        all_data = []

        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_getOpstinaKO_dropOpstina"))
            )

            # Locate the select element
            select_element = driver.find_element(By.ID, "ContentPlaceHolder1_getOpstinaKO_dropOpstina")
            options = select_element.find_elements(By.TAG_NAME, "option")

            while True:
                try:
                    # Dynamically get the total number of options
                    select_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_getOpstinaKO_dropOpstina"))
                    )
                    select = Select(select_element)
                    total_options = len(select.options)

                    for index in range(total_options):
                        # Re-fetch the dropdown before each selection
                        select_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_getOpstinaKO_dropOpstina"))
                        )
                        select = Select(select_element)

                        # Get the current option text and value
                        municipality_name = select.options[index].text.strip()
                        municipality_value = select.options[index].get_attribute("value").strip()

                        # Select the option by index
                        select.select_by_index(index)

                        # Wait for the table to update
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH, "//table[@id='ContentPlaceHolder1_getOpstinaKO_GridView']/tbody/tr"))
                        )
                        time.sleep(2)

                        # Extract table rows
                        rows = driver.find_elements(By.XPATH, "//table[@id='ContentPlaceHolder1_getOpstinaKO_GridView']/tbody/tr")

                        # Prepare the municipality data structure
                        municipality_info = {
                            "name": municipality_name,
                            "value": municipality_value,
                            "cadastral_municipalities": []
                        }

                        # Skip the header row and process data
                        for row in rows[1:]:
                            columns = row.find_elements(By.TAG_NAME, "td")
                            cadastral_name = columns[1].text.strip()
                            cadastral_value = columns[2].text.strip()

                            # Add cadastral municipality to the list
                            municipality_info["cadastral_municipalities"].append({
                                "name": cadastral_name,
                                "value": cadastral_value
                            })

                        all_data.append(municipality_info)
                        print(f"Processed: {municipality_name}")

                    # Exit loop after processing all options
                    break

                except Exception as e:
                    print(f"An error occurred during processing: {e}")
                    break

            # Save the result as a JSON file
            with open("municipalities_data.json", "w", encoding="utf-8") as f:
                json.dump({"municipalities": all_data}, f, ensure_ascii=False, indent=4)

            self.stdout.write(self.style.SUCCESS("Scraping completed and data saved to 'municipalities_data.json'"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
        finally:
            driver.quit()
