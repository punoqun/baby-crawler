#!/usr/bin/env python
# coding: utf-8

# In[1]:


import warnings
import time
import pandas as pd
import re
import os
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from multiprocessing.pool import ThreadPool

# In[2]:


import mechanicalsoup


# In[3]:


# def getBrowser():
#     global browser
#     return browser


# In[4]:


def openUrl(url):
    browser = mechanicalsoup.StatefulBrowser(soup_config={'features': 'lxml'})
    job = url[url.find('/', 9)+1:]
    i = 1
    while str(browser.open(url)) != '<Response [200]>':
        warnings.warn('Couldn\'t ' + job + ' ' + str(i) + ' times.')
        i += 1
        if i == 5:
            raise ConnectionError('Couldn\'t open ' + job + ' ' + str(i) + ' times.')
    return browser


# In[5]:


def getCities():
    browser = openUrl('https://www.yemeksepeti.com/sehir-secim')
    cities_soup = browser.get_current_page()
    cities = cities_soup.find_all(attrs={'class':'cityLink'})
    city_list = []
    for iter_city in range(len(cities)):
        city = cities[iter_city]
        city_link = city.attrs['href']
        city_name = str(city.attrs['data-catalog'])
        if '_' in city_name:
            city_name = city_name[city_name.find('_')+1:]
        city_name = city_name[0] + city_name[1:].lower()
        city_list.append([city_name, city_link])
    return city_list


# In[6]:


def getDistricts(city_name, city_link):
    browser = openUrl('https://www.yemeksepeti.com' + str(city_link) + '/restoran-arama')
    city_soup = browser.get_current_page()
    districts = city_soup.find_all('option')
    district_list = []
    for iter_dist in range(2, len(districts)):
        district_name = city_soup.find_all('option')[iter_dist].attrs['data-area-name']
        district_url = city_soup.find_all('option')[iter_dist].attrs['data-url']
        district_list.append([district_name, district_url])
    return district_list


# In[7]:


def getRestaurants(district_name, district_url):
    browser = openUrl('https://www.yemeksepeti.com' + str(district_url))# + '#ors:false')
    #TODO: untick the 'open' box
    dist_soup = browser.get_current_page()
    restaurants = dist_soup.find_all(attrs={'class': 'restaurantName'})
    restaurant_list = []
    for rest_iter in range(len(restaurants)):
        restaurant_name = restaurants[rest_iter].contents[1].contents[0].split(',')[0]
        restaurant_url = restaurants[rest_iter].attrs['href']
        restaurant_list.append([restaurant_name, restaurant_url])
    return restaurant_list


# In[8]:


def getComments(restaurant_name, restaurant_link):
    comment_list = []
    for iter_page in range(1,200):
        browser = openUrl('https://www.yemeksepeti.com' + restaurant_link + '?section=comments&page=' + str(iter_page))
        current_page = browser.get_url().split("page=")[1]
        x = re.search("^\d", current_page) 
        if iter_page != int(current_page[x.start():x.end()]):
            break
        comments_soup = browser.get_current_page()
        comments = comments_soup.find_all(attrs={'class':'comments-body'})
        for iter_comment in range(len(comments)):
            comment = comments[iter_comment]
            if comment.find('div',attrs={'class':'userName'}).contents[0] == ' Restoran Cevabı\r':
                continue
            try:
                comment_text = comment.p.contents[0]
                comment_speed = comment.find(attrs={'class':'speed'}).contents[0].split(': ')[1]
                comment_service = comment.find(attrs={'class':'serving'}).contents[0].split(': ')[1]
                comment_taste = comment.find(attrs={'class':'flavour'}).contents[0].split(': ')[1]

                comment_speed = float(comment_speed.replace(',', '.'))
                comment_service = float(comment_service.replace(',', '.'))
                comment_taste = float(comment_taste.replace(',', '.'))

                comment_time_text = comment.find(attrs={'class':'commentDate'}).div.contents[0]
                if 'gün önce' in comment_time_text:
                    comment_time = int(time.time()) - (int(comment_time_text[:comment_time_text.find(' ')]) * 86400)
                elif 'ay önce' in comment_time_text:
                    comment_time = int(time.time()) - (int(comment_time_text[:comment_time_text.find(' ')]) * 2629746)
                elif 'yıl önce' in comment_time_text:
                    comment_time = int(time.time()) - (int(comment_time_text[:comment_time_text.find(' ')]) * 2629746 * 12)
                else:
                    comment_time = int(time.time())
                
                comment_list.append([comment_text, comment_speed, comment_service, comment_taste, comment_time])
                
            except:
                continue

    return comment_list


