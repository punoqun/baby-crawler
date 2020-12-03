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

## Internal Calculations
### Food Score
Food score is a completely relative scoring system based on the reviews and the restaurants' flavor scorings. 

It's calculated as follows:

Favorite food items have 10.0 base score while all others have 5.0, then for every comment in the selected time frame; if that comment has a perfect flavor scoring it adds a point for every food item on that restaurants menu, and then if the comment has a spesific name of a food item and has above average flavor scoring (it was 6.958 for all comments in my database I rounded it to 7.0) that item's score is incremented by 2, and all other related items (if pepperoni pizza gets mentioned pepperoni pizza's score increments by 2.0 and all other pizza's gets incremented by 1.0).

If the comment has below the 20 percentile (it was 3.84 for all comments I rounded up to 4.0) it does the opposite of the above, and if it has 1.0 flavor score it decreases all food scores by 1.0 for that restaurant.

While displaying the food items every food score is multiplied by the restaurants' flavor score then it gets scaled between 0 and 5. Which means if you see a score of 5.0 for one food item and 4.0 from another that means the first one is %20 better than the second one.

When comparing districts or restaurants the food score average is displayed without getting scaled between 0-5, this ensures that if a restaurant has a score of 1.5 and another has 1.75, we can safely say 1.75 is objectively better than 1.5. These scorings however shouldn't be compared outside the actual comparison window because of it's relation to the other selected restaurants. 

**Which also means getting a score of 1.75/5 is not inheritely bad thing and should not be assumed as such. It is relative to the other food items and it represents the overall positive feedback between them**

## Screenshots
**Default uses (Get Dishes and Comparison):**
![Alt text](https://i.ibb.co/YW80mTJ/image.png "Non-filter \"Get Dishes\" and \"Comparison\"")
**Analysis:**
![Alt text](https://i.ibb.co/WkWJdCS/image.png "Analysis")
