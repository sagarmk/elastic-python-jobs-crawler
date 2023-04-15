import re
import json
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

class IndeedJobScraper:
    
    def __init__(self, url_template, max_results_per_city):
        self.url_template = url_template
        self.max_results_per_city = max_results_per_city
        
    def extract_text(self, el):
        if el:
            return el.text.strip()
        else:
            return ''
        
    def get_company_from_result(self, result):
        return self.extract_text(result.find('span', {'class' : 'company'}))

    def get_location_from_result(self, result):
        return self.extract_text(result.find('span', {'class' : 'location'}))

    def get_summary_from_result(self, result):
        return self.extract_text(result.find('span', {'class' : 'summary'}))

    def get_title_from_result(self, result):
        return result.find('a', {'data-tn-element' : 'jobTitle'}).text.strip()

    def get_salary_from_result(self, result):
        salary_table = result.find('td', {'class' : 'snip'})
        if salary_table:
            snip = salary_table.find('nobr')
            if snip:
                return snip.text.strip()
        return None

    def extract_salary_average(self, salary_string):
        regex = r'\$([0-9]+,[0-9]+)'
        matches = re.findall(regex, salary_string)
        return np.mean([float(salary.replace(',', '')) for salary in matches ])
    
    def crawl_indeed(self):
        rows = []
        for start in range(1, self.max_results_per_city):
            url = self.url_template.format(start)
            response = requests.get(url)
            soup = BeautifulSoup(response.content)
            results = soup.findAll('div', {"class": "result"})
            for result in results:
                if result:
                    row = {}
                    row['title'] = self.get_title_from_result(result)
                    row['company'] = self.get_company_from_result(result)
                    row['summary'] = self.get_summary_from_result(result)
                    row['city'] = self.get_location_from_result(result) 
                    row['bin'] = self.get_salary_from_result(result)
                    row['url'] = url
                    rows.append(row)
                    print(row)
        print("ROWS => ", rows)
        return rows
    
    def setup_elasticsearch(self):
        # Make sure Elasticsearch is up and running
        res = requests.get('http://localhost:9200')
        print(res.content)

        # Connect to our cluster
        from elasticsearch import Elasticsearch
        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        return es
    
    def index_jobs(self, rows):
        es = self.setup_elasticsearch()
        i = 1
        for elm in rows:
            es.index(index='indeed-jobs', doc_type='jobs', id=i, body=json.loads(json.dumps(elm)))
            i += 1
        # Testing Elasticsearch query 
        es.get(index='indeed-jobs', doc_type='jobs', id=3)

        
if __name__ == '__main__':
    url_template = "http://www.indeed.com/jobs?l=USA&start={}"
    max_results_per_city = 5  # Set this to a high-value (5000) to generate more results.
    
    indeed = IndeedJobScraper(url_template, max_results_per_city)
    jobs = indeed.crawl_indeed()
    indeed.index_jobs(jobs)
