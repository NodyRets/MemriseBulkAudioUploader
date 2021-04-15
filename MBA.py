import argparse
import gtts
import requests
from lxml import html
import tempfile
import json

cookies = {}

def parse_cookies():
	f = open("cookies.txt", "r")
	cookies_json = f.read()
	cookies_json = json.loads(cookies_json)
	for x in cookies_json:
		cookies[x['name']] = x['value']

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
    post_url = "https://decks.memrise.com/ajax/thing/cell/upload_file/"
    response = requests.post(post_url, files=files, cookies=cookies, headers=headers, data=form_data, timeout=60)
    response.raise_for_status()

def get_number_of_pages_in_database(url):
    response = requests.get(url, cookies=cookies)
    response.raise_for_status()
    html_doc = html.fromstring(response.text)
    page_list = html_doc.xpath("//div[contains(@class, 'pagination')]/ul/li")
    if not page_list:
        raise ValueError("Number of pages cannot be found. Please check course url and cookies!")
    if len(page_list) == 1:
        return 1
    return int(page_list[-2].text_content())

def collect_words(url):
    words = []
    response = requests.get(url, cookies = cookies)
    response.raise_for_status()
    tree = html.fromstring(response.text)
    div_elements = tree.xpath("//tr[contains(@class, 'thing')]")
    for div in div_elements:
        thing_id = div.attrib['data-thing-id']
        try:
            lang_word = div.xpath("td[2]/div/div/text()")[0]
        except IndexError:
            print("Failed to get the word of item with id " + str(thing_id) + ' on ' + str(database_page_url))
            continue
        column_number_of_audio = div.xpath("td[contains(@class, 'audio')]/@data-key")[0]
        audio_files = div.xpath("td[contains(@class, 'audio')]/div/div[contains(@class, 'dropdown-menu')]/div")
        number_of_audio_files = len(audio_files)
        words.append({'thing_id': thing_id, 'number_of_audio_files': number_of_audio_files, 'lang_word': lang_word, 'column_number_of_audio': column_number_of_audio})
    return words

def upload_audios_for_words(url, audios):
    for audio in audios:
        if audio['number_of_audio_files'] > 0:
            continue
        tts = gtts.gTTS(audio['lang_word'], lang=language)
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3')
        temp_file.close()
        tts.save(temp_file.name)
        upload_file_to_server(audio['thing_id'], audio['column_number_of_audio'], url, temp_file)
        print(audio['lang_word'] + ' succeeded')

if __name__ == "__main__":
    languages = gtts.lang.tts_langs()
    parser = argparse.ArgumentParser(description='This script uploads all missing audio files to the Memrise course')
    parser.add_argument('--language', choices=[*languages], metavar='lang-code', required=True, help='Specifies language for which audio will be downloaded.  Supported languages: ' + ', '.join([*languages]))
    parser.add_argument('--url', required=True, help='Memrise course database url. For example: https://www.memrise.com/course/1234567/my-memrise-english-course/edit/database/7654321/')

    args = parser.parse_args()
    language = args.language
    url = args.url

    if not language in languages:
        raise ValueError("Entered language: " + language + " is not supported!")
    
    parse_cookies()
    number_of_pages = get_number_of_pages_in_database(url)

    for page_number in range(1, number_of_pages + 1):
        database_page_url = url + '?page=' + str(page_number)
        audios = collect_words(database_page_url)
        upload_audios_for_words(database_page_url, audios)
