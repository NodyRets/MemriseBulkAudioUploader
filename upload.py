import requests
from lxml import html
from lxml.etree import tostring
from gtts import gTTS
cookies = {'_ga': 'GA1.2.848997881.1535397234',
           '_gid': 'GA1.2.1540815386.1535397234',
           'ab.storage.sessionId.81b5a720-d869-44a3-b051-fbf0e709467a': '%7B%22g%22%3A%229c4e9af0-f441-1936-c806-0126e749143d%22%2C%22e%22%3A1535397264300%2C%22c%22%3A1535397234289%2C%22l%22%3A1535397234300%7D',
           'ajs_anonymous_id': '%22404adf7b-fc1f-4198-b24a-c525be3b232e%22',
		   'ajs_group_id': 'null',
		   'ajs_user_id': '6131459',
		   'cookieconsent_status': 'allow',
		   'csrftoken': 'wAqRTcWHFn2tQQWrVohIvEdHS0ON8owypmaixo5MAEDnR0sxKRCY0vRnOXxnVx4I',
           'i18next': 'en',
           'sessionid': 'rulwv22gajx7mx4pmqzxvdf2iv8qxi63a'}
		   


def upload_file_to_server(thing_id, cell_id, course, file):
	files = {'f': ('whatever.mp3', open(file, 'rb'), 'audio/mp3')}
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
	
database_url = 'https://www.memrise.com/course/2028009/niemiecki-lekcje-2/edit/database/3035898/?page=3'
print(database_url)
response = requests.get(database_url, cookies = cookies)
tree = html.fromstring(response.text)
div_elements = tree.xpath("//tr[contains(@class, 'thing')]")
audios = []
for div in div_elements:
	thing_id = div.attrib['data-thing-id']
	try:
		german_word = div.xpath("td[2]/div/div/text()")[0]
	except IndexError:
		print("failed to get the word of item with id " + str(thing_id) + ' on ' + str(database_url))
		continue
	column_number_of_audio = div.xpath("td[contains(@class, 'audio')]/@data-key")[0]
	audio_files = div.xpath("td[contains(@class, 'audio')]/div/div[contains(@class, 'dropdown-menu')]/div")
	number_of_audio_files = len(audio_files)
	audios.append({'thing_id': thing_id, 'number_of_audio_files': number_of_audio_files, 'german_word': german_word, 'column_number_of_audio': column_number_of_audio})
print(audios)
#upload_file_to_server('194467457', 3, database_url, 'Kirschen.mp3')
cnt = 1
for audio in audios:
	if audio['number_of_audio_files'] > 0:
		continue
	else:
		#requests.post('http://soundoftext.com/sounds', data={'text':audio['chinese_word'], 'lang':'zh-CN'}) # warn the server of what file I'm going to need
		#temp_file = download_audio('http://soundoftext.com/static/sounds/zh-CN/' + audio['chinese_word'] + '.mp3') #download audio file
		#if isinstance(temp_file, str):
		#	print(audio['chinese_word'] + ' skipped: ' + temp_file)
		#	continue
		#else:
		tts = gTTS(audio['german_word'], lang='de')
		temp_file = str(cnt) + '.mp3'
		tts.save(temp_file)
		cnt = cnt + 1
		upload_file_to_server(audio['thing_id'], audio['column_number_of_audio'], database_url, temp_file)
		print(audio['german_word'] + ' succeeded')