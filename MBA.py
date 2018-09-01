import argparse
import gtts
import requests
from lxml import html
from variables import cookies
import tempfile

def upload_file_to_server(thing_id, cell_id, course, file):
	files = {'f': ('whatever.mp3', open(file.name, 'rb'), 'audio/mp3')}
	form_data = { 
		"thing_id": thing_id, 
		"cell_id": cell_id, 
		"cell_type": "column",
		"csrfmiddlewaretoken": cookies['csrftoken']}
	headers = {
		"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0",
		"referer": course}
	post_url = "https://www.memrise.com/ajax/thing/cell/upload_file/"
	r = requests.post(post_url, files=files, cookies=cookies, headers=headers, data=form_data, timeout=60)

languages = gtts.lang.tts_langs()

parser = argparse.ArgumentParser(description='This script uploads all missing audio files to the Memrise course')
parser.add_argument('--language', choices=[*languages], metavar='', required=True, help='Specifies language for which audio will be downloaded.  Supported languages: ' + ', '.join([*languages]))
parser.add_argument('--url', required=True, help='Memrise course database url. For example: https://www.memrise.com/course/1234567/my-memrise-english-course/edit/database/7654321/')

args = parser.parse_args()
language = args.language
url = args.url

if language in languages:
    number_of_pages = int(html.fromstring(requests.get(url, cookies=cookies).content).xpath("//div[contains(@class, 'pagination')]/ul/li")[-2].text_content())
    for page_number in range(1, number_of_pages):
        audios = []
        database_url = url + '?page=' + str(page_number)
        response = requests.get(database_url, cookies = cookies)
        tree = html.fromstring(response.text)
        div_elements = tree.xpath("//tr[contains(@class, 'thing')]")
        for div in div_elements:
            thing_id = div.attrib['data-thing-id']
            try:
                lang_word = div.xpath("td[2]/div/div/text()")[0]
            except IndexError:
                print("failed to get the word of item with id " + str(thing_id) + ' on ' + str(database_url))
                continue
            column_number_of_audio = div.xpath("td[contains(@class, 'audio')]/@data-key")[0]
            audio_files = div.xpath("td[contains(@class, 'audio')]/div/div[contains(@class, 'dropdown-menu')]/div")
            number_of_audio_files = len(audio_files)
            audios.append({'thing_id': thing_id, 'number_of_audio_files': number_of_audio_files, 'lang_word': lang_word, 'column_number_of_audio': column_number_of_audio})
        for audio in audios:
            if audio['number_of_audio_files'] > 0:
                continue
            else:
                tts = gtts.gTTS(audio['lang_word'], lang=language)
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp3')
                temp_file.close()
                print(temp_file.name)
                tts.save(temp_file.name)
                upload_file_to_server(audio['thing_id'], audio['column_number_of_audio'], database_url, temp_file)
                print(audio['lang_word'] + ' succeeded')