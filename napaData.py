#Title: Hazel interview exercise
#Author: Jesse Batstone
#Date Started: 9/19/2018
#Last Updated: 9/20/2018

import json
from lxml import html, etree
import urllib.request
from bs4 import BeautifulSoup
import re

json_dict = {}
page_url = (
    "http://ca.healthinspections.us/napa/search.cfm?start=1&1=1&sd=01/01/1970&ed=09/20/2018&kw1=&kw2=&kw3=&rel1=N.permitName&rel2=N.permitName&rel3=N.permitName&zc=&dtRng=YES&pre=similar"
)

#parse data from inspection reports
def parse(doc):
    #open inspection report
    with urllib.request.urlopen(doc) as url:                              
        soup = BeautifulSoup(url.read(), "lxml")
        #find all header information
        name = ""
        for test in soup.find_all('div'):
            if "topSection" in test['class']:
                string = test.get_text()
                #seperate lines
                string = string.split('\r' or '\n')
                #remove fluff
                for i in range(0,len(string)):
                    string[i] = string[i].strip("\u00a0\n\t")
                #store
                name = string[2].split(":")[1]
                json_dict[name] = {}
                json_dict[name][string[2].split(":")[0]] = name
                json_dict[name]["Street "+string[6].split(":")[0]] = string[6].split(":")[1]
                json_dict[name]["City"] = string[7].split(",")[0]
                json_dict[name]["State"] = string[7].split(",")[1].split(" ")[1]
                json_dict[name]["Zip Code"] = string[7].split(",")[1].split(" ")[2]

                json_dict[name]["Inspection "+string[4].split(":")[0]] = string[4].split(":")[1]
                json_dict[name][string[12].split(":")[0]] = string[12].split(":")[1]
        #get inspection grade
        table = soup.find('table',{"class" : "totPtsTbl"})
        first_td = table.findAll('td',{"class" : "center bold"})
        json_dict[name]["Inspection Grade"] = first_td[1].get_text().strip("\u00a0")
        
           
        badNums = []
        #get Item number and description for each out-of-compliance violation
        #get list of infractions
        for bad in soup.find_all('td',{"style":"width: 30px; vertical-align: top; border-right: none;"}):
            if int(str(bad.get_text()).split()[0]) not in badNums:
                badNums.append(int(str(bad.get_text()).split()[0]))
        #get descriptions of infractions
        json_dict[name]["Out of Compliance Violations"] = {}
        for test in soup.find_all('td',{"style":"text-align: left;"}):
            for i in badNums:
                if str(i)+"." in test.get_text():
                    json_dict[name]["Out of Compliance Violations"][test.get_text().split(". ")[0]] =test.get_text().split(". ")[1] 


def main():
    docUrls = []   #store links to inspection reports
    #open search results
    with urllib.request.urlopen(page_url) as url:
        soup = BeautifulSoup(url.read(), "lxml")
    #find all links
    links = soup.find_all('a')
    #open all links
    for a_tags in links:
        if "estab.cfm?permitID=" in a_tags['href']:
            with urllib.request.urlopen("http://ca.healthinspections.us/napa/" + a_tags['href']) as url:
                soup1 = BeautifulSoup(url.read(), "lxml")
                links1 = soup1.find_all('a')
                #find all inspection reports and store in list
                for i in range(0,len(links1)):
                    if "/_templates/135" in links1[i]['href']:
                        docUrls.append("http://ca.healthinspections.us/_templates/135/Food%20Inspection/" + links1[i]['href'][34:])
    #open and parse all data
    for i in docUrls:
        parse(i)
    #write json to disk
    with open("napaHealthInspectionData.json", 'w') as outfile:
        json.dump(json_dict,outfile, indent=4)
    #print data to console
    print(json.dumps(json_dict, indent=4))
    
        
if __name__ == '__main__':
    main()
