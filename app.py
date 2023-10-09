from flask import Flask, redirect, url_for, request, render_template
from bs4 import BeautifulSoup
import requests
import json
from datetime import date
 
app = Flask(__name__)

@app.route('/')
def homepage():
   return render_template('index.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        ci = request.form['city']
        checkin_date = request.form['checkin']
        checkout_date = request.form['checkout']
        num_gue = request.form['num_people']
        target_pri = request.form['target_price']
        if " " in ci:
            ci_1 = ci.split(" ")[0].capitalize()
            ci_2 = ci.split(" ")[1].capitalize()
            ci = ci_1 + " " + ci_2
        else:
            ci = ci.capitalize()

        checkin_all = checkin_date.split("-")
        checkin_year, checkin_month, checkin_day = int(checkin_all[0]), int(checkin_all[1]), int(checkin_all[2])
        dateFrom = date(checkin_year, checkin_month, checkin_day)
        checkout_all = checkout_date.split("-")
        checkout_year, checkout_month, checkout_day = int(checkout_all[0]), int(checkout_all[1]), int(checkout_all[2])
        dateTo = date(checkout_year, checkout_month, checkout_day)
        night = (dateTo-dateFrom).days

        name_list = []
        desc_list = []
        bed_list = []
        rate_list = []
        review_list = []
        unit_list = []
        total_list = []
        link_list = []
        master_list = []

        ### travel date range end
        with open('city_state.json') as user_file:
            parsed_json = json.load(user_file)
            state = parsed_json[ci]
        
        with open('state_abbr.json') as abbr_file:
            parsed_json = json.load(abbr_file)
            S = parsed_json[state]   

        if " " in ci:
            state_clean = ci.split(" ")
            city1 = state_clean[0]
            city2 = state_clean[1]
            website = f'https://www.airbnb.com/s/{city1}-{city2}--{state}--United-States/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&price_filter_input_type=0&price_filter_num_nights={night}&channel=EXPLORE&query={city1}%20{city2}%2C%20{S}&date_picker_type=calendar&checkin={checkin_date}&checkout={checkout_date}&source=structured_search_input_header&search_type=filter_change&adults={num_gue}'
        else:
            website = f'https://www.airbnb.com/s/{ci}--{state}--United-States/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&price_filter_input_type=0&price_filter_num_nights={night}&channel=EXPLORE&query={ci}%2C%20{S}&date_picker_type=calendar&checkin={checkin_date}&checkout={checkout_date}&source=structured_search_input_header&search_type=filter_change&adults={num_gue}'


        while website:
            html_text = requests.get(website).content
            soup = BeautifulSoup(html_text, 'html.parser')
            if not soup.find('a', attrs={"aria-label":"Next"}):
                next_page = None
            else:
                next = soup.find('a', attrs={"aria-label":"Next"})['href']
                next_page = f'https://www.airbnb.com{next}'
            website = next_page

            # scraper starts here
            listings = soup.find_all('div', class_ = 'c4mnd7m dir dir-ltr')

            for index, listing in enumerate(listings):
                name = listing.find('div', class_ ='t1jojoys dir dir-ltr').text 
                desc = listing.find('meta', itemprop ='name')['content']
                desc = desc.replace(",","+")

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
                    review = review[1:-1]
                ### rating session end

                # ### bed&bath session start
                beds = listing.find_all('div',class_='fb4nyux s1cjsi4j dir dir-ltr')
                if len(beds) == 2:
                    bed = beds[1].text
                elif len(beds) == 1:
                    bed = "N/A"
                bed = bed.replace(",","")
                # ### bed&bath session end
                
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
                
                # set the total price filter
                # target_price = 1500
                if int(total_price_str) < int(target_pri):
                    master_list.append([name, desc, bed, rate, review, price_per_night, total_price, more_info])
        master_list.sort(key=lambda x: x[6])
        for i in master_list:
            name_list.append(i[0])
            desc_list.append(i[1])
            bed_list.append(i[2])
            rate_list.append(i[3])
            review_list.append(i[4])
            unit_list.append(i[5])
            total_list.append(i[6])
            link_list.append(i[7])         
        return render_template('result.html', len_=len(link_list), name_list=name_list, desc_list=desc_list, bed_list=bed_list, rate_list=rate_list, review_list=review_list, unit_list=unit_list, total_list=total_list, link_list = link_list)
    else:
        return homepage()
    
if __name__ == '__main__':
    app.run(debug = True)