# In[9]:


def update_food_scores(comment_list, every_food):
    for comment_text, _, _, comment_taste, _ in comment_list:
        for food_idx in range(len(every_food)):
            food_id, food_name, food_price, food_category, food_score  = every_food[food_idx]
            if comment_taste == 10.0:
                food_score += 1.0
            elif comment_taste < 3.0:
                food_score -= 1.0
            for food_particule in food_name.split(' '):
                for comment_particule in comment_text.split(' '):
                    if food_particule in comment_particule:
                        if comment_taste > 7.0:
                            food_score += 1.0
                        else:
                            food_score -= 1.0
                        every_food[food_idx] = food_id, food_name, food_price, food_category, food_score
    return every_food


# In[10]:


def getDishes(restaurant_name, restaurant_link):
    browser = openUrl('https://www.yemeksepeti.com' + restaurant_link)
    restaurant_soup = browser.get_current_page()
    try:
        points = restaurant_soup.find(attrs={'class': 'points'})
        speed = points.find_all('span')[1].contents[0]
        service = points.find_all('span')[3].contents[0]
        taste = points.find_all('span')[5].contents[0]

        speed = float(speed.replace(',', '.'))
        service = float(service.replace(',', '.'))
        taste = float(taste.replace(',', '.'))
    except:
        return [],[],[],[]
    restaurant_metadata = [[restaurant_name, speed, service, taste, time.time()]]
    
    favorites = []
    fav_foods = restaurant_soup.find_all(attrs={'class': 'restaurantDetailBox favFoods'})[0].contents[3]
    for iter_food in range(len(fav_foods)):
        try:
            food_name = fav_foods.find_all(attrs={'class':'product'})[iter_food].contents[1].contents[1].contents[0]
            # if ' (' in food_name:
            #     food_name = food_name.split(' (')[0]
            
            if len(food_name) < 2:
                continue
            food_id = fav_foods.find_all(attrs={'class':'product'})[iter_food].contents[1].contents[1].attrs['data-product-id']
            food_price = fav_foods.find_all(attrs={'class':'price'})[iter_food].contents[0]
            favorites.append([food_id, food_name, food_price])
        except IndexError:
            continue

    every_food = []
    all_food_boxes = restaurant_soup.find_all(attrs={'class': 'restaurantDetailBox None'})
    
    for iter_box in range(len(all_food_boxes)):
        if all_food_boxes[iter_box].div.attrs['class'] != ['head', 'white']:
            continue
        food_box = all_food_boxes[iter_box]
        foods_in_box = food_box.find_all(attrs={'class':'product'})
        for iter_food in range(len(foods_in_box)):
            try:
                food_name = foods_in_box[iter_food].contents[1].contents[1].contents[0]
                if len(food_name) < 2:
                    continue
                food_id = foods_in_box[iter_food].contents[1].contents[1].attrs['data-product-id']
                food_price = food_box.find_all(attrs={'class':'price'})[iter_food].contents[0]
                food_category = food_box.b.contents[0]
                if food_id in str(favorites):
                    food_score = 10.0
                else:
                    food_score = 5.0
                every_food.append([food_id, food_name, food_price, food_category, food_score])
            except IndexError:
                continue
    
    comment_list = getComments(restaurant_name, restaurant_link)

    every_food = update_food_scores(comment_list, every_food)

    return restaurant_metadata, every_food, favorites, comment_list


# In[11]:


def makeTheDirs(city_name, district_name, restaurant_name):
    path = 'data/' + city_name + '/' + district_name + '/'+ restaurant_name
    os.makedirs(path)
    return path


# In[12]:


