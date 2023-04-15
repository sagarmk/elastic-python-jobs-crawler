import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# function to scrape indeed resume based on search query
def scrape_resume(search_query):
    print("Starting the scraping process...")
    options = webdriver.FirefoxOptions()
    # options.add_argument('--headless')

    driver = webdriver.Firefox(options=options)
    driver.get("https://www.indeed.com/resumes?q=" + search_query)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    resume_listings = soup.find_all('div', {'class': 'rezemp-u-hr'})

    print(f"Found {len(resume_listings)} resume listings")
    print("Raw HTML of the first resume listing (if any):")
    if resume_listings:
        print(resume_listings[0])

    results = []
    for resume in resume_listings:
        try:
            name = resume.find('h2', {'class': 'icl-u-textBold'}).text
        except AttributeError:
            name = "Not found"
        
        try:
            location = resume.find('div', {'class': 'icl-u-textColor--tertiary'}).text
        except AttributeError:
            location = "Not found"
        
        try:
            title = resume.find('div', {'class': 'icl-u-lg-mr--sm'}).text
        except AttributeError:
            title = "Not found"

        result = f"Name: {name}\nLocation: {location}\nTitle: {title}\n\n"
        print(f"Extracted result: {result}")
        results.append(result)

    driver.quit()
    return results

class IndeedScraperApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Indeed Resume Scraper')

        layout = QVBoxLayout()

        self.search_label = QLabel('Enter search query:')
        layout.addWidget(self.search_label)

        self.search_input = QLineEdit()
        layout.addWidget(self.search_input)

        self.search_button = QPushButton('Search Resumes')
        self.search_button.clicked.connect(self.scrape_and_display_results)
        layout.addWidget(self.search_button)

        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        layout.addWidget(self.results_display)

        self.setLayout(layout)

    def scrape_and_display_results(self):
        print("Starting the search...")
        search_query = self.search_input.text()
        results = scrape_resume(search_query)

        self.results_display.clear()
        for result in results:
            print("Displaying a result...")
            self.results_display.append(result)

app = QApplication(sys.argv)
window = IndeedScraperApp()
window.show()
sys.exit(app.exec_())
