from bs4 import BeautifulSoup
#Just a test to check integration with pycharm

MARK_VALUES = {'1':1, '1+':1.5, '2-':1.75, '2':2, '2+':2.5, '3-':2.75, '3':3, '3+':3.5,
               '4-':3.75, '4':4, '4+':4.5, '5-':4.75, '5':5, '5+':5.5, '6-':5.75, '6':6,
               'np':'np', '+':'+', '0':'0', '-': '-'}


def parse_marks(bs_object):
    marks = bs_object.find_all('a')
    results = []
    for i in marks:
        mark_data = {}
        data = i.attrs['title'].strip('<br/>').split('<br>')
        for j in data:
            semicolon_idex = j.find(':')
            mark_data[j[0 : semicolon_idex]] = j[semicolon_idex+2:]
        mark_data['intOcena'] = MARK_VALUES[i.text]
        results.append(mark_data)
    return results



def parse_subject(foo):
    parts = foo.find_all(name='td', recursive=False)
    length = len(parts)
    name = parts[1].text

    if parts[2].text == 'Brak ocen':
        marks1 = None
        average = None
    else:
        marks1 = parse_marks(parts[2])
        average = parts[3].text

    if parts[4].text == ' - ':
        semestral = None
    else:
        semestral = parts[4].text

    if parts[5].text == 'Brak ocen':
        marks2 = None
        average2 = None
        yearly_average = None
    else:
        marks2 = parse_marks(parts[5])
        average2 = parts[6].text
        yearly_average = parts[8].text


    if parts[7].text == ' - ':
        semestral2 = None
    else:
        semestral2 = parts[7].text


    if parts[9].text == ' - ':
        final_mark = None
    else:
        final_mark = parts[9].text

    return name, marks1, average, semestral, marks2, average2, semestral2, yearly_average, final_mark


def get_marks_table(bs_page):
    """extraxts the table with marks from librus' source file"""
    stage1 = bs_page.find(name='div', id='body')
    return stage1.find_all(name = 'table', class_ = 'decorated stretch')[1]         #TODO make it look more... appealing


page = open("librushtml.html", 'r')
parsed_page = BeautifulSoup(page, "html.parser")

table = get_marks_table(parsed_page)
marks_part = table.find('tbody')
subject_list = []
for i in marks_part.find_all(name='tr', recursive=False):   #finds all <tr>'s responsible for grades
    if not 'style' in i.attrs.keys ():                      #TODO get rid of class="bolded line1" at the end
        try:
            subject_list.append(parse_subject(i))
        except Exception as e:
            print(repr(e))

print(subject_list)



