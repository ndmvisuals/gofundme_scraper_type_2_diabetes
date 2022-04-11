### Libraries

# packages to install
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd

# packages that are included
import time
from datetime import datetime
import json
import pathlib
import os
import tarfile
import shutil

### Set up Chrome Driver

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(
        ChromeDriverManager().install(),
        options=chrome_options
        )

### Set up search term

search_term = "type 2 diabetes"
ls_search_term = search_term.split(" ") 
search_term_final = "+".join([word for word in ls_search_term])
search_term_filename = "_".join([word for word in ls_search_term])

### Set up folders

date = datetime.now().strftime("%Y-%m-%d")
pathlib.Path(f'data/html/{date}--{search_term_filename}/').mkdir(parents=True, exist_ok=True)

### Scrape list of urls for search results

i = 1
page_result = "Fundraisers for"
ls_urls = []
while "Fundraisers for" in page_result:
    driver.get(f"https://www.gofundme.com/s?q={search_term_final}&pg={i}")
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    page_result = soup.find("h1", {"class": "text-regular"}).text
    cards = soup.find_all("div", {"class": "m-search-result-card"})    
    for card in cards:
        detail = card.find("a")
        url = "https://www.gofundme.com"+ detail["href"]
        ls_urls.append(url)
    i = i +1
    print(f"Page {i} done")
    
 ### Scrape HTML and save in folder
 
 
 row_url = []
row_file_name = []
row_status = []

for url in tqdm(ls_urls[0:2]):
    html_dict = {}
    try:
        driver.get(url)
    except:
        status = "url didn't open"
    try:
        html = driver.page_source  
        date_time_now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]
        complete_filename = f"{date_time_now}--{search_term_filename}"
        file = open(f"data/html/{date}--{search_term_filename}/{complete_filename}.html","w")
        file.write(html)
        file.close()      
    except:
        file_name = "no file name"
        status = "html didn't save"
    status = "complete"

    row_url.append(url)
    row_file_name.append(complete_filename)
    row_status.append(status)
    time.sleep(5) 

log = pd.DataFrame(list(zip(row_url, row_file_name, row_status)), columns = ["url", "file_name"  ,"status"])
log.to_csv(f"data/html/{date}--{search_term_filename}/{date}--log_{search_term_filename}.csv")


### Compress and save html files and log into tar.gz

with tarfile.open(f"data/{date}--{search_term_filename}.tar.gz", "w:gz") as tar:
    tar.add(f"data/html/{date}--{search_term_filename}/", arcname=os.path.basename(f"data/html/{date}--{search_term_filename}/"))
    
### Delete html files

path = pathlib.Path(f"data/html/{date}--{search_term_filename}/")
shutil.rmtree(path)



