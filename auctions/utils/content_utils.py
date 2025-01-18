# auctions/content_utils.py

class SerbianTextConverter:
    """
    A utility class for handling Serbian text conversions between Cyrillic and Latin scripts.
    """
    
    # Single source of truth for character mappings
    CYRILLIC_TO_LATIN = {
        # Uppercase
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Ђ': 'Đ', 'Е': 'E',
        'Ж': 'Ž', 'З': 'Z', 'И': 'I', 'Ј': 'J', 'К': 'K', 'Л': 'L', 'Љ': 'Lj',
        'М': 'M', 'Н': 'N', 'Њ': 'Nj', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S',
        'Т': 'T', 'Ћ': 'Ć', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'C', 'Ч': 'Č',
        'Џ': 'Dž', 'Ш': 'Š',
        # Lowercase
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'ђ': 'đ', 'е': 'e',
        'ж': 'ž', 'з': 'z', 'и': 'i', 'ј': 'j', 'к': 'k', 'л': 'l', 'љ': 'lj',
        'м': 'm', 'н': 'n', 'њ': 'nj', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's',
        'т': 't', 'ћ': 'ć', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'č',
        'џ': 'dž', 'ш': 'š'
    }

    # Precompute the reverse mapping for Latin to Cyrillic
    LATIN_TO_CYRILLIC = {v: k for k, v in CYRILLIC_TO_LATIN.items()}

    # Special digraphs that need to be handled first
    LATIN_DIGRAPHS = [
        ('Lj', 'Љ'), ('lj', 'љ'),
        ('Nj', 'Њ'), ('nj', 'њ'),
        ('Dž', 'Џ'), ('dž', 'џ')
    ]

    # Simplified mapping for URL-safe conversions
    URL_SAFE_MAPPING = {
        'đ': 'dj', 'ђ': 'dj', 'ж': 'z', 'з': 'z', 'ћ': 'c',
        'ц': 'c', 'ч': 'c', 'џ': 'dz', 'ш': 's',
        'Đ': 'Dj', 'Ж': 'Z', 'З': 'Z', 'Ћ': 'C',
        'Ц': 'C', 'Ч': 'C', 'Џ': 'Dz', 'Ш': 'S'
    }

    @classmethod
    def is_cyrillic(cls, text: str) -> bool:
        """Check if text contains any Cyrillic characters."""
        if not text:
            return False
        return any(char in cls.CYRILLIC_TO_LATIN for char in text)

    @classmethod
    def is_latin(cls, text: str) -> bool:
        """Check if text contains any Latin characters."""
        if not text:
            return False
        return any(char in cls.LATIN_TO_CYRILLIC for char in text)
    
    @classmethod
    def to_latin(cls, text: str) -> str:
        """Convert text from Cyrillic to Latin script."""
        if not text:
            return ''

        result = text
        # Handle digraphs first (if input is Cyrillic)
        if cls.is_cyrillic(text):
            return ''.join(cls.CYRILLIC_TO_LATIN.get(char, char) for char in text)
        return result

    @classmethod
    def to_cyrillic(cls, text: str) -> str:
        """Convert text from Latin to Cyrillic script."""
        if not text:
            return ''

        result = text
        # Handle digraphs first
        for latin, cyrillic in cls.LATIN_DIGRAPHS:
            result = result.replace(latin, cyrillic)

        # Convert remaining characters
        return ''.join(cls.LATIN_TO_CYRILLIC.get(char, char) for char in result)

    @classmethod
    def normalize(cls, text: str) -> str:
        """
        Normalize text for URLs and slugs by converting to Latin and simplifying characters.
        """
        if not text:
            return ''

        # First convert to Latin if it's Cyrillic
        latin_text = cls.to_latin(text)

        # Then apply URL-safe conversions
        for char, replacement in cls.URL_SAFE_MAPPING.items():
            latin_text = latin_text.replace(char, replacement)

        return latin_text.lower()

    @staticmethod
    def generate_unique_slug(source_text: str, model_class, existing_instance=None) -> str:
        """
        Generate a unique slug for any Django model instance.
        
        Args:
            source_text (str): The text to generate the slug from
            model_class: The Django model class
            existing_instance: Optional existing model instance (for updates)
            
        Returns:
            str: A unique slug for the model
        """
        from django.utils.text import slugify
        
        # Handle empty source text
        if not source_text:
            base_slug = f"unnamed-{model_class.__name__.lower()}"
        else:
            # Normalize and slugify the text
            normalized_text = SerbianTextConverter.normalize(source_text)
            base_slug = slugify(normalized_text)
            
            if not base_slug:
                base_slug = f"unnamed-{model_class.__name__.lower()}"

        # If we're updating an existing instance and its slug starts with our base_slug,
        # we can keep using the same slug
        if existing_instance and existing_instance.slug.startswith(base_slug):
            return existing_instance.slug

        # Query existing objects with this base slug
        existing_slugs = model_class.objects.filter(slug__startswith=base_slug)
        if existing_instance:
            existing_slugs = existing_slugs.exclude(pk=existing_instance.pk)

        if not existing_slugs.exists():
            return base_slug

        # Find the highest number suffix
        max_suffix = 0
        for obj in existing_slugs:
            try:
                suffix = obj.slug.replace(f"{base_slug}-", "")
                if suffix.isdigit():
                    max_suffix = max(max_suffix, int(suffix))
            except (ValueError, AttributeError):
                continue

        # Return new slug with incremented suffix
        return f"{base_slug}-{max_suffix + 1}"