def myLoop(thread=0, thread_count=1,start=0):
    while(True):
        cities = getCities()
        for city_idx in range(start, len(cities), thread_count):
            city_name, city_link = cities[city_idx]
            for district_name, district_link in getDistricts(city_name, city_link):
                try:
                    for restaurant_name, restaurant_link in getRestaurants(district_name, district_link):
                        try:
                            try:
                                path = makeTheDirs(city_name, district_name, restaurant_name)
                            except FileExistsError:
                                continue
                            restaurant_metadata, every_food, favorites, comment_list = getDishes(restaurant_name, restaurant_link)

                            restaurant = pd.DataFrame(restaurant_metadata, columns=['restaurant_name', 'speed', 'service', 'taste', 'update_date'])
                            foods = pd.DataFrame(every_food, columns=['food_id', 'food_name', 'food_price', 'food_category', 'food_score'])
                            favs = pd.DataFrame(favorites, columns=['food_id', 'food_name', 'food_price'])
                            comments = pd.DataFrame(comment_list, columns=['comment_text', 'comment_speed', 'comment_service', 'comment_taste', 'comment_time'])

                            restaurant.to_csv((path + '/restaurant_metadata.csv'), index=False)
                            foods.to_csv((path + '/foods.csv'), index=False)
                            favs.to_csv((path + '/favorites.csv'), index=False)
                            comments.to_csv((path + '/comments.csv'), index=False)
                        except :
                            continue
                except:
                    continue

# In[3]:


def updateRestaurant(city, dist, rest):
    path = './data/'+city+'/'+dist+'/'+rest
    cities = getCities()
    for c in cities:
        if c[0] == city:
            city_link = c[1]
            break
    
    districts = getDistricts(city, city_link)

    for d in districts:
        if d[0] == dist:
            dist_link = d[1]
            break
    
    restaurants = getRestaurants(dist, dist_link)
    for r in restaurants:
        if r[0] == rest:
            rest_link = r[1]
            break
    restaurant_metadata, every_food, favorites, comment_list = getDishes(rest, rest_link)

    restaurant = pd.DataFrame(restaurant_metadata, columns=['restaurant_name', 'speed', 'service', 'taste', 'update_date'])
    foods = pd.DataFrame(every_food, columns=['food_id', 'food_name', 'food_price', 'food_category', 'food_score'])
    favs = pd.DataFrame(favorites, columns=['food_id', 'food_name', 'food_price'])
    comments = pd.DataFrame(comment_list, columns=['comment_text', 'comment_speed', 'comment_service', 'comment_taste', 'comment_time'])

    restaurant.to_csv((path + '/restaurant_metadata.csv'), index=False)
    foods.to_csv((path + '/foods.csv'), index=False)
    favs.to_csv((path + '/favorites.csv'), index=False)
    comments.to_csv((path + '/comments.csv'), index=False)

    


# In[23]:


def localDishesnComments(city, dist='', rest='',min=0,max=5,sort_rest=False,date='Year'):
    
    # print(city, dist, rest)
    path = './data/'+city+'/'+dist+'/'+rest
    # print(path)
    ret_foods = pd.DataFrame()
    for root, _, files in os.walk(path):

        if 'foods.csv' in files:
            restaurant = root[root.rfind('/')+1:]
            l_foods = pd.read_csv(root+'/foods.csv')
            
            if date != 'Year':
                fav_foods = pd.read_csv(root+'/favorites.csv')
                favs = str(fav_foods.values.tolist())
                comment_list = pd.read_csv(root+'/comments.csv').values.tolist()
                foods = filter_comments(comment_list, l_foods.values.tolist(), date=date, favs=favs)
                # print(foods)
                l_foods = pd.DataFrame(foods,columns=['food_id', 'food_name', 'food_price', 'food_category', 'food_score'])
            l_foods['rest_name'] = restaurant
            ret_foods = pd.concat((ret_foods,l_foods),axis=0)

    # global r
    # r = ret_foods
    # print(ret_foods.values)
    y = MinMaxScaler((0,5)).fit_transform(ret_foods[['food_score']])
    y = np.around(y,2)
    ret_foods[['food_score']] = y
    ret_foods.sort_values(by='food_score',inplace=True, ascending=False)
    if sort_rest:
        ret_foods.sort_values(by=['rest_name','food_score',],inplace=True, ascending=[True,False])
    ret_foods = ret_foods[ret_foods['food_score'].between(min, max)]

    restaurant_ = ret_foods['rest_name']
    ret_foods.drop(['food_id','food_category','rest_name'],axis=1,inplace=True)
    ret_foods = pd.concat((restaurant_,ret_foods),axis=1)
    return ret_foods


