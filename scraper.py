import sys
import re
import argparse
import requests
import platform

from tabulate import tabulate
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from colorama import Fore
from random import choice



parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", dest="name")
parser.add_argument("-mp", "--max-price", dest="max_price")
parser.add_argument("-p", "--pages", dest="pages", default=1)
parser.add_argument("-d", "--driver", dest="webdriver", default="firefox")
parser.add_argument("-l", "--list", dest="list", default=False)
args = parser.parse_args()

# adding keywords to FILTER_WORDS will mostly remove any articles with these words included
FILTER_WORDS = [
    'kaputt',
    'bastler',
    'tausche',
    'defekt',
    'risse',
    'hülle',
    'case'
]


def run(driver, keyword, max_price, pages):
    link_price_pairs = []
    for page in range(1, pages + 1):
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
            combined_filtered = [pair for pair in combined if not any(re.search(r'\b{}\b'.format(keyword), pair[0].lower(), re.IGNORECASE) for keyword in FILTER_WORDS)]
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


    if args.list:
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        
        with open(f'results/results-{current_time}.txt', 'w') as file:
            for i, pair in enumerate(link_price_pairs):
                
                if int(pair[1]) >= prices_information[1]:
                    price = pair[1] + "€"
                else:
                    price = pair[1] + "€ - SCAM/DAMAGED/WRONG PRODUCT"
                
                file.write(f"{i+1}. https://www.kleinanzeigen.de{pair[0]} - {price}\n")
    else:
        # formats number, links and prices for output
        formatted_link_price_pairs = []
        for pair in link_price_pairs:
            number = Fore.GREEN + str(link_price_pairs.index(pair) + 1)
            link = Fore.WHITE + f"https://www.kleinanzeigen.de{pair[0]}"
            if int(pair[1]) >= prices_information[1]:
                price = Fore.GREEN + pair[1] + "€"
            else:
                price = Fore.RED + pair[1] + "€ - SCAM/DAMAGED/WRONG PRODUCT"
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


# calculates the true average price of the searched item
def get_estimated_average_prices(prices):
    extreme_below_average_price = (sum(prices) / len(prices)) * 0.45 # factor change by desire
    new_prices = [p for p in prices if p > extreme_below_average_price]
    average_product_price = sum(new_prices) / len(new_prices)
    below_average_price = average_product_price * 0.8 # factor change by desire

    return [average_product_price, below_average_price, extreme_below_average_price]


# creates and returns driver instance
def create_driver(wd):
    if wd == 'firefox':
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument('--headless')
        firefox_options.add_argument(f'user-agent={generate_user_agent()}')
        driver = webdriver.Firefox(
            options=firefox_options,
            service=Service(GeckoDriverManager().install())
        )
    else:
        chrome_options = webdriver.ChromeOptions()        
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--enable-javascript')   
        chrome_options.add_argument('--headless')
        chrome_options.add_argument(f"user-agent={generate_user_agent()}")
        
        if platform.system() == 'Darwin':
            driver = webdriver.Chrome(executable_path="webdrivers/chromedriver", options=chrome_options)
        else:
            # get latest chromedriver version
            url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
            response = requests.get(url)
            version_number = response.text
            driver = webdriver.Chrome(service=Service(ChromeDriverManager(version=version_number).install()))

    return driver


# return random user-agent string
def generate_user_agent() -> str:
    user_agents = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 "
        "Safari/600.1.25",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 "
        "Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 "
        "Safari/537.85.10",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36",
        ]

    return choice(user_agents)


def start():
    keyword = str(args.name)
    max_price = str(args.max_price)
    pages = int(args.pages)
    webdriver = str(args.webdriver)

    # required command-line parameters check
    if not keyword or not max_price:
        print("Keyword or price missing, exit.")
        sys.exit(1)
        
    if pages < 1:
        print("Number of pages must be larger than 0, exit.")
        sys.exit(1)
        
    if webdriver.lower() not in ['firefox', 'chrome']:
        print("Select a valid webdriver (e.g. chrome or firefox)")
        sys.exit(1)
        
    driver = create_driver(webdriver)
    run(driver, keyword, max_price, pages)


if __name__ == '__main__':
    start()
