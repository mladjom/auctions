# auctions/content_utils.py

def cyrillic_to_latin(text):
    """
    Convert Cyrillic text to Latin alphabet for slugs
    """
    cyrillic_to_latin_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'ђ': 'dj',
        'е': 'e', 'ж': 'z', 'з': 'z', 'и': 'i', 'ј': 'j', 'к': 'k',
        'л': 'l', 'љ': 'lj', 'м': 'm', 'н': 'n', 'њ': 'nj', 'о': 'o',
        'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'ћ': 'c', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'c', 'џ': 'dz', 'ш': 's',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Ђ': 'Dj',
        'Е': 'E', 'Ж': 'Z', 'З': 'Z', 'И': 'I', 'Ј': 'J', 'К': 'K',
        'Л': 'L', 'Љ': 'Lj', 'М': 'M', 'Н': 'N', 'Њ': 'Nj', 'О': 'O',
        'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'Ћ': 'C', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'C', 'Ч': 'C', 'Џ': 'Dz', 'Ш': 'S'
    }
    return ''.join(cyrillic_to_latin_map.get(c, c) for c in text)


def normalize_text(text):
    """
    Normalize text by converting Cyrillic to Latin when needed and handling mixed character sets
    """
    if not text:
        return ''
        
    cyrillic_to_latin_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'ђ': 'dj',
        'е': 'e', 'ж': 'z', 'з': 'z', 'и': 'i', 'ј': 'j', 'к': 'k',
        'л': 'l', 'љ': 'lj', 'м': 'm', 'н': 'n', 'њ': 'nj', 'о': 'o',
        'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'ћ': 'c', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'c', 'џ': 'dz', 'ш': 's',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Ђ': 'Dj',
        'Е': 'E', 'Ж': 'Z', 'З': 'Z', 'И': 'I', 'Ј': 'J', 'К': 'K',
        'Л': 'L', 'Љ': 'Lj', 'М': 'M', 'Н': 'N', 'Њ': 'Nj', 'О': 'O',
        'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'Ћ': 'C', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'C', 'Ч': 'C', 'Џ': 'Dz', 'Ш': 'S'
    }
    
    # Check if text contains any Cyrillic characters
    has_cyrillic = any(char in cyrillic_to_latin_map for char in text)
    
    if has_cyrillic:
        # Convert Cyrillic characters to Latin
        return ''.join(cyrillic_to_latin_map.get(c, c) for c in text)
    else:
        # Text is already in Latin, just return it
        return text