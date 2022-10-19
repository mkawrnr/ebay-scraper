import sys
import argparse

from tabulate import tabulate
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from colorama import Fore


# additional command-line parameters are created here
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", dest="name")
parser.add_argument("-mp", "--max-price", dest="max_price")
parser.add_argument("-p", "--pages", dest="pages", default=1)
args = parser.parse_args()

# add / remove filter keywords
FILTERWORDS = ['suche', 'tausche',
               'verpackung', 'defekt', 
               'bildfehler', 'bastler', 
               'basteln', 'fehler',
               'kaputt',
               ]



# to calculate the true average price of the searched item
def get_estimated_average_prices(prices):
    average_product_price = sum(prices) / len(prices)
    extreme_below_average_price = average_product_price * 0.45
    
    new_prices = [p for p in prices if p > extreme_below_average_price]  
    average_product_price_new = sum(new_prices) / len(new_prices)
    below_average_price = average_product_price_new * 0.8
    
    return [average_product_price_new, below_average_price, extreme_below_average_price]


def run(driver, keyword, max_price, pages):
    link_price_pairs = []
    for page in range(1, pages+1):
        try:
            driver.get(f"https://www.ebay-kleinanzeigen.de/s-preis::{max_price}/seite:{page}/{keyword}/k0")
            
            # extracts item links
            links = [
                str(l.attrs['href']) for l in BeautifulSoup(driver.page_source, 'html.parser')
                .find_all('a', {'class': 'ellipsis'})
            ]
            
            # extracts item prices
            prices = [
                str(p.text.strip("\n                                        ")
                .strip(" VB")
                .strip("€")
                .replace(" ", "")) for p in BeautifulSoup(driver.page_source, 'html.parser')
                .find_all('p', {'class': 'aditem-main--middle--price-shipping--price'})
            ]
            
            # combines extracted links and prices; removes items matching filter words
            combined = list(zip(links, prices))
            combined_filtered = [pair for pair in combined if not any(word in pair[0] for word in FILTERWORDS)] 
            for pair in combined_filtered:
                link_price_pairs.append(pair)
        except:
            break
        
    # terminates driver instance
    driver.close()
    
    # sorts out items by calculating and applying extrem_below_average_price filter
    prices_collection = [int(p[1]) for p in link_price_pairs]
    prices_information = get_estimated_average_prices(prices_collection)
    link_price_pairs = [pair for pair in link_price_pairs if int(pair[1]) > prices_information[2]]
    
    # formats number, links and prices for output
    formatted_link_price_pairs = []
    for pair in link_price_pairs:
        number = Fore.GREEN + str(link_price_pairs.index(pair)+1)
        link = Fore.WHITE + f"https://www.ebay-kleinanzeigen.de{pair[0]}"
        if int(pair[1]) >= prices_information[1]:
            price = Fore.GREEN + pair[1] + "€"
        else:
            price = Fore.RED + pair[1] + "€ - POSSIBLE SCAM OR WRONG PRODUCT"
        formatted_link_price_pairs.append([number, link, price])
    
    # prints formatted output
    print(
        "\n\n"
        + Fore.WHITE + "  KEYWORD: " + Fore.YELLOW + keyword 
        + Fore.WHITE + " | MAX. PRICE: " + Fore.YELLOW + max_price + "€" 
        + Fore.WHITE + " | PAGES: " + Fore.YELLOW + str(pages)
        + Fore.WHITE + " | AVERAGE PRICE: " + Fore.YELLOW + f"~{prices_information[0]:0.2f}€"
        + "\n"
    ) 
    
    print(tabulate(formatted_link_price_pairs, headers=["Nr.", "Link", "Price"]) + "\n\n")


# creates and returns driver instance
def create_driver():
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument('--headless')
    driver = webdriver.Firefox(
        options=firefox_options,
        service=Service(GeckoDriverManager().install())
    )
    
    return driver


def start():        
    keyword = str(args.name)
    max_price = str(args.max_price)
    pages = int(args.pages)
    
    # required command-line parameters check
    if not keyword or not max_price:
        print("Keyword or price missing, exit.")
        sys.exit(1)
        
    driver = create_driver()
    run(driver, keyword, max_price, pages)
    

if __name__ == '__main__':
    start()
