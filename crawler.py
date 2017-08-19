
import matplotlib as plt
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request, requests


def extract_text(el):
    if el:
        return el.text.strip()
    else:
        return ''      

def get_company_from_result(result):
    return extract_text(result.find('span', {'class' : 'company'}))

def get_location_from_result(result):
    return extract_text(result.find('span', {'class' : 'location'}))

def get_summary_from_result(result):
    return extract_text(result.find('span', {'class' : 'summary'}))

def get_title_from_result(result):
    return result.find('a', {'data-tn-element' : 'jobTitle'}).text.strip()

def get_salary_from_result(result):
    salary_table = result.find('td', {'class' : 'snip'})
    if salary_table:
        snip = salary_table.find('nobr')
        if snip:
            return snip.text.strip()

    return None


def extract_salary_average(salary_string):
    regex = r'\$([0-9]+,[0-9]+)'
    matches = re.findall(regex, salary_string)
    return np.mean([float(salary.replace(',', '')) for salary in matches ])

###########################
# crawling through indeed #
###########################

url_template = "http://www.indeed.com/jobs?l=USA&start={}"
max_results_per_city = 5 # Set this to a high-value (5000) to generate more results. 


rows = []
for start in range(1,10):
    ur = url_template.format(start)
    r = requests.get(ur)
    soup = BeautifulSoup(r.content) 
    results = soup.findAll('div', { "class" : "result" })
    for result in results:
        if result:
            row = {}
            row['title'] = get_title_from_result(result)
            row['company'] = get_company_from_result(result)
            row['summary'] = get_summary_from_result(result)
            row['city'] = get_location_from_result(result) 
            row['bin'] = salary
            row['url'] = ur
            #row['salary'] = get_salary_from_result(result)
            rows.append(row)
            print(row)
print("ROWS => ", rows)

########################
# elastic search setup #
########################

# make sure ES is up and running
import requests
res = requests.get('http://localhost:9200')
#print(res.content)


#connect to our cluster
from elasticsearch import Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


###################################
# indexing through collected jobs #
###################################

import json
r = requests.get('http://localhost:9200') 
i = 1
for elm in rows:
    
    es.index(index='indeed-jobs', doc_type='jobs', id=i, body=json.loads(json.dumps(elm)))
    i=i+1
 
# testing elastic search query 
es.get(index='indeed-jobs', doc_type='jobs', id=3)