# baby-crawler
Yet another Yemeksepeti crawler, but with complete gui and half-crawled data. Made as a BIL573 project.
##  Installation
**1-** Clone, or Download and extract, the repository into your selected directory.

**2-** Navigate into the directory with a shell.

**3-** Install the prerequisites with the following:
```
pip install -r requirements.txt
```
**4-** When the installation completes, execute ``` python gui.py``` to run the program.

## Usage
**1-** Run the program with ```python gui.py```

**2-** Clicking the first empty table with the **Cities** title will fill the said table with the locally stored city list.

**3-** Selecting a city will list the avaible districts of the said city in the **Districts** table.

**4-** Selecting one or multiple districts will fill the **Restaurants** table with the available restaurants from the selected district(s).

**5-** On the right there are few buttons.

  ```Get Dishes```: will fill the bigger table at the bottom with food info from selected city, district(s) or restaurant(s).
  
  You can ```Filter``` these results with the filters below:
  
    Min: min score
    Max: max score
    Date: only comments from the selected time period will affect the food scores
    Sort by A-Z: sorts the table by restaurant names rather than food score
    
  ```Compare```: fills the smaller table at the bottom with the selected district(s) or restaurant(s) and their average food scores. Checking **Filter Comparison** before clicking ```Compare``` will filter the compared foods with the filters selected above.
  
  ```Analysis```: will print a order/time graphic for the most popular food in the selected restaurant. 
  
  ```Update```: updates the stored data for the selected restaurant(s) from the website.
  
  ```Crawl```: starts updating the whole database, checking **Continue crawl from selected** will start the crawling from the selected city, choosing a thread count will multithread the crawl process by the selected amount. (Multithreading is discouraged because of it triggers the ddos protections)


## Screenshots
![Alt text](https://i.ibb.co/YW80mTJ/image.png "Non-filter \"Get Dishes\" and \"Comparison\"")
