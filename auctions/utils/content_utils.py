# auctions/content_utils.py

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
    
def cyrillic_to_latin():
    """
    Returns a dictionary mapping Serbian Cyrillic characters to their Latin equivalents.
    Includes both uppercase and lowercase letters.
    """
    return {
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Ђ': 'Đ', 'Е': 'E',
        'Ж': 'Ž', 'З': 'Z', 'И': 'I', 'Ј': 'J', 'К': 'K', 'Л': 'L', 'Љ': 'Lj',
        'М': 'M', 'Н': 'N', 'Њ': 'Nj', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S',
        'Т': 'T', 'Ћ': 'Ć', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'C', 'Ч': 'Č',
        'Џ': 'Dž', 'Ш': 'Š',
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'ђ': 'đ', 'е': 'e',
        'ж': 'ž', 'з': 'z', 'и': 'i', 'ј': 'j', 'к': 'k', 'л': 'l', 'љ': 'lj',
        'м': 'm', 'н': 'n', 'њ': 'nj', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's',
        'т': 't', 'ћ': 'ć', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'č',
        'џ': 'dž', 'ш': 'š'
    }

def transliterate_text(text):
    """
    Transliterate Serbian Cyrillic text to Latin script.
    
    Args:
        text (str): Text in Serbian Cyrillic
        
    Returns:
        str: Text converted to Serbian Latin script
    """
    mapping = cyrillic_to_latin()
    result = []
    i = 0
    while i < len(text):
        # Check for special cases (Љ/Њ/Џ)
        if i + 1 < len(text):
            two_char = text[i:i+2]
            if two_char in mapping:
                result.append(mapping[two_char])
                i += 2
                continue
        
        # Handle single characters
        char = text[i]
        result.append(mapping.get(char, char))
        i += 1
        
    return ''.join(result)

def is_cyrillic(text):
    """
    Check if text contains Cyrillic characters.
    Returns True if the text contains any Cyrillic characters, False otherwise.
    """
    cyrillic_range = range(0x0400, 0x04FF + 1)  # Unicode range for Cyrillic
    return any(ord(char) in cyrillic_range for char in text)

def latin_to_cyrillic(text):
    """
    Convert Serbian Latin text to Cyrillic.
    This mapping covers Serbian-specific characters.
    """
    mapping = {
        'A': 'А', 'B': 'Б', 'V': 'В', 'G': 'Г', 'D': 'Д', 'Đ': 'Ђ', 'E': 'Е', 
        'Ž': 'Ж', 'Z': 'З', 'I': 'И', 'J': 'Ј', 'K': 'К', 'L': 'Л', 'Lj': 'Љ',
        'M': 'М', 'N': 'Н', 'Nj': 'Њ', 'O': 'О', 'P': 'П', 'R': 'Р', 'S': 'С',
        'T': 'Т', 'Ć': 'Ћ', 'U': 'У', 'F': 'Ф', 'H': 'Х', 'C': 'Ц', 'Č': 'Ч',
        'Dž': 'Џ', 'Š': 'Ш',
        'a': 'а', 'b': 'б', 'v': 'в', 'g': 'г', 'd': 'д', 'đ': 'ђ', 'e': 'е',
        'ž': 'ж', 'z': 'з', 'i': 'и', 'j': 'ј', 'k': 'к', 'l': 'л', 'lj': 'љ',
        'm': 'м', 'n': 'н', 'nj': 'њ', 'o': 'о', 'p': 'п', 'r': 'р', 's': 'с',
        't': 'т', 'ć': 'ћ', 'u': 'у', 'f': 'ф', 'h': 'х', 'c': 'ц', 'č': 'ч',
        'dž': 'џ', 'š': 'ш'
    }
    
    # Handle special digraphs first
    text = text.replace('Lj', 'Љ').replace('lj', 'љ')
    text = text.replace('Nj', 'Њ').replace('nj', 'њ')
    text = text.replace('Dž', 'Џ').replace('dž', 'џ')
    
    # Convert remaining characters
    result = ''
    i = 0
    while i < len(text):
        char = text[i]
        if char in mapping:
            result += mapping[char]
        else:
            result += char
        i += 1
        
    return result