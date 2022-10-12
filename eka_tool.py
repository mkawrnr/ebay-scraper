import sys

from os import system
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from colorama import Fore


def run(driver, keyword, max_price, pages):
    collection = []
    for page in range(1, pages+1):
        try:
            driver.get(f"https://www.ebay-kleinanzeigen.de/s-preis::{max_price}/seite:{page}/{keyword}/k0")
            links = [str(l.attrs['href']) for l in BeautifulSoup(driver.page_source, 'html.parser').find_all('a', {'class': 'ellipsis'})]
            filtered = [l for l in links if not 
                        "suche" in l and not
                        "tausche" in l and not 
                        "verpackung" in l and not
                        "defekt" in l and not
                        "bildfehler" in l and not 
                        "bastler" in l and not
                        "basteln" in l
                        ]
            for l in filtered:
                collection.append(l)
        # breaks if less pages available than specified
        except:
            break
    
    print("\n\n" 
        + Fore.WHITE + "GPU: " + Fore.YELLOW + keyword
        + Fore.WHITE + " | MAX. PRICE: " + Fore.YELLOW + max_price + "€"
        + Fore.WHITE + " | PAGES: " + Fore.YELLOW + str(pages) 
        +"\n")
     
    for i in range(len(collection)):
        print(Fore.GREEN + f"[{i + 1}] - " + Fore.WHITE + f"https://www.ebay-kleinanzeigen.de{collection[i]}")
    print("\n")
    
    driver.close()
        

def start():
    if len(sys.argv) != 4:
        print("Invalid Arguments")
        sys.exit(1)
        
    keyword = sys.argv[1]
    max_price = sys.argv[2]
    pages = int(sys.argv[3])
   
    
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument('--headless')
    driver = webdriver.Firefox(
        options=firefox_options,
        service=Service(GeckoDriverManager().install())
    )
    
    run(driver, keyword, max_price, pages)
    

if __name__ == '__main__':
    if sys.platform in ['linux', 'linux2']:
        system('pip install -r requirements.txt')
    start()
    