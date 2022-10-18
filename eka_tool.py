import sys

from tabulate import tabulate
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from colorama import Fore



# All filters that can be applied to prodcut information goes here
def advanced_filters(prices):
    average_product_price = sum(int(p) for p in prices) / len(prices)
    
    below_average_price = average_product_price * 0.666
    extreme_below_average_price = average_product_price* 0.45
    
    return([average_product_price, below_average_price, extreme_below_average_price])


def run(driver, keyword, max_price, pages):
    collection = []
    for page in range(1, pages+1):
        try:
            driver.get(f"https://www.ebay-kleinanzeigen.de/s-preis::{max_price}/seite:{page}/{keyword}/k0")
            
            # extracting links from source code
            links = [
                str(l.attrs['href']) for l in BeautifulSoup(driver.page_source, 'html.parser')
                .find_all('a', {'class': 'ellipsis'})
            ]
            
            # extracting prices from source code
            prices = [
                str(p.text.strip("\n                                        ")
                .strip(" VB")
                .strip("€")
                .replace(" ", "")) for p in BeautifulSoup(driver.page_source, 'html.parser')
                .find_all('p', {'class': 'aditem-main--middle--price-shipping--price'})
            ]
            
            driver.close()
            
            # average_product_price - below_average_price
            information = advanced_filters(prices)
            
            # merging links to corresponding prices
            combined = []
            for l in links:
                combined.append([l, prices[links.index(l)]])
                
            # removing links matching filter keywords & applied advanced filter
            filtered = [pair for pair in combined if not 
                        "suche" in pair[0] and not
                        "tausche" in pair[0] and not 
                        "verpackung" in pair[0] and not
                        "defekt" in pair[0] and not
                        "bildfehler" in pair[0] and not 
                        "bastler" in pair[0] and not
                        "basteln" in pair[0] and not
                        "fehler" in pair[0] and not
                        int(pair[1]) < information[2]
                        ]
        
                
            # formatting link-price pairs for output
            for pair in filtered:
                number = Fore.GREEN + str(filtered.index(pair)+1)
                link = Fore.WHITE + f"https://www.ebay-kleinanzeigen.de{pair[0]}"
                
                if int(pair[1]) >= information[1]:
                    price = Fore.GREEN + pair[1] + "€"
                else:
                    price = Fore.RED + pair[1] + "€ - POSSIBLE SCAM OR WRONG PRODUCT"
                collection.append([number, link, price])
        except:
            break
    
    # output
    print(
        "\n\n"
        + Fore.WHITE + "  KEYWORD: " + Fore.YELLOW + keyword 
        + Fore.WHITE + " | MAX. PRICE: " + Fore.YELLOW + max_price + "€" 
        + Fore.WHITE + " | PAGES: " + Fore.YELLOW + str(pages)
        + Fore.WHITE + " | AVERAGE PRICE: " + Fore.YELLOW + "~" + str(information[0]) + "€"
        + "\n"
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
