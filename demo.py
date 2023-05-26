from gingerit.gingerit import GingerIt
import googletrans


def check_text(text):
    parser = GingerIt()
    result = parser.parse(text)
    return result['corrections']


# Example usage
sentence = "This is a example sentance with bad grammer and speling."

corrections = check_text(sentence)

for correction in corrections:
    print(f"Message: {correction['definition']}")
    print(f"Suggested correction: {correction['correct']}")
    print(f"Error context: {correction['text']}\n")


print(googletrans.LANGUAGES)

from googletrans import Translator

def translate_to_hindi(text):
    translator = Translator()
    translated = translator.translate(text, src='en', dest='hi')
    return translated.text

english_text = "Hello, how are you?"
hindi_text = translate_to_hindi(english_text)
print(hindi_text)
