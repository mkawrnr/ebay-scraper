from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from colorama import Fore


def run(driver, keyword, price):
    URL = f"https://www.ebay-kleinanzeigen.de/s-preis::{price}/{keyword}/k0"
        
    driver.get(URL)
    links = [str(l.attrs['href']) for l in BeautifulSoup(driver.page_source, 'html.parser').find_all('a', {'class': 'ellipsis'})]
    filtered = [l for l in links if not 
                "suche" in l and not
                "tausche" in l and not 
                "verpackung" in l and not
                "defekt" in l and not
                "bildfehler" in l and not 
                "bastler" in l
                ]
    
    print("\n\n" + "GPU: " + Fore.YELLOW + keyword + Fore.WHITE + " MAX. PRICE: " + Fore.YELLOW + price + "€" + "\n") 
    for i in range(len(filtered)):
        print(Fore.GREEN + f"[{i + 1}] - " + Fore.WHITE + f"https://www.ebay-kleinanzeigen.de{filtered[i]}")
    print("\n")
    
    driver.close()
    start()
        

def start():    
    keyword = str(input("KEYWORD >> "))
    if keyword == "exit":
        exit()
    price = str(input("PRICE >> "))
    
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument('--headless')
    driver = webdriver.Firefox(
        options=firefox_options,
        service=Service(GeckoDriverManager().install())
    )
    
    run(driver, keyword, price)
    

if __name__ == '__main__':
    start()
    