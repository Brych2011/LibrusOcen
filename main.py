from bs4 import BeautifulSoup
import re
import requests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def convertToSeconds(time):
    return ((int(time[0])*60+(int(time[2])*10)+int(time[3])+(int(time[5])*0.1)))
def deleteContent(pfile):
    """this part clears the temporary file that holds all of the text"""

    pfile.seek(0)
    pfile.truncate()



timesInSeconds = []
page = []
soup = []
masterText = open("TextFiles/masterText.txt", "w")
expression = re.compile("[0-9]:[0-9][0-9].[0-9]\n")
deleteContent(masterText)
""" This section downloads the data from each webpage and adds its text to the file"""
for x in range(1, 4):
    num = str(x)
    page.append(requests.get('https://log.concept2.com/rankings/2017/rower/2000?gender=M&status=race&page='+str(x)))
    soup.append(BeautifulSoup(page[x-1].content,"lxml"))
    masterText.write(soup[x-1].text)
    print(soup[x-1].text)
"""this section close the file and repens it for read"""

masterText.close()

regRead =  open("TextFiles/masterText.txt", "r")

linesInFile = regRead.readlines()

#these are the datapoints a want to collect
times = []
sportsMen = []
age = []



"""checks every line of the file for the pattern of the time and also removes the averege and the split times form the data set"""
for line in linesInFile[10:-10]:
    if re.match(expression, line):
        if re.match(expression, linesInFile[linesInFile.index(line)-1]) == None and re.match(expression, linesInFile[linesInFile.index(line)+1]) == None and len(linesInFile[linesInFile.index(line)+4]) <3 : #do not touch
            sportsMen.append(linesInFile[linesInFile.index(line)-5].strip()) # pulls the names of athletes and strips the \n from it and adds it to the list
            age.append(int(linesInFile[linesInFile.index(line) - 4].strip()))
            times.append(line) # adds the time to the list


print(times)

"""here it converts the ugly string to a pretty int in seconds"""
for x in times:
    temp = convertToSeconds(x)

    timesInSeconds.append(temp)



"""all numpy arrays from here"""

npTimes = np.array(timesInSeconds)
npAthletes = np.array(sportsMen)
npAge = np.array(age)


"""plotting section, here it will present the data that was downloaded on the end of the program"""


print(timesInSeconds)
"""plots the data here"""





print(sportsMen)
plt.plot(range(len(timesInSeconds)),timesInSeconds)




#pandas dataframe setup
tempNp = np.array([npTimes, npAge])
#mainframe = pd.DataFrame(data = tempNp, index = npAthletes)

#print(mainframe.describe())



plt.show()


#print(mainframe['Rolandas Mascinskas'])
