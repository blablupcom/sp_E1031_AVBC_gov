# -*- coding: utf-8 -*-

#### IMPORTS 1.0

import os
import re
import scraperwiki
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup


#### FUNCTIONS 1.0

def validateFilename(filename):
    filenameregex = '^[a-zA-Z0-9]+_[a-zA-Z0-9]+_[a-zA-Z0-9]+_[0-9][0-9][0-9][0-9]_[0-9QY][0-9]$'
    dateregex = '[0-9][0-9][0-9][0-9]_[0-9QY][0-9]'
    validName = (re.search(filenameregex, filename) != None)
    found = re.search(dateregex, filename)
    if not found:
        return False
    date = found.group(0)
    now = datetime.now()
    year, month = date[:4], date[5:7]
    validYear = (2000 <= int(year) <= now.year)
    if 'Q' in date:
        validMonth = (month in ['Q0', 'Q1', 'Q2', 'Q3', 'Q4'])
    elif 'Y' in date:
        validMonth = (month in ['Y1'])
    else:
        try:
            validMonth = datetime.strptime(date, "%Y_%m") < now
        except:
            return False
    if all([validName, validYear, validMonth]):
        return True


def validateURL(url, download_data):
    try:
        r = requests.post(url, data=download_data)
        count = 1
        while r.status_code == 500 and count < 4:
            print ("Attempt {0} - Status code: {1}. Retrying.".format(count, r.status_code))
            count += 1
            r = requests.post(url, data=download_data)
        sourceFilename = r.headers.get('Content-Disposition')

        if sourceFilename:
            ext = os.path.splitext(sourceFilename)[1].replace('"', '').replace(';', '').replace(' ', '')
        else:
            ext = os.path.splitext(url)[1]
        validURL = r.status_code == 200
        validFiletype = ext.lower() in ['.csv', '.xls', '.xlsx']
        return validURL, validFiletype
    except:
        print ("Error validating URL.")
        return False, False


def validate(filename, file_url, download_data):
    validFilename = validateFilename(filename)
    validURL, validFiletype = validateURL(file_url, download_data)
    if not validFilename:
        print filename, "*Error: Invalid filename*"
        print file_url
        return False
    if not validURL:
        print filename, "*Error: Invalid URL*"
        print file_url
        return False
    if not validFiletype:
        print filename, "*Error: Invalid filetype*"
        print file_url
        return False
    return True


def convert_mth_strings ( mth_string ):
    month_numbers = {'JAN': '01', 'FEB': '02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06', 'JUL':'07', 'AUG':'08', 'SEP':'09','OCT':'10','NOV':'11','DEC':'12' }
    for k, v in month_numbers.items():
        mth_string = mth_string.replace(k, v)
    return mth_string


#### VARIABLES 1.0

entity_id = "E1031_AVBC_gov"
url = "http://www.ambervalley.gov.uk/council-and-democracy/council-budgets-and-spending/invoices-over-500.aspx"
errors = 0
data = []
download_data = {"__EVENTTARGET":"",
"__EVENTARGUMENT":"",
"__VIEWSTATE":"/wEPDwUENTM4MWRkoQazEup3A3cpuKDAQVyRPVsKDWKUpiy7/P98F7cfzY4=",
"ctl00$ctl00$ctl00$ContentPlaceHolderDefault$MasterTemplateBodyMainPlaceHolder$ctl00$Invoices50Plus_4$ddlYear":"2017",
"ctl00$ctl00$ctl00$ContentPlaceHolderDefault$MasterTemplateBodyMainPlaceHolder$ctl00$Invoices50Plus_4$ddlMonth":"5",
"ctl00$ctl00$ctl00$ContentPlaceHolderDefault$MasterTemplateBodyMainPlaceHolder$ctl00$Invoices50Plus_4$btnSubmit":"Submit",
"__VIEWSTATEGENERATOR":"CA0B0334"}

#### READ HTML 1.0
import requests
html = urllib2.urlopen(url)
soup = BeautifulSoup(html, "lxml")

#### SCRAPE DATA

year_dates = soup.find('select', attrs={'name':'ctl00$ctl00$ctl00$ContentPlaceHolderDefault$MasterTemplateBodyMainPlaceHolder$ctl00$Invoices50Plus_4$ddlYear'}).find_all('option')
for year_date in year_dates:
    year = year_date['value']
    months_dates = soup.find('select', attrs={'name':'ctl00$ctl00$ctl00$ContentPlaceHolderDefault$MasterTemplateBodyMainPlaceHolder$ctl00$Invoices50Plus_4$ddlMonth'}).find_all('option')
    for months_date in months_dates:
        month = months_date['value']
        download_data['ctl00$ctl00$ctl00$ContentPlaceHolderDefault$MasterTemplateBodyMainPlaceHolder$ctl00$Invoices50Plus_4$ddlYear'] = year
        download_data['ctl00$ctl00$ctl00$ContentPlaceHolderDefault$MasterTemplateBodyMainPlaceHolder$ctl00$Invoices50Plus_4$ddlMonth'] = month
        download_page = requests.post(url, data=download_data)
        download_soup = BeautifulSoup(download_page.text, "lxml")
        download_link = download_soup.find('input', id="ContentPlaceHolderDefault_MasterTemplateBodyMainPlaceHolder_ctl00_Invoices50Plus_4_btnDownloadCSV")
        d_csv = ''
        try:
            d_csv = download_link['value']
        except:
            pass
        if d_csv:
            d_data = {"__EVENTTARGET":"",
                    "__EVENTARGUMENT":"",
                    "__VIEWSTATE":"/wEPDwUENTM4MWRkoQazEup3A3cpuKDAQVyRPVsKDWKUpiy7/P98F7cfzY4=",
                    "ctl00$ctl00$ctl00$ContentPlaceHolderDefault$MasterTemplateBodyMainPlaceHolder$ctl00$Invoices50Plus_4$ddlYear":year,
                    "ctl00$ctl00$ctl00$ContentPlaceHolderDefault$MasterTemplateBodyMainPlaceHolder$ctl00$Invoices50Plus_4$ddlMonth":month,
                    "ctl00$ctl00$ctl00$ContentPlaceHolderDefault$MasterTemplateBodyMainPlaceHolder$ctl00$Invoices50Plus_4$btnDownloadCSV":"DownloadCSV",
                    "__VIEWSTATEGENERATOR":"CA0B0334"}
            csvMth = months_date.text[:3]
            csvYr = year
            csvMth = convert_mth_strings(csvMth.upper())
            data.append([csvYr, csvMth, url, d_data])


#### STORE DATA 1.0

for row in data:
    csvYr, csvMth, url, download_data = row
    filename = entity_id + "_" + csvYr + "_" + csvMth
    todays_date = str(datetime.now())
    file_url = url.strip()

    valid = validate(filename, file_url, download_data)

    if valid == True:
        scraperwiki.sqlite.save(unique_keys=['l'], data={"l": file_url, "f": filename, "d": todays_date })
        print filename
    else:
        errors += 1

if errors > 0:
    raise Exception("%d errors occurred during scrape." % errors)


#### EOF
