import time
import requests
import logging
import threading

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from flask import Flask

# Configure flask for endpoint routing
app = Flask(__name__)

#configure logging
logging.basicConfig(filename='api_logging.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

URL = 'https://new.mta.info/'
SCRAPE_INTERVAL_SECONDS = 60

# Set Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument('--headless')  # Enable headless mode

# Initialize a Selenium webdriver with headless options
driver = webdriver.Chrome(options=chrome_options)

# Count the service start time for the uptime calculation
start_time = time.time()

threadDict = {}
thread_terminate_flags = {}


delaySet = {}
notDelaySet = set()

# initiate scraping for specified URL
def scrape_website():
    driver.get(URL)
    html_content = driver.page_source
    return soup_work(html_content)

# keeps track of how many seconds a subway line has been in the DelaySet
def track_time(element):
    while True:
        if element in delaySet:
            delaySet[element] += 1
            time.sleep(1)
            
# adds the thread for a subway line when added to DelaySet
def add_element(element):
    if element not in delaySet:
        delaySet[element] = 0
        thread_terminate_flags[element] = threading.Event()
        thread = threading.Thread(target=track_time,args=(element,))
        threadDict[element] = thread
        thread.start()

# eliminates the thread for a subway line when removed from DelaySet
def terminate_thread(element):
    if element in thread_terminate_flags:
        thread_terminate_flags[element].set()
        threadDict[element].join()
        del thread_terminate_flags[element]
        del threadDict[element]

# finds the subway lines on the NJT site and what categories they fall into
# Adds lines that aren't in delay set but fall under the delay category to the delay set
# Adds lines that aren't in the non-delay set but fall under the non-delay category to the non-delay set 
# Logs info from non-delay --> delay and delay --> non-delay transition
def soup_work(res):
    soup = BeautifulSoup(res, 'html.parser')

    categories = soup.find_all('div', class_='by-status')

    for category in categories:
        category_name = category.find('h5').text.strip()
        line_letters = set()
        for line in category.find_all('span', class_='line'):
            line_letters.add(line.text.strip())
        if category_name == "Delays":
            for element in line_letters.difference(set(delaySet.keys())):
                if element in notDelaySet :
                    notDelaySet.remove(element)
                add_element(element)
                logging.info('Line %s is experiencing delays', element)
        else:
            for element in line_letters.difference(notDelaySet):
                if element in delaySet:
                    terminate_thread(element)
                    del delaySet[element]
                notDelaySet.add(element)
                logging.info('Line %s is now recovered', element)


    categoryNoActiveAlerts = soup.find_all('div', class_='good-service-lines-center')
    for category in categoryNoActiveAlerts:
        category_name = category.find('h5').text.strip()
        line_letters = set()
        for line in category.find_all('span', class_='line'):
            line_letters.add(line.text.strip())
        for element in line_letters.difference(notDelaySet):
            if element in delaySet:
                terminate_thread(element)
                del delaySet[element]
            notDelaySet.add(element)
            logging.info('Line %s is now recovered', element)
    return 

# starts running the thread that accesses the site to look for the subway lines
def background_task():
    while True:
        print("Background task is running... ")
        scrape_website()
        #print("DELAY SET:   " , delaySet) 
        time.sleep(5)
        

backgroundThread = threading.Thread(target=background_task)
backgroundThread.start()

# tells whether a subway line is delayed or not
@app.route('/status/<lineName>')
def getStatus(lineName):
    return "Line " + lineName + " is Delayed " + str(lineName in delaySet)

# Get the total uptime for a subawy line
@app.route('/uptime/<lineName>')
def user_profile(lineName):
    if lineName not in delaySet:
        return "Line " + lineName + " has not been delayed for 100% of the time"
    # Implement the formula as per guidlines, 1 - (total_time_delayed / total_time)
    return "Line " + lineName + " has not been delayed for " + str(round((1 - (delaySet[lineName] / (time.time() - start_time))) * 100, 1)) + "% of the time"

if __name__ == '__main__':
    app.run()

