import argparse
import gtts

languages = gtts.lang.tts_langs()
language_help = 'Specifies language for which audio will be downloaded. Supported formats: \n'

for code, lang in languages.items():
    language_help = language_help + code + " : " + lang + '\n'


parser = argparse.ArgumentParser(description='This script uploads all missing audio files to the Memrise course')
parser.add_argument('--language', choices=[*languages], metavar='', help='Specifies language for which audio will be downloaded.  Supported languages: ' + ', '.join([*languages]))

args = parser.parse_args()

language = args.language
print(language)
