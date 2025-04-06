from django.core.management.base import BaseCommand
import requests
from datetime import datetime
import json

class Command(BaseCommand):
    help = "Fetch data from LIBRIS XL API"

    def add_arguments(self, parser):
        parser.add_argument(
            '--query',
            type=str,
            help='Search query for LIBRIS XL',
            default='Lindgren'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Number of results to fetch',
            default=10
        )

    def handle(self, *args, **options):
        base_url = "https://libris.kb.se/find"
        
        params = {
            'q': options['query'],
            '_limit': options['limit'],
            'format': 'json'
        }

        try:
            self.stdout.write(f"Fetching data for query: {options['query']}")
            response = requests.get(base_url, params=params)
            print(response.url)
            response.raise_for_status()  # Raise exception for bad status codes
            
            data = response.json()
            
            # Save raw response to file for inspection
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'libris_data_{timestamp}.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Process and display results
            if 'items' in data:
                for item in data['items']:
                    title = item.get('title', 'No title')
                    creator = item.get('creator', 'Unknown creator')
                    year = item.get('year', 'Unknown year')
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"Title: {title}\n"
                        f"Creator: {creator}\n"
                        f"Year: {year}\n"
                        f"-------------------"
                    ))
            
            self.stdout.write(self.style.SUCCESS(
                f"\nData saved to {filename}"
            ))

        except requests.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'Error fetching data: {str(e)}')
            )
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'Error parsing JSON response: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {str(e)}')
            )