# In[19]:



def filter_comments(comment_list, every_food, date='Year', favs=''):
    for food_idx in range(len(every_food)):
        food_id, food_name, food_price, food_category, food_score  = every_food[food_idx]
        if food_id in favs:
            food_score =10
        else: 
            food_score = 5
        every_food[food_idx] = food_id, food_name, food_price, food_category, food_score

    update_time = comment_list[0][4]
    for comment_text, _, _, comment_taste, comment_time in comment_list:
        if date != 'Year':
            if date == 'Day':
                if abs(update_time - comment_time) > 86400:
                    break
                
            elif date == 'Week':
                if abs(update_time - comment_time) > 86400*7:
                    break
            elif date == 'Month':
                if abs(update_time - comment_time) > 86400*30:
                    break
        for food_idx in range(len(every_food)):
            food_id, food_name, food_price, food_category, food_score  = every_food[food_idx]
            if comment_taste == 10.0:
                food_score += 1.0
            elif comment_taste < 3.0:
                food_score -= 1.0
            for food_particule in food_name.split(' '):
                for comment_particule in comment_text.split(' '):
                    if food_particule in comment_particule:
                        if comment_taste > 7.0:
                            food_score += 1.0
                        else:
                            food_score -= 1.0
                        every_food[food_idx] = food_id, food_name, food_price, food_category, food_score

    return every_food


# In[15]:


def join_multiple(city,dist,rest,min=0,max=5,sort_rest=False,date='Year'):
    ret = pd.DataFrame()
    # print(rest)
    if rest[0] == '':
        for d in dist:
            print(d)
            added = localDishesnComments(city, d, rest='',min=min,max=max,sort_rest=sort_rest,date=date)
            ret = pd.concat((ret,added),axis=0)
            
    if len(rest) != 0:
        for d in rest:
            added = localDishesnComments(city, dist, rest=d,min=min,max=max,sort_rest=sort_rest,date=date)
            ret = pd.concat((ret,added),axis=0)
    return ret

def do_analysis(city, dist='', rest=''):
    
    # print(city, dist, rest)
    path = './data/'+city+'/'+dist+'/'+rest
    # print(path)
    ret_foods = pd.DataFrame()
    for root, _, files in os.walk(path):

        if 'foods.csv' in files:
            restaurant = root[root.rfind('/')+1:]
            l_foods = pd.read_csv(root+'/foods.csv')
            comment_list = pd.read_csv(root+'/comments.csv').values.tolist()
            occurence = analysis(comment_list, l_foods.values.tolist())
            occurence = pd.DataFrame(occurence,columns =['Food','Ordered on'])
            occurence['rest_name'] = restaurant
            ret_foods = pd.concat((ret_foods,occurence),axis=0)


    restaurant_ = ret_foods['rest_name']
    ret_foods.drop(['rest_name'],axis=1,inplace=True)
    ret_foods = pd.concat((restaurant_,ret_foods),axis=1)
    return ret_foods


# In[19]:



def analysis(comment_list, every_food):
    update_time = comment_list[0][4]
    food_anal = []
    for comment_text, _, _, _, comment_time in comment_list:

        if abs(update_time - comment_time) > 86400*100:
            break
        for food_idx in range(len(every_food)):
            try:
                _, food_name, _, _, _  = every_food[food_idx]
                for food_particule in food_name.split(' '):
                    for comment_particule in comment_text.split(' '):
                        if food_particule in comment_particule:
                            food_anal.append([food_name, comment_time])
                            raise Exception('found one')
            except:
                break

    return food_anal

    
def multithread(thread_count=1,start=0):
    pool = ThreadPool(thread_count)
    pool.map(myLoop, range(thread_count),start)