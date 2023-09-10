from bs4 import BeautifulSoup
import requests
import json
import csv
from datetime import date
import pandas as pd

def get_hotel(html_text, round, target_price):
    listings = soup.find_all('div', class_ = 'c4mnd7m dir dir-ltr')
   
    for index, listing in enumerate(listings):
        name = listing.find('div', class_ ='t1jojoys dir dir-ltr').text 
        desc = listing.find('meta', itemprop ='name')['content']

        ### rating session start
        rate_review = listing.find('span', class_ ='r1dxllyb dir dir-ltr')
        if rate_review == None:
            rate = listing.find('span', class_ ='r1dxllyb dir dir-ltr')
            review = 'None'
        elif rate_review.text == 'New':
            rate = listing.find('span', class_ ='r1dxllyb dir dir-ltr').text
            review = 'None'
        else:
            rate = rate_review.text.split(" ")[0]
            review = rate_review.text.split(" ")[1]
        ### rating session end

        ### listing link session start
        more_info = listing.find('meta', itemprop = 'url')["content"]
        ### listing link session end

        ### price start
        price = listing.find('div', class_= '_1jo4hgw').text.split("\xa0")
        if len(price) == 2:
            price_per_night = price[0]
        else:
            price_per_night = price[1]
        ## price end

        total_price = listing.find('div', class_= '_tt122m').text.split(" ")[0]
        total_price_str = ""
        for char in total_price:
            if str.isnumeric(char):
                total_price_str += char

        # set the total price filter start
        if int(total_price_str) < target_price:
            with open('result__.csv', 'a', encoding='UTF8', newline='') as f:
                fieldnames = ['description', 'rating','reviews', 'price_per_night','total_price','link']      
                writer = csv.DictWriter(f, fieldnames = fieldnames)
                data = {'description':desc.strip(), 'rating': rate, 'reviews': review, 'price_per_night':price_per_night, 'total_price':total_price, 'link':more_info}
                writer.writerow(data)
        # set the total price filter end

    return find_next(html_text)

def find_next(html_text):
    if not soup.find('a', attrs={"aria-label":"Next"}):
        next_page = None
    else:
        next = soup.find('a', attrs={"aria-label":"Next"})['href']
        next_page = f'https://www.airbnb.com{next}'
    website = next_page
    return website

if __name__ == '__main__':
    # input start
    print(f'\nAirbnb Listing Search App')
    city = str(input(f'Enter the city/island: '))
    checkin = str(input(f'Enter checkin date(seperate with -, ex: 2023-03-12): '))
    checkout = str(input(f'Enter checkout date(seperate with -, ex: 2023-03-18): '))
    num_people = int(input(f'Enter the number of guests: '))
    target_price = int(input(f'Enter the desired total price(tax excluded): '))
    print(f'\nLoading now...Please wait...')
    # input end

    ### travel date range start
    checkin_all = checkin.split("-")
    checkin_year, checkin_month, checkin_day = int(checkin_all[0]), int(checkin_all[1]), int(checkin_all[2])
    dateFrom = date(checkin_year, checkin_month, checkin_day)
    checkout_all = checkout.split("-")
    checkout_year, checkout_month, checkout_day = int(checkout_all[0]), int(checkout_all[1]), int(checkout_all[2])
    dateTo = date(checkout_year, checkout_month, checkout_day)
    night = (dateTo-dateFrom).days
    ### travel date range end

    with open('city_state.json') as user_file:
        parsed_json = json.load(user_file)
        state = parsed_json[city]

    with open('state_abbr.json') as abbr_file:
        parsed_json = json.load(abbr_file)
        S = parsed_json[state]   

    if " " in city:
        state_clean = city.split(" ")
        city1 = state_clean[0]
        city2 = state_clean[1]
        website = f'https://www.airbnb.com/s/{city1}-{city2}--{state}--United-States/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&price_filter_input_type=0&price_filter_num_nights={night}&channel=EXPLORE&query={city1}%20{city2}%2C%20{S}&date_picker_type=calendar&checkin={checkin}&checkout={checkout}&source=structured_search_input_header&search_type=filter_change&adults={num_people}'
    else:
        website = f'https://www.airbnb.com/s/{city}--{state}--United-States/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&price_filter_input_type=0&price_filter_num_nights={night}&channel=EXPLORE&query={city}%2C%20{S}&date_picker_type=calendar&checkin={checkin}&checkout={checkout}&source=structured_search_input_header&search_type=filter_change&adults={num_people}'
    
    with open("result__.csv",'w') as file:
        pass    
    round = 0

    while website:
        html_text = requests.get(website).content
        soup = BeautifulSoup(html_text, 'html.parser')
        round += 1
        website = get_hotel(html_text, round, target_price)

path = 'result__.csv'
df = pd.read_csv(path)
df.to_csv(path, header = ['description', 'rating','reviews','price_per_night','total_price','link'], index=False)
df = pd.read_csv(path)
df = pd.DataFrame(df)
print(df)