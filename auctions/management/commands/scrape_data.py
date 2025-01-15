from django.core.management.base import BaseCommand
from django.utils import timezone
from auctions.models import (
    Auction,
    Category,
    Tag,
    Executor,
    Location,
    AuctionDocument
)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
from django.db import transaction
from django.utils.text import slugify
from django.utils import timezone
from ...utils.content_utils import SerbianTextConverter
class Command(BaseCommand):
    help = 'Scrapes auction data from eaukcija.sud.rs and populates the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            default=2,
            help='Number of pages to scrape'
        )
        parser.add_argument(
            '--headless',
            action='store_true',
            help='Run Chrome in headless mode'
        )

    def setup_webdriver(self, headless=False):
        service = Service("/usr/bin/chromedriver")
        options = Options()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        return driver

    def wait_for_element_load(self, driver, by, selector, timeout=10):
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )

    def wait_for_url_change(self, driver, old_url):
        def url_changed(driver):
            return driver.current_url != old_url
        WebDriverWait(driver, 10).until(url_changed)

    def parse_price(self, price_str):
        try:
            price_str = price_str.replace("РСД", "").strip()
            price_str = price_str.replace(".", "").replace(",", ".")
            return float(price_str)
        except (ValueError, AttributeError):
            self.stdout.write(self.style.WARNING(f"Error converting price: {price_str}"))
            return None


    def parse_serbian_date(self, date_str):
        serbian_months = {
            'јан': '01', 'феб': '02', 'мар': '03', 'апр': '04',
            'мај': '05', 'јун': '06', 'јул': '07', 'авг': '08',
            'сеп': '09', 'окт': '10', 'нов': '11', 'дец': '12'
        }
        
        date_str = date_str.strip().lower()
        if date_str.endswith('.'):
            date_str = date_str[:-1]
            
        parts = [p.strip() for p in date_str.split('.') if p.strip()]
        
        day = parts[0].zfill(2)
        month = serbian_months[parts[1].strip()]
        year = parts[2]
        
        time_str = "00:00"
        if len(parts) > 3:
            time_str = parts[3]
        
        datetime_str = f"{year}-{month}-{day} {time_str}"
        naive_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        return timezone.make_aware(naive_datetime)
    
    def split_pdf_documents(self, doc_text):
        docs = [d.strip() + '.pdf' for d in doc_text.split('.pdf') if d.strip()]
        return docs


    def get_or_create_category(self, name_sr):
        """
        Get or create a category with both Cyrillic and Latin titles
        """
        if not name_sr:
            return None
        
        # Create Latin version
        name_lat = SerbianTextConverter.to_latin(name_sr)
        
        # Generate slug from Latin version
        slug = SerbianTextConverter.generate_unique_slug(SerbianTextConverter.normalize(name_sr), Category)
        
        # Create or update with both versions
        category, _ = Category.objects.get_or_create(
            title_sr=name_sr,
            defaults={
                'title_lat': name_lat,
                'slug': slug,
                'meta_title_sr': name_sr,
                'meta_title_lat': name_lat,
                'meta_description_sr': name_sr,
                'meta_description_lat': name_lat
            }
        )
        return category

    def get_or_create_executor(self, name_sr):
        """
        Get or create an executor with both Cyrillic and Latin titles,
        handling cases where the input might be in Latin script.
        """
        if not name_sr:
            return None
        
        # Convert to Cyrillic if the input is in Latin
        if not SerbianTextConverter.is_cyrillic(name_sr):
            name_sr = SerbianTextConverter.to_cyrillic(name_sr)
        
        # Create Latin version from the (now definitely) Cyrillic name
        name_lat = SerbianTextConverter.to_latin(name_sr)
        
        # Generate slug from Latin version
        slug = SerbianTextConverter.generate_unique_slug(SerbianTextConverter.normalize(name_sr), Executor)
        
        # Create or update with both versions
        executor, _ = Executor.objects.get_or_create(
            title_sr=name_sr,
            defaults={
                'title_lat': name_lat,
                'slug': slug,
                'meta_title_sr': name_sr,
                'meta_title_lat': name_lat,
                'meta_description_sr': name_sr,
                'meta_description_lat': name_lat
            }
        )
        return executor

    def get_or_create_location(self, location_data):
        """
        Get or create a location with both Cyrillic and Latin titles
        """
        if not location_data:
            return None
        
        # Get location components
        municipality_sr = location_data.get('municipality', '')
        city_sr = location_data.get('city', '')
        cadastral_municipality_sr = location_data.get('cadastral_municipality', '')
        
        # Transliterate components to Latin
        municipality_lat = SerbianTextConverter.to_latin(municipality_sr)
        city_lat = SerbianTextConverter.to_latin(city_sr)
        cadastral_municipality_lat = SerbianTextConverter.to_latin(cadastral_municipality_sr)
        
        # Create combined titles
        name_parts_sr = [municipality_sr, city_sr, cadastral_municipality_sr]
        name_parts_lat = [municipality_lat, city_lat, cadastral_municipality_lat]
        
        title_sr = ' '.join(filter(None, name_parts_sr))
        title_lat = ' '.join(filter(None, name_parts_lat))
        
        # Generate slug from Latin version
        slug = SerbianTextConverter.generate_unique_slug(SerbianTextConverter.normalize(title_sr), Location)
        
        # Create or update with both versions
        location, _ = Location.objects.get_or_create(
            municipality=municipality_sr,
            city=city_sr,
            cadastral_municipality=cadastral_municipality_sr,
            defaults={
                'title_sr': title_sr,
                'title_lat': title_lat,
                'slug': slug,
                'meta_title_sr': title_sr,
                'meta_title_lat': title_lat,
                'meta_description_sr': title_sr,
                'meta_description_lat': title_lat
            }
        )
        return location

    def get_or_create_tags(self, tag_names_sr):
        """
        Get or create tags with both Cyrillic and Latin titles
        """
        tags = []
        for name_sr in tag_names_sr:
            if name_sr:
                # Create Latin version
                name_lat = SerbianTextConverter.to_latin(name_sr)
                
                # Generate slug from Latin version
                slug = SerbianTextConverter.generate_unique_slug(SerbianTextConverter.normalize(name_sr), Tag)
                
                # Create or update with both versions
                tag, _ = Tag.objects.get_or_create(
                    title_sr=name_sr,
                    defaults={
                        'title_lat': name_lat,
                        'slug': slug,
                        'meta_title_sr': name_sr,
                        'meta_title_lat': name_lat,
                        'meta_description_sr': name_sr,
                        'meta_description_lat': name_lat
                    }
                )
                tags.append(tag)
        return tags

    def create_or_update_documents(self, auction, document_names_sr):
        """
        Create or update documents with both Cyrillic and Latin titles
        """
        existing_docs = {doc.title_sr: doc for doc in auction.documents.all()}
        
        # Create new documents
        for name_sr in document_names_sr:
            if name_sr not in existing_docs:
                # Create Latin version
                name_lat = SerbianTextConverter.to_latin(name_sr)
                
                # Generate slug from Latin version
                #slug = SerbianTextConverter.generate_unique_slug(SerbianTextConverter.normalize(name_sr), AuctionDocument)
                
                doc = AuctionDocument.objects.create(
                    title_sr=name_sr,
                    title_lat=name_lat,
                    # slug=slug,
                    # meta_title_sr=name_sr,
                    # meta_title_lat=name_lat,
                    # meta_description_sr=name_sr,
                    # meta_description_lat=name_lat,
                    file=f'auction_documents/{auction.code}/{name_sr}'
                )
                auction.documents.add(doc)
        
        # Remove documents that no longer exist
        for doc_name in existing_docs:
            if doc_name not in document_names_sr:
                auction.documents.remove(existing_docs[doc_name])

    def extract_details(self, driver, auction_code, current_url):
        details = {}
        try:
            self.stdout.write(f"\nStarting to process auction {auction_code}")
            
            detail_url = f"https://eaukcija.sud.rs/#/aukcije/{auction_code}"
            self.stdout.write(f"Navigating to URL: {detail_url}")
            driver.get(detail_url)
            
            try:
                self.wait_for_element_load(driver, By.CLASS_NAME, "auction-info", timeout=20)
                time.sleep(2)
                
                # Extract basic details
                details["code"] = self.wait_for_element_load(driver, By.CLASS_NAME, "auction-list-item__code", timeout=10).text
                details["status"] = self.wait_for_element_load(driver, By.CLASS_NAME, "auction-list-item__status", timeout=10).text
                details["title"] = self.wait_for_element_load(driver, By.CLASS_NAME, "auction-item-title", timeout=10).text
                details["url"] = detail_url

                # Extract detail lines
                detail_lines = driver.find_elements(By.CLASS_NAME, "auction-state-info__line")
                for line in detail_lines:
                    text = line.text
                    if "Датум објаве" in text:
                        date_str = text.split("еАукције")[1].strip()
                        details["publication_date"] = self.parse_serbian_date(date_str)
                    elif "Почетак еАукције" in text:
                        date_str = text.split("еАукције")[1].strip()
                        details["start_time"] = self.parse_serbian_date(date_str)
                    elif "Крај еАукције" in text:
                        date_str = text.split("еАукције")[1].strip()
                        details["end_time"] = self.parse_serbian_date(date_str)
                    elif "Почетна цена" in text:
                        details["pricing"] = details.get("pricing", {})
                        details["pricing"]["starting_price"] = self.parse_price(text.split("Почетна цена")[1].strip())
                    elif "Процењена вредност" in text:
                        details["pricing"] = details.get("pricing", {})
                        details["pricing"]["estimated_value"] = self.parse_price(text.split("Процењена вредност")[1].strip())
                    elif "Лицитациони корак" in text:
                        details["pricing"] = details.get("pricing", {})
                        details["pricing"]["bidding_step"] = self.parse_price(text.split("Лицитациони корак")[1].strip())

                # Process tabs
                additional_info = {}
                tabs = self.wait_for_element_load(driver, By.CLASS_NAME, "ant-tabs-nav", timeout=10).find_elements(By.CLASS_NAME, "ant-tabs-tab")
                
                for tab in tabs:
                    tab_name = tab.text.strip()
                    self.stdout.write(f"Processing tab: {tab_name}")
                    
                    # Click tab with retry
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            driver.execute_script("arguments[0].click();", tab)
                            time.sleep(1)
                            break
                        except Exception as e:
                            if attempt == max_retries - 1:
                                raise
                            time.sleep(1)
                    
                    tab_content = self.wait_for_element_load(driver, By.CLASS_NAME, "ant-tabs-tabpane-active", timeout=10)
                    
                    if tab_name == "Детаљи":
                        detail_lines = tab_content.find_elements(By.CLASS_NAME, "info-label-row")
                        for line in detail_lines:
                            text = line.text.strip()
                            if "Опис:" in text:
                                additional_info["description"] = text.replace("Опис:", "").strip()
                            elif "Продаја:" in text:
                                additional_info["sale_number"] = text.replace("Продаја:", "").strip()
                    
                    elif tab_name == "Локација":
                        location = {}
                        location_lines = tab_content.find_elements(By.CLASS_NAME, "info-label-row")
                        for line in location_lines:
                            text = line.text.strip()
                            if "Општина:" in text:
                                location["municipality"] = text.replace("Општина:", "").strip()
                            elif "Место:" in text:
                                location["city"] = text.replace("Место:", "").strip()
                            elif "Катастарска општина:" in text:
                                location["cadastral_municipality"] = text.replace("Катастарска општина:", "").strip()
                        additional_info["location"] = location
                    
                    elif tab_name == "Категорија":
                        category_element = tab_content.find_element(By.CLASS_NAME, "category-name")
                        additional_info["categories"] = category_element.text.strip()
                    
                    elif tab_name == "Тагови":
                        tags_elements = tab_content.find_elements(By.CLASS_NAME, "category-name")
                        additional_info["tags"] = [tag.text.strip() for tag in tags_elements if tag.text.strip()]
                    
                    elif tab_name == "Јавни извршитељ":
                        executor_element = tab_content.find_element(By.CLASS_NAME, "category-name")
                        additional_info["executor"] = executor_element.text.strip()
                    
                    elif tab_name == "Документи":
                        document_elements = tab_content.find_elements(By.CLASS_NAME, "category-name")
                        doc_text = "".join([doc.text.strip() for doc in document_elements if doc.text.strip()])
                        additional_info["documents"] = self.split_pdf_documents(doc_text)

                details["additional_info"] = additional_info

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error during content extraction: {str(e)}"))
            
            finally:
                self.stdout.write("Returning to listing page...")
                driver.get(current_url)
                self.wait_for_element_load(driver, By.CLASS_NAME, "auction-list-item", timeout=10)
                time.sleep(1)
            
            return details
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Critical error processing auction {auction_code}: {str(e)}"))
            try:
                driver.get(current_url)
                self.wait_for_element_load(driver, By.CLASS_NAME, "auction-list-item", timeout=10)
                time.sleep(1)
            except Exception as nav_error:
                self.stdout.write(self.style.ERROR(f"Error navigating back: {str(nav_error)}"))
            return None

    def extract_auctions_from_page(self, driver):
        auctions = []
        try:
            self.wait_for_element_load(driver, By.CLASS_NAME, "auction-list-item")
            time.sleep(1)
            
            items = driver.find_elements(By.CLASS_NAME, "auction-list-item")
            
            for item in items:
                try:
                    code = item.find_element(By.CLASS_NAME, "auction-list-item__code").text
                    numeric_code = ''.join(filter(str.isdigit, code))
                    auctions.append({"code": code, "numeric_code": numeric_code})
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error extracting item data: {str(e)}"))
                    
            return auctions
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error finding auction items: {str(e)}"))
            return []

    def check_page_has_content(self, driver):
        try:
            self.wait_for_element_load(driver, By.CLASS_NAME, "auction-list-item")
            return True
        except TimeoutException:
            return False

    def navigate_to_page(self, driver, base_url, page_num):
        page_url = f"{base_url}#/?stranica={page_num}"
        current_url = driver.current_url
        driver.get(page_url)
        if current_url != page_url:
            self.wait_for_element_load(driver, By.CLASS_NAME, "auction-list-item")
            time.sleep(2)
        return page_url

    def save_auction_data(self, data):
        try:
            # Get or create related objects
            category = self.get_or_create_category(data['additional_info'].get('categories'))
            executor = self.get_or_create_executor(data['additional_info'].get('executor'))
            location = self.get_or_create_location(data['additional_info'].get('location'))
            
            # Original title (Cyrillic) and description
            title_sr = data['title']
            description_sr = data['additional_info'].get('description', '')
            
            # Convert to Latin script using proper Serbian transliteration
            title_lat = SerbianTextConverter.to_latin(title_sr)
            description_lat = SerbianTextConverter.to_latin(description_sr)
            
            # Generate slug from simplified Latin version (using SerbianTextConverter.normalize to avoid URL issues)
            slug = SerbianTextConverter.generate_unique_slug(SerbianTextConverter.normalize(title_sr), Auction)
            
            # Generate meta fields
            meta_title_sr = f"{title_sr} - еАукција {data['code']}"
            meta_title_lat = f"{title_lat} - eAukcija {data['code']}"
            
            # Create meta descriptions by truncating main descriptions
            meta_description_sr = description_sr[:160] + '...' if len(description_sr) > 160 else description_sr
            meta_description_lat = description_lat[:160] + '...' if len(description_lat) > 160 else description_lat
            
            # Create or update auction
            auction, created = Auction.objects.update_or_create(
                code=data['code'],
                defaults={
                    'slug': slug,
                    'status': data['status'],
                    # Serbian Cyrillic content
                    'title_sr': title_sr,
                    'description_sr': description_sr,
                    'meta_title_sr': meta_title_sr,
                    'meta_description_sr': meta_description_sr,
                    # Serbian Latin content (properly transliterated)
                    'title_lat': title_lat,
                    'description_lat': description_lat,
                    'meta_title_lat': meta_title_lat,
                    'meta_description_lat': meta_description_lat,
                    # Other fields
                    'url': data['url'],
                    'publication_date': data['publication_date'],
                    'start_time': data['start_time'],
                    'end_time': data['end_time'],
                    'starting_price': data['pricing']['starting_price'],
                    'estimated_value': data['pricing']['estimated_value'],
                    'bidding_step': data['pricing']['bidding_step'],
                    'sale_number': data['additional_info'].get('sale_number', ''),
                    'category': category,
                    'executor': executor,
                    'location': location,
                }
            )
            
            # Handle tags and documents
            tags = self.get_or_create_tags(data['additional_info'].get('tags', []))
            auction.tags.set(tags)
            
            self.create_or_update_documents(
                auction,
                data['additional_info'].get('documents', [])
            )
            
            return created
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error saving auction {data['code']}: {str(e)}"))
            raise

    def handle(self, *args, **options):
        driver = self.setup_webdriver(options['headless'])
        try:
            base_url = "https://eaukcija.sud.rs"
            max_pages = options['pages']
            
            created_count = 0
            updated_count = 0
            
            self.stdout.write(self.style.SUCCESS(f"Starting scrape of {max_pages} pages"))
            
            # Loop through the pages and scrape auctions
            for page_num in range(1, max_pages + 1):
                self.stdout.write(self.style.SUCCESS(f"Scraping page {page_num}"))
                
                # Navigate to the page and check if it has content
                page_url = self.navigate_to_page(driver, base_url, page_num)
                
                if not self.check_page_has_content(driver):
                    self.stdout.write(self.style.WARNING(f"No content found on page {page_num}"))
                    continue
                
                # Extract auctions from the page
                auctions = self.extract_auctions_from_page(driver)
                if not auctions:
                    self.stdout.write(self.style.WARNING(f"No auctions found on page {page_num}"))
                    continue
                
                # Process each auction
                for auction in auctions:
                    auction_code = auction['numeric_code']
                    self.stdout.write(self.style.SUCCESS(f"Processing auction {auction_code}"))
                    
                    current_url = driver.current_url
                    auction_details = self.extract_details(driver, auction_code, current_url)
                    
                    if auction_details:
                        created = self.save_auction_data(auction_details)
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                    else:
                        self.stdout.write(self.style.WARNING(f"Failed to extract details for auction {auction_code}"))
            
            self.stdout.write(self.style.SUCCESS(
                f"\nScraping completed:\n"
                f"Created: {created_count} auctions\n"
                f"Updated: {updated_count} auctions"
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during scraping: {str(e)}"))
        finally:
            driver.quit()
