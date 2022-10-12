import sys

from tabulate import tabulate
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from colorama import Fore


def run(driver, keyword, max_price, pages):
    collection = []
    for page in range(1, pages+1):
        try:
            driver.get(f"https://www.ebay-kleinanzeigen.de/s-preis::{max_price}/seite:{page}/{keyword}/k0")
            
            links = [
                str(l.attrs['href']) for l in BeautifulSoup(driver.page_source, 'html.parser')
                .find_all('a', {'class': 'ellipsis'})
            ]
            
            prices = [
                str(p.text.strip("\n                                        ")
                .strip(" VB").replace(" ", "")) for p in BeautifulSoup(driver.page_source, 'html.parser')
                .find_all('p', {'class': 'aditem-main--middle--price-shipping--price'})
            ]
            
            combined = []
            for l in links:
                combined.append([l, prices[links.index(l)]])
                
            filtered = [pair for pair in combined if not 
                        "suche" in pair[0] and not
                        "tausche" in pair[0] and not 
                        "verpackung" in pair[0] and not
                        "defekt" in pair[0] and not
                        "bildfehler" in pair[0] and not 
                        "bastler" in pair[0] and not
                        "basteln" in pair[0]
                        ]
            
            for pair in filtered:
                number = Fore.GREEN + str(filtered.index(pair))
                link = Fore.WHITE + f"https://www.ebay-kleinanzeigen.de{pair[0]}"
                price = Fore.GREEN + pair[1]
                collection.append([number, link, price])
        except:
            break

    driver.close()
    
    print(
        "\n\n" + "  KEYWORD: " + Fore.YELLOW + keyword 
        + Fore.WHITE + " | MAX. PRICE: " + Fore.YELLOW + max_price + "€" 
        + Fore.WHITE + " | PAGES: " + Fore.YELLOW + str(pages) +"\n"
    ) 
    print(tabulate(collection, headers=["Nr.", "Link", "Price"]) + "\n\n")


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
    start()
    