import sys

from tabulate import tabulate
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from colorama import Fore



def get_estimated_average_prices(prices):
    average_product_price = sum(prices) / len(prices)
    extreme_below_average_price = average_product_price * 0.45
    
    new_prices = []
    for p in prices:
        if p > extreme_below_average_price:
            new_prices.append(p)
    
    average_product_price_new = sum(new_prices) / len(new_prices)
    below_average_price = average_product_price_new * 0.666
    
    return [average_product_price_new, below_average_price, extreme_below_average_price]


def run(driver, keyword, max_price, pages):
    collection = []
    collection_prices = []
    for page in range(1, pages+1):
        try:
            driver.get(f"https://www.ebay-kleinanzeigen.de/s-preis::{max_price}/seite:{page}/{keyword}/k0")
            
            links = [
                str(l.attrs['href']) for l in BeautifulSoup(driver.page_source, 'html.parser')
                .find_all('a', {'class': 'ellipsis'})
            ]
            
            prices = [
                str(p.text.strip("\n                                        ")
                .strip(" VB")
                .strip("€")
                .replace(" ", "")) for p in BeautifulSoup(driver.page_source, 'html.parser')
                .find_all('p', {'class': 'aditem-main--middle--price-shipping--price'})
            ]
            
            for p in prices:
                collection_prices.append(int(p))
            
            combined = []
            for l in links:
                combined.append([l, prices[links.index(l)]])
                
            collection = [pair for pair in combined if not 
                        "suche" in pair[0] and not
                        "tausche" in pair[0] and not 
                        "verpackung" in pair[0] and not
                        "defekt" in pair[0] and not
                        "bildfehler" in pair[0] and not 
                        "bastler" in pair[0] and not
                        "basteln" in pair[0] and not
                        "fehler" in pair[0]
                        ]
        except:
            break
    driver.close()
    print(collection)
    prices_information = get_estimated_average_prices(collection_prices)
    
    for pair in collection:
        if int(pair[1]) < prices_information[2]:
            collection.remove(pair)
    
    complete = []
    for pair in collection:
        number = Fore.GREEN + str(collection.index(pair)+1)
        link = Fore.WHITE + f"https://www.ebay-kleinanzeigen.de{pair[0]}"
        if int(pair[1]) >= prices_information[1]:
            price = Fore.GREEN + pair[1] + "€"
        else:
            price = Fore.RED + pair[1] + "€ - POSSIBLE SCAM OR WRONG PRODUCT"
        complete.append([number, link, price])
    
    print(
        "\n\n"
        + Fore.WHITE + "  KEYWORD: " + Fore.YELLOW + keyword 
        + Fore.WHITE + " | MAX. PRICE: " + Fore.YELLOW + max_price + "€" 
        + Fore.WHITE + " | PAGES: " + Fore.YELLOW + str(pages)
        + Fore.WHITE + " | AVERAGE PRICE: " + Fore.YELLOW + "~" + str(prices_information[0]) + "€"
        + "\n"
    ) 
    print(tabulate(complete, headers=["Nr.", "Link", "Price"]) + "\n\n")


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
