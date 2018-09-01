import argparse
import gtts

languages = gtts.lang.tts_langs()

parser = argparse.ArgumentParser(description='This script uploads all missing audio files to the Memrise course')
parser.add_argument('--language', choices=[*languages], metavar='', required=True, help='Specifies language for which audio will be downloaded.  Supported languages: ' + ', '.join([*languages]))
parser.add_argument('--url', required=True, help='Memrise course database url. For example: https://www.memrise.com/course/1234567/my-memrise-english-course/edit/database/7654321/')

args = parser.parse_args()

language = args.language
print(language)
