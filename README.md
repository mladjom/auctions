# Auctions Platform

A Django-based web application for managing and displaying auction listings with multiple languages support.

## Overview

This platform facilitates the management of online auctions with comprehensive features for categorization, search, and multilingual support (Serbian Cyrillic and Serbian Latin scripts). It includes a scraper that collects auction data from official sources.

## Features

- **Auction Management**: Full CRUD operations for auctions with detailed information
- **Categories & Tags**: Organize auctions by categories and tags
- **Locations**: Geographic organization of auction items
- **Executors**: Track auction enforcement officials
- **Document Management**: Attach and manage documents related to auctions
- **Multilingual Support**: Full support for Serbian (Cyrillic and Latin scripts)
- **Data Scraper**: Automated data collection from external sources
- **Responsive Design**: Mobile-friendly interface using Bootstrap

## Project Structure

The project follows a modular Django architecture:

```
project/
├── auctions/             # Main application
│   ├── admin/            # Admin panel customizations
│   ├── management/       # Management commands (scraper)
│   ├── migrations/       # Database migrations
│   ├── models/           # Database models
│   ├── templates/        # HTML templates
│   ├── utils/            # Utility functions
│   └── views/            # View functions
├── config/               # Project configuration
├── locale/               # Translation files
├── templates/            # Global templates
└── pages/                # Static pages application
```

## Models

The application's core models include:

- **Auction**: Main auction entity with details and relationships
- **Category**: Classification of auctions
- **Tag**: Labeling and grouping auctions
- **Executor**: Officials responsible for auctions
- **Location**: Geographic information
- **AuctionDocument**: Files associated with auctions
- **Image**: Pictures for auctions

## Installation

1. Clone the repository:
```bash
git clone git@github.com:mladjom/auctions.git
cd auctions
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup the database:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Data Scraping

The platform includes a data scraper that collects auction data from external sources:

```bash
python manage.py scrape_auctions --pages=2
```

Options:
- `--pages`: Number of pages to scrape (default: 2)
- `--headless`: Run Chrome in headless mode

## Multilingual Support

The platform supports multiple languages with a focus on Serbian Cyrillic and Latin scripts. Language files are located in the `locale/` directory.

To generate or update translation files:

```bash
python manage.py makemessages -l sr
python manage.py makemessages -l sr_Latn
python manage.py compilemessages
```

## Development

### Settings

The project uses different settings for development and production:

- **Development**: `config/settings/development.py`
- **Production**: `config/settings/production.py`

To switch between environments, set the `DJANGO_SETTINGS_MODULE` environment variable:

```bash
export DJANGO_SETTINGS_MODULE=config.settings.development  # Development
export DJANGO_SETTINGS_MODULE=config.settings.production   # Production
```

### Running Tests

```bash
python manage.py test
```

## Deployment

For production deployment:

1. Set environment variables:
```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
export POSTGRES_DB=your_db_name
export POSTGRES_USER=your_db_user
export POSTGRES_PASSWORD=your_db_password
export POSTGRES_HOST=your_db_host
export POSTGRES_PORT=your_db_port
```

2. Collect static files:
```bash
python manage.py collectstatic
```

3. Deploy using your preferred method (Gunicorn, uWSGI, etc.)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django framework
- TailWind for UI components
- Selenium for web scraping