from __future__ import print_function
import requests
import datetime
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import argparse

user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 ' \
             '(KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36'

CLASS_SCHEDULE = {0: (datetime.time(7, 30, 0), datetime.time(8, 15, 0)),
                  1: (datetime.time(8, 15, 0), datetime.time(9, 0, 0)),
                  2: (datetime.time(9, 10, 0), datetime.time(9, 55, 0)),
                  3: (datetime.time(10, 0, 0), datetime.time(10, 45, 0)),
                  4: (datetime.time(10, 55, 0), datetime.time(11, 40, 0)),
                  5: (datetime.time(11, 50, 0), datetime.time(12, 35, 0)),
                  6: (datetime.time(12, 40, 0), datetime.time(13, 25, 0)),
                  7: (datetime.time(13, 30, 0), datetime.time(14, 15, 0)),
                  8: (datetime.time(14, 25, 0), datetime.time(15, 5, 0)),
                  9: (datetime.time(15, 10, 0), datetime.time(15, 55, 0)),
                  10: (datetime.time(16, 0, 0), datetime.time(16, 45, 0))}

def get_pages(login, password, pages_list):
    s = requests.Session()
    result = s.get('https://synergia.librus.pl/loguj', verify=False, headers={'User-Agent':user_agent})
    data = {'ed_pass_keyup': [''], 'passwd': [password], 'czy_js': ['0'], 'captcha': [''], 'ed_pass_keydown': [''], 'login': [login]}
    result = s.post('https://synergia.librus.pl///loguj', data, verify=False, headers={'Referer': result.url, 'User-Agent': user_agent})
    result.raise_for_status()

    pages_html = []
    for i in pages_list:
        page = s.get(i, verify=False,
                     headers={'Referer': result.url, 'User-Agent': user_agent})
        pages_html.append(page)
    return pages_html, s


def librus_string_to_date(string):
    part1, part2 = string.split(' ')
    part1 = part1.split('-')
    part2 = part2.split(':')
    whole = map(int, part1 + part2)
    return datetime.datetime(*whole)


def is_a_test(tag):
    return tag.name == 'td' and tag.has_attr('title') and tag.has_attr('style') and 'background-color: #FF7878;' not in tag['style']


def parse_events(bs, year, month):
    raw_list = bs.find_all(class_="kalendarz-dzien")
    result = []
    for index, day in enumerate(raw_list):
        event_list = day.find_all(is_a_test)
        for entry in event_list:
            data = {}
            desc = entry['title']
            desc = desc.split('<br />')
            for i in desc:
                data[i[:i.find(':')]] = i[(i.find(':') + 2):]

            if "Nr" in entry.contents[0]:
                data['time'] = CLASS_SCHEDULE[int(entry.contents[0][-1])]
                data["start"] = datetime.datetime.combine(datetime.date(year, month, index + 1),
                                                          data['time'][0]).astimezone()
                data["end"] = datetime.datetime.combine(datetime.date(year, month, index + 1),
                                                          data['time'][1]).astimezone()
            else:
                data['day'] = datetime.date(year, month, index + 1)
            data["subject"] = str(entry.contents[2].text)
            data["type"] = str(entry.contents[3])

            result.append(data)
    return result


def setup_api():
    # Setup the Calendar API
    SCOPES = 'https://www.googleapis.com/auth/calendar'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    return service


def add_events(parsed_events, api_service):
    for entry in parsed_events:
        event = {
            "summary": "{} z {}".format(entry['type'], entry['subject']),
            "description": entry['Opis'],
            "start": {
                "timeZone": "Europe/Warsaw"
            },
            "end": {
                "timeZone": "Europe/Warsaw"
            },
            "reminder": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 60 * 24},
                ]
            }

        }
        if entry.get("time"):
            event["start"]["dateTime"] = entry["start"].isoformat()
            event["end"]["dateTime"] = entry["end"].isoformat()
        else:
            event["start"]["date"] = entry["day"].isoformat()
            event["end"]["date"] = entry["day"].isoformat()
        event = api_service.events().insert(calendarId='primary', body=event).execute()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-l', '--login')
    parser.add_argument('-p', '--password')

    args = parser.parse_args()
    service = setup_api()
    pages = ['https://synergia.librus.pl/przegladaj_oceny/uczen',
             'https://synergia.librus.pl/wiadomosci',
             'https://synergia.librus.pl/przegladaj_nb/uczen',
             'https://synergia.librus.pl/ogloszenia',
             'https://synergia.librus.pl/terminarz']
    result, session = get_pages(args.login, args.password, pages)
    payload = {'miesiac': 3, 'rok': 2018}
    terminarz2 = session.post('https://synergia.librus.pl/terminarz', payload)
    terminarz2.raise_for_status()
    soup = BeautifulSoup(terminarz2.content.decode('utf-8', 'ignore'), "lxml")
    for entry in parse_events(soup, 2018, 5):
        print(entry)
        break


if __name__ == '__main__':
    main()
