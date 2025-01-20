from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from django.core.management.base import BaseCommand
from selenium.webdriver.support.ui import Select
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Command(BaseCommand):
    help = "Scrape data from the Katastar public access page using Selenium"

    def handle(self, *args, **kwargs):
        url = "https://katastar.rgz.gov.rs/eKatastarPublic/PublicAccess.aspx"

        # Set up Selenium WebDriver
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_getOpstinaKO_dropOpstina"))
            )
            # Example: Get the page title
            page_title = driver.title
            self.stdout.write(self.style.SUCCESS(f"Page Title: {page_title}"))
            
            select_element = driver.find_element(By.ID, "ContentPlaceHolder1_getOpstinaKO_dropOpstina")

            # Extract all <option> elements inside the <select> element
            options = select_element.find_elements(By.TAG_NAME, "option")

            # Print or process the options
            for option in options:
                value = option.get_attribute("value")  # Extract the value attribute
                text = option.text  # Extract the visible text
                self.stdout.write(f"Value: {value}, Text: {text}")            
                
            # Locate the <select> element
            # select = Select(select_element)

            # Prepare a list to store extracted data
            all_data = []
              
            while True:
                try:
                    # Get the total number of options dynamically each time
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

                        # Get the current option text for debugging/logging
                        option_text = select.options[index].text

                        # Select the option by index
                        select.select_by_index(index)

                        # Wait for the table to update
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH, "//table[@id='ContentPlaceHolder1_getOpstinaKO_GridView']/tbody/tr"))
                        )
                        time.sleep(2)

                        # Extract table rows
                        rows = driver.find_elements(By.XPATH, "//table[@id='ContentPlaceHolder1_getOpstinaKO_GridView']/tbody/tr")

                        # Skip the header row and process data
                        for row in rows[1:]:
                            columns = row.find_elements(By.TAG_NAME, "td")
                            row_data = [col.text.strip() for col in columns]
                            all_data.append(row_data)

                        print(f"Processed: {option_text}")

                    # Exit loop after processing all options
                    break

                except Exception as e:
                    print(f"An error occurred during processing: {e}")
                    break

            # Save or process the data
            for row in all_data:
                print(row)                
                

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
        finally:
            driver.quit()
