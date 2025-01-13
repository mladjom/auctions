from django.shortcuts import render

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

# Example usage with a web framework (Django)
from django.shortcuts import redirect

def language_redirect(request, path=''):
    """
    View to handle language/script switching.
    Add to urls.py: path('lat/<path:path>', views.language_redirect)
    """
    if request.path.startswith('/sr/'):
        # Convert the content and metadata to Latin script
        # This is a basic example - you'll need to adapt it for your specific needs
        content = request.content  # Get your content here
        latin_content = transliterate_text(content)
        
        # Return the Latin version
        response = render(request, 'your_template.html', {
            'content': latin_content,
            'script': 'lat'
        })
        return response
    
    return redirect(f'/sr/{path}')

# Example middleware to handle script selection
class ScriptMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if we're requesting Latin script
        if request.path.startswith('/lat/'):
            request.script = 'lat'
        else:
            request.script = 'cyr'
            
        response = self.get_response(request)
        return response