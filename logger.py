from bs4 import BeautifulSoup
import requests

payload = {}
s = requests.Session()
r = s.get('https://synergia.librus.pl/loguj')
starting_index = r.text.find('csrfTokenValue = "')
csrf_token = r.text[starting_index + len('csrfTokenValue = "'): starting_index + len('csrfTokenValue = "') + 72]
payload['csrfTokenValue'] = csrf_token
payload['login'] = 'twojlogin'
payload['passwd'] = 'twojehaslo'
payload['csrfTokenName'] = "requestkey"
p = s.post('https://synergia.librus.pl/loguj', data = payload)
print(p.cookies)
print(s.cookies)

