<h3>Requires Firefox to be installed because the Selenium Geckodriver is used</h3>

![Preview Screenshot](./preview.png "Preview")

**Install Requirements**<br>
```
pip install -r requirements.txt
```
**Usage**<br>
```
Required

scraper.py [-n NAME; --name NAME] set the article name
           [-mp PRICE; --max_price PRICE] set the maximum price


Optional

scraper.py [-p PAGES; --pages PAGES] set how many pages to scrape
           [-d DRIVER; --driver DRIVER] set which driver to use (chrome / firefox) 


Example

scraper.py -n gtx1080ti -mp 300 -p 5 -d chrome
```
