from flask import Flask, redirect, url_for, request, render_template
from bs4 import BeautifulSoup
import requests
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

        # checkin_all = checkin_date.split("-")
        # checkin_year, checkin_month, checkin_day = int(checkin_all[0]), int(checkin_all[1]), int(checkin_all[2])
        # dateFrom = date(checkin_year, checkin_month, checkin_day)
        # checkout_all = checkout_date.split("-")
        # checkout_year, checkout_month, checkout_day = int(checkout_all[0]), int(checkout_all[1]), int(checkout_all[2])
        # dateTo = date(checkout_year, checkout_month, checkout_day)
        # night = (dateTo-dateFrom).days

        name_list = []
        desc_list = []
        bed_list = []
        rate_list = []
        review_list = []
        unit_list = []
        total_list = []
        link_list = []
        master_list = []

        if " " in ci:
            state_clean = ci.split(" ")
            city1 = state_clean[0]
            city2 = state_clean[1]
        #     website = f'https://www.airbnb.com/s/{city1}-{city2}/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&price_filter_input_type=0&price_filter_num_nights={night}&channel=EXPLORE&date_picker_type=calendar&checkin={checkin_date}&checkout={checkout_date}&source=structured_search_input_header&search_type=filter_change&adults={num_gue}'
        # else:
        #     website = f'https://www.airbnb.com/s/{ci}/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&price_filter_input_type=0&price_filter_num_nights={night}&channel=EXPLORE&date_picker_type=calendar&checkin={checkin_date}&checkout={checkout_date}&source=structured_search_input_header&search_type=filter_change&adults={num_gue}'
           
            website = f'https://www.airbnb.com/s/{city1}-{city2}/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&price_filter_input_type=0&channel=EXPLORE&date_picker_type=calendar&checkin={checkin_date}&checkout={checkout_date}&source=structured_search_input_header&search_type=filter_change&adults={num_gue}'
        else:
            website = f'https://www.airbnb.com/s/{ci}/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&price_filter_input_type=0&channel=EXPLORE&date_picker_type=calendar&checkin={checkin_date}&checkout={checkout_date}&source=structured_search_input_header&search_type=filter_change&adults={num_gue}'
         
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
            listings = soup.find_all('div', class_ = 'c4mnd7m atm_9s_11p5wf0 atm_dz_1osqo2v dir dir-ltr')

            for index, listing in enumerate(listings):
                name = listing.find('div', class_ ='t1jojoys atm_g3_1kw7nm4 atm_ks_15vqwwr atm_sq_1l2sidv atm_9s_cj1kg8 atm_6w_1e54zos atm_fy_1vgr820 atm_7l_18pqv07 atm_cs_qo5vgd atm_w4_1eetg7c atm_ks_zryt35__1rgatj2 dir dir-ltr').text
                desc = listing.find('span', class_ = 't6mzqp7 atm_g3_1kw7nm4 atm_ks_15vqwwr atm_sq_1l2sidv atm_9s_cj1kg8 atm_6w_1e54zos atm_fy_kb7nvz atm_7l_12u4tyr atm_am_qk3dho atm_ks_zryt35__1rgatj2 dir dir-ltr').text
                desc = desc.replace(",","+")

                ### rating session start
                rate_review = listing.find('span', class_ ='r1dxllyb atm_7l_18pqv07 atm_cp_1ts48j8 dir dir-ltr')     
                if rate_review == None:
                    rate = listing.find('span', class_ ='r1dxllyb atm_7l_18pqv07 atm_cp_1ts48j8 dir dir-ltr')
                    review = 'None'
                elif rate_review.text == 'New':
                    rate = listing.find('span', class_ ='r1dxllyb atm_7l_18pqv07 atm_cp_1ts48j8 dir dir-ltr').text
                    review = 'None'
                else:
                    rate = rate_review.text.split(" ")[0]
                    review = rate_review.text.split(" ")[1]
                    review = review[1:-1]
                 
                if rate == 'New' or rate == 'None'or rate == None:
                    rate = 0
                if review == 'None':
                    review = 0
                else:
                    review = int(review)
                ### rating session end

                # ### bed&bath session start
                desc_beds = listing.find_all('div',class_='fb4nyux atm_da_cbdd7d s1cjsi4j atm_g3_1kw7nm4 atm_ks_15vqwwr atm_sq_1l2sidv atm_9s_cj1kg8 atm_6w_1e54zos atm_fy_kb7nvz atm_7l_12u4tyr atm_ks_zryt35__1rgatj2 dir dir-ltr')
                if len(desc_beds) == 2:
                    bed = desc_beds[1].text
                elif len(desc_beds) == 1:
                    bed = "N/A"
                # bed = bed.replace(",","")
                reform = [',', '·',' ']
                for sym in bed:
                    if sym in reform:
                        bed = bed.replace(sym," & ")
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

                reformat = [',', '$',' ']
                for char1 in price_per_night:
                    if char1 in reformat:
                        price_per_night = price_per_night.replace(char1,"")
                price_per_night=int(price_per_night)
                ## price end

                total_price = listing.find('div', class_= '_tt122m').text.split(" ")[0]
                for char in total_price:
                    if char in reformat:
                        total_price = total_price.replace(char,"")
                total_price = int(total_price)
                
                # set the total price filter
                if total_price < int(target_pri):
                    master_list.append([name, desc, bed, rate, review, price_per_night, total_price, more_info])
        # master_list.sort(key=lambda x: x[6])
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

