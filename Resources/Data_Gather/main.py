import datetime
import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
base_url = "http://ufcstats.com/statistics/events/completed?page=all"


# Instantiating the list to hold the URL of each fight of each event
url_fight_list = []
empty_list = []

#Funtion created to scrape the URLs needed for fight data1
def url_scraper(URL):

    # Instantiating the list to hold fight event URLs from base_url
    url_event_list = []
    # Requesting page
    page = requests.get(URL)
    # Parsing page content
    soup = BeautifulSoup(page.content, "html.parser")

    # Found the one and only table on the page, which contains each event in a "row"
    event_table = soup.find("table", {"class": "b-statistics__table-events"})

    # USER MESSAGE
    print("Extracting Event URLs...")

    # Finding all of the <a> tags within the table, which contain the event url
    for td in event_table.find_all("a")[1:]:

        # Using .get("href") to grab the url and assigning it to "link"
        link = td.get("href")

        # Checking if url is already in url_event_list, if NOT, appends it.
        if link not in url_event_list:
            url_event_list.append(link)


    # USER MESSAGE

    print("Event URL Extraction COMPLETE. Moving on...\nExtracting fight stat URLs...")


    # Looping through url_event_list to grab the urls associated with each fight
    # Essentially the same as scraping for url_event_list above
    for url in url_event_list:
        event_page = requests.get(url)
        soup = BeautifulSoup(event_page.content, "html.parser")
        fight_table = soup.find("table", {"class": "b-fight-details__table b-fight-details__table_style_margin-top b-fight-details__table_type_event-details js-fight-table"})

        for td in fight_table.find_all("a", {"class": "b-flag b-flag_style_green"}):
            fight_link = td.get("href")
            if fight_link not in url_fight_list:
                url_fight_list.append(fight_link)



    with open("new_scraped_urls.txt", "w") as w:
        for link in url_fight_list:
            w.write(str(link) + "\n")



    # USER MESSAGE
    print("Fight stat URL Extraction COMPLETED.")




months = {"Jan": 1,
          "Feb": 2,
          "Mar": 3,
          "Apr": 4,
          "May": 5,
          "Jun": 6,
          "Jul": 7,
          "Aug": 8,
          "Sep": 9,
          "Oct": 10,
          "Nov": 11,
          "Dec": 12
          }


fight_stat_list =[]

# Function that intakes the fight urls and gathers stats.
def stat_scraper(fight_list):
    new_scraped_list = []
    prev_scraped_list = []
    new_fight_list = []

    with open("new_scraped_urls.txt", "r") as r:
        for link in r:
            new_scraped_list.append(link.strip())

    with open("prev_scraped_urls.txt", "r") as r:
        for link in r:
            prev_scraped_list.append(link.strip())

    for url in new_scraped_list:
        if url in prev_scraped_list:
            print("already in list")
        else:
            new_fight_list.append(url.strip())
    print(new_fight_list)

    # Looping through the urls in fight_list
    for url in new_fight_list:
        try :

            fight_stat_page = requests.get(url)
            stat_soup = BeautifulSoup(fight_stat_page.content, "html.parser")
            # Div that hold essentially all the pages elements
            fighter_name_main_div = stat_soup.find("div", {"class": "b-fight-details"})
            fight_event_date_header = stat_soup.find("h2", {"class": "b-content__title"}).find("a")
            fight_event_date_url = fight_event_date_header.get("href")
            event_date_page = requests.get(fight_event_date_url)
            event_date_soup = BeautifulSoup(event_date_page.content, "html.parser")
            event_date = event_date_soup.find("li", {"class": "b-list__box-list-item"}).text.replace("Date:","").strip()

            # Converting date to xx/xx/xxxx format
            event_date_convertions = "%B %d, %Y"
            event_date_converted = datetime.datetime.strptime(event_date,
                                                                    event_date_convertions)

            # Stripping excess
            event_date_cleaned = str(event_date_converted).strip("00:00:00").strip()



            event_date_split = event_date_cleaned.split("-")
            event_year, event_month, event_day = event_date_split[0], event_date_split[1], event_date_split[2]

            # Getting the weight class of the bout. Stripping "Bout", leaving only the weight class
            bout_weight_class = stat_soup.find("i", {"class": "b-fight-details__fight-title"}).text.replace("Bout", "").strip()


            # Getting fighter corner color
            red_fighter_div = fighter_name_main_div.find("i", {"class": "b-fight-details__charts-name b-fight-details__charts-name_pos_left js-chart-name"})
            blue_fighter_div = fighter_name_main_div.find("i", {"class": "b-fight-details__charts-name b-fight-details__charts-name_pos_right js-chart-name"})

            # fighter name assigned to corner color
            blue_fighter = blue_fighter_div.text.strip()
            red_fighter = red_fighter_div.text.strip()

            winner = ""
            blue_career_stat_url = ""
            red_career_stat_url = ""

            # Getting the winners name and career stat URL
            for div in fighter_name_main_div.find_all("div", {"class": "b-fight-details__person"}):

                # Getting career stat url for fighter
                fighter_href_div = div.find("a")
                fighter_career_name = fighter_href_div.text.strip()
                fighter_career_href = fighter_href_div.get("href")

                if fighter_career_name == blue_fighter:
                    blue_career_stat_url = fighter_career_href
                elif fighter_career_name == red_fighter:
                    red_career_stat_url = fighter_career_href


                fighter_header = div.find('i')
                header_text = fighter_header.text

                # Checks if header text contains "W" (Winner)
                if header_text.strip() == "W":
                    # If header text contains "W", the corrisponding name is extracted and assigned to "winner_name"
                    winner_text = div.find("a", {"class": {"b-link b-fight-details__person-link"}})
                    winner_name = winner_text.text.strip()

                    # Comparing "winner_namer" to each corner colors fighter name. If match, winner color is instantiated.
                    if winner_name == blue_fighter:
                        winner = "Blue"
                    elif winner_name == red_fighter:
                        winner = "Red"


            # Getting fight details div
            outcome_div = fighter_name_main_div.find("p", {"class":"b-fight-details__text"})

            # Checking <i> tag holding method of victory
            method_div = outcome_div.find("i", {"style": "font-style: normal"})

            fight_win_method = ""
            # Assigning "fight_win_method" through comparison
            if "Decision" in method_div.text:
               fight_win_method = "DEC"
            elif "KO/TKO" in method_div.text:
               fight_win_method = "KO/TKO"
            elif "Submission" in method_div.text:
                fight_win_method = "SUB"

            max_rounds = ""
            ending_round = ""

            # Getting the Round the fight ended and number of maximum possible rounds.
            for i in outcome_div.find_all("i", {"class": "b-fight-details__label"}):

                if "Round:" in i.text:
                    ending_round = i.next_sibling.text.strip()
                if "Time format:" in i.text:
                    max_rounds_split = i.next_sibling.text.split("Rnd")
                    max_rounds = max_rounds_split[0].strip()




            # CAREER STAT RETRIEVAL STARTS HERE
            # BLUE CORNER
            blue_career_stat_page = requests.get(blue_career_stat_url)
            blue_career_stat_soup = BeautifulSoup(blue_career_stat_page.content, "html.parser")
            blue_main_career_stats_ul = blue_career_stat_soup.find('ul', {'class': 'b-list__box-list'})
            blue_main_career_stats_li = blue_main_career_stats_ul.find_all('li', {'class': 'b-list__box-list-item b-list__box-list-item_type_block'})

            blue_fighter_Age = ''
            blue_fighter_Stance = ''
            blue_fighter_Reach = ''
            blue_fighter_Weight = ''
            blue_fighter_Height = ''
            blue_fighter_Wins = ''
            blue_fighter_Losses = ''
            blue_fighter_Draws = ''
            blue_fighter_SLpM = ''
            blue_fighter_Str_Acc = ''
            blue_fighter_SApM = ""
            blue_fighter_Str_Def = ""
            blue_fighter_Td_Avg = ""
            blue_fighter_Td_Acc = ""
            blue_fighter_Td_Def = ""
            blue_fighter_Sub_Avg = ""
            


            # getting fighters wins, losses and draws
            title = blue_career_stat_soup.find("h2", {"class": "b-content__title"})
            blue_fighter_record = title.select_one(":nth-child(2)")
            blue_fighter_WLD = blue_fighter_record.text.strip().strip('Record: ').split('-')
            blue_fighter_Wins, blue_fighter_Losses, blue_fighter_Draws = blue_fighter_WLD[0], blue_fighter_WLD[1], \
                                                                         blue_fighter_WLD[2]
            blue_age_month_clean = ""
            for li in blue_main_career_stats_li:

                # Finding the <i> tag thats within each <li> tag

                blue_stat = li.find('i', {'class': 'b-list__box-item-title b-list__box-item-title_type_width'})

                # Checking to see if "Height" exists within the <i> tag
                if "Height:" in blue_stat.text:
                    # If it is, fighterHeights is instantiated with the
                    # next sibling (In this case, the fighters height)
                    blue_fighter_height_dirty = blue_stat.next_sibling
                    # Reformatting by removing unwanted html
                    blue_fighter_height_clean = ''.join(c for c in blue_fighter_height_dirty if c.isalnum())

                    # Reformatting by adding the feet and inches symbols back into the fighters height
                    blue_fighter_Height_cleaned = blue_fighter_height_clean[:1] + "'" + blue_fighter_height_clean[1:] + '"'

                    inches_gathering = blue_fighter_Height_cleaned.split("'")
                    feet_to_inches = int(inches_gathering[0]) * 12
                    inches_cleaned = inches_gathering[1].replace('"', "")
                    blue_fighter_Height = int(feet_to_inches) + int(inches_cleaned)


                if "Weight:" in blue_stat.text:
                    blue_fighter_weight_dirty = blue_stat.next_sibling
                    blue_fighter_Weight = blue_fighter_weight_dirty.text.replace("lbs.","").strip()

                if "Reach:" in blue_stat.text:
                    blue_fighter_reach_dirty = blue_stat.next_sibling
                    blue_fighter_Reach = blue_fighter_reach_dirty.replace('"', "").strip()

                if "STANCE:" in blue_stat.text:
                    blue_fighter_Stance = blue_stat.next_sibling.text.strip()


                # Gets DOB and calculates age
                if "DOB:" in blue_stat.text:
                    blue_fighter_Age_dirty = blue_stat.next_sibling.text.strip()
                    blue_fighter_age_convertions = "%b %d, %Y"
                    blue_fighter_Age_converted = datetime.datetime.strptime(blue_fighter_Age_dirty,
                                                                          blue_fighter_age_convertions)

                    blue_fighter_Age_cleaned = str(blue_fighter_Age_converted).strip("00:00:00").strip()
                    blue_fighter_date_split = blue_fighter_Age_cleaned.split("-")
                    blue_fighter_age_year,blue_fighter_age_month,blue_fighter_age_day  = blue_fighter_date_split[0],\
                                                                                         blue_fighter_date_split[1],\
                                                                                         blue_fighter_date_split[2]


                    blue_fighter_Age = int(event_year) - int(blue_fighter_age_year) -((int(event_month), int(event_day)) < (int(blue_fighter_age_month), int(blue_fighter_age_day)))


                blue_career_stat_div = blue_career_stat_soup.find("div", {"class": "b-list__info-box-left clearfix"})
                middleCareerStats = blue_career_stat_div.find_all("i", {
                    "class": "b-list__box-item-title b-list__box-item-title_font_lowercase b-list__box-item-title_type_width"})
    
                for i in middleCareerStats:
    
                    if "SLpM:" in i.text:
                        blue_fighter_SLpM = i.next_sibling.text.strip()
    
                    if "Str. Acc.:" in i.text:
                        blue_fighter_Str_Acc = i.next_sibling.text.replace("%", "").strip()
    
                    if "SApM:" in i.text:
                        blue_fighter_SApM = i.next_sibling.text.strip()
    
                    if "Str. Def:" in i.text:
                        blue_fighter_Str_Def = i.next_sibling.text.replace("%", "").strip()
    
                    if "TD Avg.:" in i.text:
                        blue_fighter_Td_Avg = i.next_sibling.text.strip()
    
                    if "TD Acc.:" in i.text:
                        blue_fighter_Td_Acc = i.next_sibling.text.replace("%", "").strip()
    
                    if "TD Def.:" in i.text:
                        blue_fighter_Td_Def = i.next_sibling.text.replace("%", "").strip()
    
                    if "Sub. Avg.:" in i.text:
                        blue_fighter_Sub_Avg = i.next_sibling.text.strip()

            # RED CORNER
            red_career_stat_page = requests.get(red_career_stat_url)
            red_career_stat_soup = BeautifulSoup(red_career_stat_page.content, "html.parser")
            red_main_career_stats_ul = red_career_stat_soup.find('ul', {'class': 'b-list__box-list'})
            red_main_career_stats_li = red_main_career_stats_ul.find_all('li', {
                'class': 'b-list__box-list-item b-list__box-list-item_type_block'})

            red_fighter_Age = ''
            red_fighter_Stance = ''
            red_fighter_Reach = ''
            red_fighter_Weight = ''
            red_fighter_Height = ''
            red_fighter_Wins = ''
            red_fighter_Losses = ''
            red_fighter_Draws = ''
            red_fighter_SLpM = ''
            red_fighter_Str_Acc = ''
            red_fighter_SApM = ""
            red_fighter_Str_Def = ""
            red_fighter_Td_Avg = ""
            red_fighter_Td_Acc = ""
            red_fighter_Td_Def = ""
            red_fighter_Sub_Avg = ""

            # getting fighters wins, losses and draws
            title = red_career_stat_soup.find("h2", {"class": "b-content__title"})
            red_fighter_record = title.select_one(":nth-child(2)")
            red_fighter_WLD = red_fighter_record.text.strip().strip('Record: ').split('-')
            red_fighter_Wins, red_fighter_Losses, red_fighter_Draws = red_fighter_WLD[0], red_fighter_WLD[1], \
                                                                         red_fighter_WLD[2]
            red_age_month_clean = ""
            for li in red_main_career_stats_li:

                # Finding the <i> tag thats within each <li> tag

                red_stat = li.find('i', {'class': 'b-list__box-item-title b-list__box-item-title_type_width'})

                # Checking to see if "Height" exists within the <i> tag
                if "Height:" in red_stat.text:
                    # If it is, fighterHeights is instantiated with the
                    # next sibling (In this case, the fighters height)
                    red_fighter_height_dirty = red_stat.next_sibling
                    # Reformatting by removing unwanted html
                    red_fighter_height_clean = ''.join(c for c in red_fighter_height_dirty if c.isalnum())

                    # Reformatting by adding the feet and inches symbols back into the fighters height
                    red_fighter_Height_cleaned = red_fighter_height_clean[:1] + "'" + red_fighter_height_clean[
                                                                                        1:] + '"'

                    inches_gathering = red_fighter_Height_cleaned.split("'")
                    feet_to_inches = int(inches_gathering[0]) * 12
                    inches_cleaned = inches_gathering[1].replace('"', "")
                    red_fighter_Height = int(feet_to_inches) + int(inches_cleaned)

                if "Weight:" in red_stat.text:
                    red_fighter_weight_dirty = red_stat.next_sibling
                    red_fighter_Weight = red_fighter_weight_dirty.text.replace("lbs.", "").strip()

                if "Reach:" in red_stat.text:
                    red_fighter_reach_dirty = red_stat.next_sibling
                    red_fighter_Reach = red_fighter_reach_dirty.replace('"', "").strip()

                if "STANCE:" in red_stat.text:
                    red_fighter_Stance = red_stat.next_sibling.text.strip()

                # Gets DOB and calculates age
                if "DOB:" in red_stat.text:
                    red_fighter_Age_dirty = red_stat.next_sibling.text.strip()
                    red_fighter_age_convertions = "%b %d, %Y"
                    red_fighter_Age_converted = datetime.datetime.strptime(red_fighter_Age_dirty,
                                                                            red_fighter_age_convertions)

                    red_fighter_Age_cleaned = str(red_fighter_Age_converted).strip("00:00:00").strip()
                    red_fighter_date_split = red_fighter_Age_cleaned.split("-")
                    red_fighter_age_year, red_fighter_age_month, red_fighter_age_day = red_fighter_date_split[0], \
                                                                                          red_fighter_date_split[1], \
                                                                                          red_fighter_date_split[2]
                    red_fighter_Age = int(event_year) - int(red_fighter_age_year) - (
                                (int(event_month), int(event_day)) < (int(red_fighter_age_month), int(red_fighter_age_day)))



                red_career_stat_div = red_career_stat_soup.find("div", {"class": "b-list__info-box-left clearfix"})
                middleCareerStats = red_career_stat_div.find_all("i", {
                    "class": "b-list__box-item-title b-list__box-item-title_font_lowercase b-list__box-item-title_type_width"})

                for i in middleCareerStats:

                    if "SLpM:" in i.text:
                        red_fighter_SLpM = i.next_sibling.text.strip()

                    if "Str. Acc.:" in i.text:
                        red_fighter_Str_Acc = i.next_sibling.text.replace("%", "").strip()

                    if "SApM:" in i.text:
                        red_fighter_SApM = i.next_sibling.text.strip()

                    if "Str. Def:" in i.text:
                        red_fighter_Str_Def = i.next_sibling.text.replace("%", "").strip()

                    if "TD Avg.:" in i.text:
                        red_fighter_Td_Avg = i.next_sibling.text.strip()

                    if "TD Acc.:" in i.text:
                        red_fighter_Td_Acc = i.next_sibling.text.replace("%", "").strip()

                    if "TD Def.:" in i.text:
                        red_fighter_Td_Def = i.next_sibling.text.replace("%", "").strip()

                    if "Sub. Avg.:" in i.text:
                        red_fighter_Sub_Avg = i.next_sibling.text.strip()

                        
                        
                        
                        

            # Instantiating values here so they can be assigned to the dictionary
            Red_Significant_Strikes_Landed = ""
            Red_Significant_Strikes_Attempted = ""
            Blue_Significant_Strikes_Landed = ""
            Blue_Significant_Strikes_Attempted = ""
            Red_Significant_Strike_Perc = ""
            Blue_Significant_Strike_Perc = ""
            Red_Total_Strikes_Landed = ""
            Red_Total_Strikes_Attempted = ""
            Blue_Total_Strikes_Landed = ""
            Blue_Total_Strikes_Attempted = ""
            Red_Takedowns_Landed = ""
            Red_Takedowns_Attepmted = ""
            Blue_Takedowns_Landed = ""
            Blue_Takedowns_Attempted = ""
            Red_Takedown_Perc = ""
            Blue_Takedown_Perc = ""
            Red_Submissions_Attempted = ""
            Blue_Submissions_Attempted = ""
            Red_Grappling_Reversals = ""
            Blue_Grappling_Reversals = ""
            Red_Grappling_Control_Time = ""
            Blue_Grappling_Control_Time = ""
            red_knockdowns = ""
            blue_knockdowns = ""

            # Getting the "Totals" table
            total_overall_table = stat_soup.find("table")

            # Looping through the "rows"
            for tab in total_overall_table.find_all("tbody"):
                fighter1rowList = []
                fighter2rowList = []
                blue_fighter_row = []
                red_fighter_row = []
                row = tab.find_all("td")

                # Looping through the column of each row
                for r in row:
                    fighter1rowList.append(r.select_one(":nth-child(1)").text)
                    fighter2rowList.append(r.select_one(":nth-child(2)").text)


                # Assigning the values to a list based on the fighters corner color
                if fighter1rowList[0].strip() == blue_fighter:
                    for i in fighter1rowList:
                        blue_fighter_row.append(i)
                elif fighter1rowList[0].strip() == red_fighter:
                    for i in fighter1rowList:
                        red_fighter_row.append(i)

                if fighter2rowList[0].strip() == blue_fighter:
                    for i in fighter2rowList:
                        blue_fighter_row.append(i)
                elif fighter2rowList[0] == red_fighter:
                    for i in fighter2rowList:
                        red_fighter_row.append(i)

                # Referencing and assigning the Knockdown variables in X_fighter_row
                red_knockdowns = red_fighter_row[1].strip()
                blue_knockdowns = blue_fighter_row[1].strip()


                # Splitting total table stats and assigning to each corner color
                Red_Significant_Strikes_Landed = red_fighter_row[2].split("of")[0].strip()
                Red_Significant_Strikes_Attempted = red_fighter_row[2].split("of")[1].strip()
                Blue_Significant_Strikes_Landed = blue_fighter_row[2].split("of")[0].strip()
                Blue_Significant_Strikes_Attempted = blue_fighter_row[2].split("of")[1].strip()

                Red_Significant_Strike_Perc = red_fighter_row[3].strip("%\n ").strip()
                Blue_Significant_Strike_Perc = blue_fighter_row[3].strip("%\n ").strip()

                Red_Total_Strikes_Landed = red_fighter_row[4].split("of")[0].strip()
                Red_Total_Strikes_Attempted = red_fighter_row[4].split("of")[1].strip()
                Blue_Total_Strikes_Landed = blue_fighter_row[4].split("of")[0].strip()
                Blue_Total_Strikes_Attempted = blue_fighter_row[4].split("of")[1].strip()

                Red_Takedowns_Landed = red_fighter_row[5].split("of")[0].strip()
                Red_Takedowns_Attepmted = red_fighter_row[5].split("of")[1].strip()
                Blue_Takedowns_Landed = blue_fighter_row[5].split("of")[0].strip()
                Blue_Takedowns_Attempted = blue_fighter_row[5].split("of")[1].strip()

                Red_Takedown_Perc = red_fighter_row[6].strip("%\n ").strip()
                Blue_Takedown_Perc = blue_fighter_row[6].strip("%\n ").strip()

                Red_Submissions_Attempted = red_fighter_row[7].strip()
                Blue_Submissions_Attempted = blue_fighter_row[7].strip()

                Red_Grappling_Reversals = red_fighter_row[8].strip()
                Blue_Grappling_Reversals = blue_fighter_row[8].strip()

                Red_Grappling_Control_Time = red_fighter_row[9].strip()
                Blue_Grappling_Control_Time = blue_fighter_row[9].strip()


            fighter1SigStrikeRowList = []
            fighter2SigStrikeRowList = []

            # Getting the "Significant Strikes" table
            Sig_Strike_overall_table = stat_soup.find_all("table")[2]

            Sig_Strike_overall_tbody = Sig_Strike_overall_table.find("tbody", {"class": "b-fight-details__table-body"})
            # Looping through <tbody> "rows"
            for i in Sig_Strike_overall_tbody.find_all("td"):
                fighter1SigStrikeRowList.append(i.select_one(":nth-child(1)").text)
                fighter2SigStrikeRowList.append(i.select_one(":nth-child(2)").text)



            blue_sig_strike_fighter_row = []
            red_sig_strike_fighter_row = []

            # deciding corner color base on fighter name vs blue_fighter or red_fighter name
            if fighter1SigStrikeRowList[0].strip() == blue_fighter:
                for i in fighter1SigStrikeRowList:
                    blue_sig_strike_fighter_row.append(i)
            elif fighter1SigStrikeRowList[0].strip() == red_fighter:
                for i in fighter1SigStrikeRowList:
                    red_sig_strike_fighter_row.append(i)

            if fighter2SigStrikeRowList[0].strip() == blue_fighter:
                for i in fighter2SigStrikeRowList:
                    blue_sig_strike_fighter_row.append(i)
            elif fighter2SigStrikeRowList[0] == red_fighter:
                for i in fighter2SigStrikeRowList:
                    red_sig_strike_fighter_row.append(i)

            # Splitting total table stats (Attempted Vs. Landed) assigning to each color
            Red_Head_Significant_Strikes_Landed = red_sig_strike_fighter_row[3].split("of")[0].strip()
            Red_Head_Significant_Strikes_Attempted = red_sig_strike_fighter_row[3].split("of")[1].strip()
            Blue_Head_Significant_Strikes_Landed = blue_sig_strike_fighter_row[3].split("of")[0].strip()
            Blue_Head_Significant_Strikes_Attempted = blue_sig_strike_fighter_row[3].split("of")[1].strip()

            Red_Body_Significant_Strikes_Landed = red_sig_strike_fighter_row[4].split("of")[0].strip()
            Red_Body_Significant_Strikes_Attempted = red_sig_strike_fighter_row[4].split("of")[1].strip()
            Blue_Body_Significant_Strikes_Landed = blue_sig_strike_fighter_row[4].split("of")[0].strip()
            Blue_Body_Significant_Strikes_Attempted = blue_sig_strike_fighter_row[4].split("of")[1].strip()

            Red_Leg_Significant_Strikes_Landed = red_sig_strike_fighter_row[5].split("of")[0].strip()
            Red_Leg_Significant_Strikes_Attempted = red_sig_strike_fighter_row[5].split("of")[1].strip()
            Blue_Leg_Significant_Strikes_Landed = blue_sig_strike_fighter_row[5].split("of")[0].strip()
            Blue_Leg_Significant_Strikes_Attempted = blue_sig_strike_fighter_row[5].split("of")[1].strip()

            Red_Distance_Significant_Strikes_Landed = red_sig_strike_fighter_row[6].split("of")[0].strip()
            Red_Distance_Significant_Strikes_Attempted = red_sig_strike_fighter_row[6].split("of")[1].strip()
            Blue_Distance_Significant_Strikes_Landed = blue_sig_strike_fighter_row[6].split("of")[0].strip()
            Blue_Distance_Significant_Strikes_Attempted = blue_sig_strike_fighter_row[6].split("of")[1].strip()

            Red_Clinch_Significant_Strikes_Landed = red_sig_strike_fighter_row[7].split("of")[0].strip()
            Red_Clinch_Significant_Strikes_Attempted = red_sig_strike_fighter_row[7].split("of")[1].strip()
            Blue_Clinch_Significant_Strikes_Landed = blue_sig_strike_fighter_row[7].split("of")[0].strip()
            Blue_Clinch_Significant_Strikes_Attempted = blue_sig_strike_fighter_row[7].split("of")[1].strip()

            Red_Ground_Significant_Strikes_Landed = red_sig_strike_fighter_row[8].split("of")[0].strip()
            Red_Ground_Significant_Strikes_Attempted = red_sig_strike_fighter_row[8].split("of")[1].strip()
            Blue_Ground_Significant_Strikes_Landed = blue_sig_strike_fighter_row[8].split("of")[0].strip()
            Blue_Ground_Significant_Strikes_Attempted = blue_sig_strike_fighter_row[8].split("of")[1].strip()




            # Instantiating strings to find each rounds "section"
            round_one = "Round 1"
            round_two = "Round 2"
            round_three = "Round 3"
            round_four = "Round 4"
            round_five = "Round 5"

            # Getting the section containing the "Totals" table round information
            Rounds_totals_round_table = stat_soup.find_all("section", {"class": "b-fight-details__section js-fight-section"})[2]
            totals_round_table = Rounds_totals_round_table.find("table", {"class": "b-fight-details__table js-fight-table"})

            # Finding all round headers within the Totals table
            roundHeaders = totals_round_table.find_all("thead", {
                "class": "b-fight-details__table-row b-fight-details__table-row_type_head"})

            R1_Fighter1_Totals_Table_List = []
            R1_Fighter2_Totals_Table_List = []
            R1_Blue_Fighter_Totals_Row = []
            R1_Red_Fighter_Totals_Row = []

            R2_Fighter1_Totals_Table_List = []
            R2_Fighter2_Totals_Table_List = []
            R2_Blue_Fighter_Totals_Row = []
            R2_Red_Fighter_Totals_Row = []

            R3_Fighter1_Totals_Table_List = []
            R3_Fighter2_Totals_Table_List = []
            R3_Blue_Fighter_Totals_Row = []
            R3_Red_Fighter_Totals_Row = []

            R4_Fighter1_Totals_Table_List = []
            R4_Fighter2_Totals_Table_List = []
            R4_Blue_Fighter_Totals_Row = []
            R4_Red_Fighter_Totals_Row = []

            R5_Fighter1_Totals_Table_List = []
            R5_Fighter2_Totals_Table_List = []
            R5_Blue_Fighter_Totals_Row = []
            R5_Red_Fighter_Totals_Row = []
            # ROUND ONE TOTAL VALUES INITIALIZED
                #RED
            R_Round_One_Knockdowns = ""
            R_Round_One_Significant_Strikes_Landed = ""
            R_Round_One_Significant_Strikes_Attempted = ""
            R_Round_One_Significant_Strike_Perc = ""
            R_Round_One_Total_Strikes_Attempted = ""
            R_Round_One_Total_Strikes_Landed = ""
            R_Round_One_Takedowns_Attempted = ""
            R_Round_One_Takedowns_Landed = ""
            R_Round_One_Takedown_Perc = ""
            R_Round_One_Submission_Attempts = ""
            R_Round_One_Grappling_Reversals = ""
            R_Round_One_Grappling_Control_Time = ""
                #BLUE
            B_Round_One_Knockdowns = ""
            B_Round_One_Significant_Strikes_Landed = ""
            B_Round_One_Significant_Strikes_Attempted = ""
            B_Round_One_Significant_Strike_Perc = ""
            B_Round_One_Total_Strikes_Attempted = ""
            B_Round_One_Total_Strikes_Landed = ""
            B_Round_One_Takedowns_Attempted = ""
            B_Round_One_Takedowns_Landed = ""
            B_Round_One_Takedown_Perc = ""
            B_Round_One_Submission_Attempts = ""
            B_Round_One_Grappling_Reversals = ""
            B_Round_One_Grappling_Control_Time = ""

            # ROUND TWO TOTAL VALUES INITIALIZED
                #RED
            R_Round_Two_Knockdowns = ""
            R_Round_Two_Significant_Strikes_Landed = ""
            R_Round_Two_Significant_Strikes_Attempted = ""
            R_Round_Two_Significant_Strike_Perc = ""
            R_Round_Two_Total_Strikes_Attempted = ""
            R_Round_Two_Total_Strikes_Landed = ""
            R_Round_Two_Takedowns_Attempted = ""
            R_Round_Two_Takedowns_Landed = ""
            R_Round_Two_Takedown_Perc = ""
            R_Round_Two_Submission_Attempts = ""
            R_Round_Two_Grappling_Reversals = ""
            R_Round_Two_Grappling_Control_Time = ""
                #BLUE
            B_Round_Two_Knockdowns = ""
            B_Round_Two_Significant_Strikes_Landed = ""
            B_Round_Two_Significant_Strikes_Attempted = ""
            B_Round_Two_Significant_Strike_Perc = ""
            B_Round_Two_Total_Strikes_Attempted = ""
            B_Round_Two_Total_Strikes_Landed = ""
            B_Round_Two_Takedowns_Attempted = ""
            B_Round_Two_Takedowns_Landed = ""
            B_Round_Two_Takedown_Perc = ""
            B_Round_Two_Submission_Attempts = ""
            B_Round_Two_Grappling_Reversals = ""
            B_Round_Two_Grappling_Control_Time = ""

            # ROUND THREE TOTAL VALUES INITIALIZED
                # RED
            R_Round_Three_Knockdowns = ""
            R_Round_Three_Significant_Strikes_Landed = ""
            R_Round_Three_Significant_Strikes_Attempted = ""
            R_Round_Three_Significant_Strike_Perc = ""
            R_Round_Three_Total_Strikes_Attempted = ""
            R_Round_Three_Total_Strikes_Landed = ""
            R_Round_Three_Takedowns_Attempted = ""
            R_Round_Three_Takedowns_Landed = ""
            R_Round_Three_Takedown_Perc = ""
            R_Round_Three_Submission_Attempts = ""
            R_Round_Three_Grappling_Reversals = ""
            R_Round_Three_Grappling_Control_Time = ""
                #BLUE
            B_Round_Three_Knockdowns = ""
            B_Round_Three_Significant_Strikes_Landed = ""
            B_Round_Three_Significant_Strikes_Attempted = ""
            B_Round_Three_Significant_Strike_Perc = ""
            B_Round_Three_Total_Strikes_Attempted = ""
            B_Round_Three_Total_Strikes_Landed = ""
            B_Round_Three_Takedowns_Attempted = ""
            B_Round_Three_Takedowns_Landed = ""
            B_Round_Three_Takedown_Perc = ""
            B_Round_Three_Submission_Attempts = ""
            B_Round_Three_Grappling_Reversals = ""
            B_Round_Three_Grappling_Control_Time = ""

            # ROUND FOUR TOTAL VALUES INITIALIZED
                # RED
            R_Round_Four_Knockdowns = ""
            R_Round_Four_Significant_Strikes_Landed = ""
            R_Round_Four_Significant_Strikes_Attempted = ""
            R_Round_Four_Significant_Strike_Perc = ""
            R_Round_Four_Total_Strikes_Attempted = ""
            R_Round_Four_Total_Strikes_Landed = ""
            R_Round_Four_Takedowns_Attempted = ""
            R_Round_Four_Takedowns_Landed = ""
            R_Round_Four_Takedown_Perc = ""
            R_Round_Four_Submission_Attempts = ""
            R_Round_Four_Grappling_Reversals = ""
            R_Round_Four_Grappling_Control_Time = ""
                # BLUE
            B_Round_Four_Knockdowns = ""
            B_Round_Four_Significant_Strikes_Landed = ""
            B_Round_Four_Significant_Strikes_Attempted = ""
            B_Round_Four_Significant_Strike_Perc = ""
            B_Round_Four_Total_Strikes_Attempted = ""
            B_Round_Four_Total_Strikes_Landed = ""
            B_Round_Four_Takedowns_Attempted = ""
            B_Round_Four_Takedowns_Landed = ""
            B_Round_Four_Takedown_Perc = ""
            B_Round_Four_Submission_Attempts = ""
            B_Round_Four_Grappling_Reversals = ""
            B_Round_Four_Grappling_Control_Time = ""

            # ROUND FIVE TOTAL VALUES INITIALIZED
                # RED
            R_Round_Five_Knockdowns = ""
            R_Round_Five_Significant_Strikes_Landed = ""
            R_Round_Five_Significant_Strikes_Attempted = ""
            R_Round_Five_Significant_Strike_Perc = ""
            R_Round_Five_Total_Strikes_Attempted = ""
            R_Round_Five_Total_Strikes_Landed = ""
            R_Round_Five_Takedowns_Attempted = ""
            R_Round_Five_Takedowns_Landed = ""
            R_Round_Five_Takedown_Perc = ""
            R_Round_Five_Submission_Attempts = ""
            R_Round_Five_Grappling_Reversals = ""
            R_Round_Five_Grappling_Control_Time = ""
                # BLUE
            B_Round_Five_Knockdowns = ""
            B_Round_Five_Significant_Strikes_Landed = ""
            B_Round_Five_Significant_Strikes_Attempted = ""
            B_Round_Five_Significant_Strike_Perc = ""
            B_Round_Five_Total_Strikes_Attempted = ""
            B_Round_Five_Total_Strikes_Landed = ""
            B_Round_Five_Takedowns_Attempted = ""
            B_Round_Five_Takedowns_Landed = ""
            B_Round_Five_Takedown_Perc = ""
            B_Round_Five_Submission_Attempts = ""
            B_Round_Five_Grappling_Reversals = ""
            B_Round_Five_Grappling_Control_Time = ""

            # GETS Total (table) values of each round:
            for i in roundHeaders:
                # ROUND 1
                # If the loop encounters the header "Round 1", continue...
                if i.text.strip() == round_one:
                    # Since the header matches the round we are looking for, we grab the next sibling, which is a
                    # <tbody> ceontaining the round information
                    round_one_tbody = i.find_next_siblings(limit=1)
                    # Even though there is only 1, we must loop through the results
                    for x in round_one_tbody:
                        round_one_td = x.find_all("td")
                        for y in round_one_td:
                            R1_Fighter1_Totals_Table_List.append(y.select_one(":nth-child(1)").text)
                            R1_Fighter2_Totals_Table_List.append(y.select_one(":nth-child(2)").text)

                    # Assigning the values to a list based on the fighters corner color
                    if R1_Fighter1_Totals_Table_List[0].strip() == blue_fighter:
                        for z in R1_Fighter1_Totals_Table_List:
                            R1_Blue_Fighter_Totals_Row.append(z)
                    elif R1_Fighter1_Totals_Table_List[0].strip() == red_fighter:
                        for z in R1_Fighter1_Totals_Table_List:
                            R1_Red_Fighter_Totals_Row.append(z)
                    if R1_Fighter2_Totals_Table_List[0].strip() == blue_fighter:
                        for z in R1_Fighter2_Totals_Table_List:
                            R1_Blue_Fighter_Totals_Row.append(z)
                    elif R1_Fighter2_Totals_Table_List[0] == red_fighter:
                        for z in R1_Fighter2_Totals_Table_List:
                            R1_Red_Fighter_Totals_Row.append(z)

                # TOTALS TABLE ROUND 2
                if i.text.strip() == round_two:
                    # Since the header matches the round we are looking for, we grab the next sibling, which is a
                    # <tbody> ceontaining the round information
                    round_two_tbody = i.find_next_siblings(limit=1)
                    # Even though there is only 1, we must loop through the results
                    for x in round_two_tbody:
                        round_two_td = x.find_all("td")
                        for y in round_two_td:
                            R2_Fighter1_Totals_Table_List.append(y.select_one(":nth-child(1)").text)
                            R2_Fighter2_Totals_Table_List.append(y.select_one(":nth-child(2)").text)

                    # Assigning the values to a list based on the fighters corner color
                    if R2_Fighter1_Totals_Table_List[0].strip() == blue_fighter:
                        for z in R2_Fighter1_Totals_Table_List:
                            R2_Blue_Fighter_Totals_Row.append(z)
                    elif R2_Fighter1_Totals_Table_List[0].strip() == red_fighter:
                        for z in R2_Fighter1_Totals_Table_List:
                            R2_Red_Fighter_Totals_Row.append(z)
                    if R2_Fighter2_Totals_Table_List[0].strip() == blue_fighter:
                        for z in R2_Fighter2_Totals_Table_List:
                            R2_Blue_Fighter_Totals_Row.append(z)
                    elif R2_Fighter2_Totals_Table_List[0] == red_fighter:
                        for z in R2_Fighter2_Totals_Table_List:
                            R2_Red_Fighter_Totals_Row.append(z)


                # TOTALS TABLE ROUND 3
                if i.text.strip() == round_three:
                    # Since the header matches the round we are looking for, we grab the next sibling, which is a
                    # <tbody> ceontaining the round information
                    round_three_tbody = i.find_next_siblings(limit=1)
                    # Even though there is only 1, we must loop through the results
                    for x in round_three_tbody:
                        round_three_td = x.find_all("td")
                        for y in round_three_td:
                            R3_Fighter1_Totals_Table_List.append(y.select_one(":nth-child(1)").text)
                            R3_Fighter2_Totals_Table_List.append(y.select_one(":nth-child(2)").text)

                    # Assigning the values to a list based on the fighters corner color
                    if R3_Fighter1_Totals_Table_List[0].strip() == blue_fighter:
                        for z in R3_Fighter1_Totals_Table_List:
                            R3_Blue_Fighter_Totals_Row.append(z)
                    elif R3_Fighter1_Totals_Table_List[0].strip() == red_fighter:
                        for z in R3_Fighter1_Totals_Table_List:
                            R3_Red_Fighter_Totals_Row.append(z)
                    if R3_Fighter2_Totals_Table_List[0].strip() == blue_fighter:
                        for z in R3_Fighter2_Totals_Table_List:
                            R3_Blue_Fighter_Totals_Row.append(z)
                    elif R3_Fighter2_Totals_Table_List[0] == red_fighter:
                        for z in R3_Fighter2_Totals_Table_List:
                            R3_Red_Fighter_Totals_Row.append(z)


                # TOTALS TABLE ROUND 4
                if i.text.strip() == round_four:
                    # Since the header matches the round we are looking for, we grab the next sibling, which is a
                    # <tbody> ceontaining the round information
                    round_four_tbody = i.find_next_siblings(limit=1)
                    # Even though there is only 1, we must loop through the results
                    for x in round_four_tbody:
                        round_four_td = x.find_all("td")
                        for y in round_four_td:
                            R4_Fighter1_Totals_Table_List.append(y.select_one(":nth-child(1)").text)
                            R4_Fighter2_Totals_Table_List.append(y.select_one(":nth-child(2)").text)

                    # Assigning the values to a list based on the fighters corner color
                    if R4_Fighter1_Totals_Table_List[0].strip() == blue_fighter:
                        for z in R4_Fighter1_Totals_Table_List:
                            R4_Blue_Fighter_Totals_Row.append(z)
                    elif R4_Fighter1_Totals_Table_List[0].strip() == red_fighter:
                        for z in R4_Fighter1_Totals_Table_List:
                            R4_Red_Fighter_Totals_Row.append(z)
                    if R4_Fighter2_Totals_Table_List[0].strip() == blue_fighter:
                        for z in R4_Fighter2_Totals_Table_List:
                            R4_Blue_Fighter_Totals_Row.append(z)
                    elif R4_Fighter2_Totals_Table_List[0] == red_fighter:
                        for z in R4_Fighter2_Totals_Table_List:
                            R4_Red_Fighter_Totals_Row.append(z)

                # TOTALS TABLE ROUND 5
                if i.text.strip() == round_five:
                    # Since the header matches the round we are looking for, we grab the next sibling, which is a
                    # <tbody> ceontaining the round information
                    round_five_tbody = i.find_next_siblings(limit=1)
                    # Even though there is only 1, we must loop through the results
                    for x in round_five_tbody:
                        round_five_td = x.find_all("td")
                        for y in round_five_td:
                            R5_Fighter1_Totals_Table_List.append(y.select_one(":nth-child(1)").text)
                            R5_Fighter2_Totals_Table_List.append(y.select_one(":nth-child(2)").text)

                    # Assigning the values to a list based on the fighters corner color
                    if R5_Fighter1_Totals_Table_List[0].strip() == blue_fighter:
                        for z in R5_Fighter1_Totals_Table_List:
                            R5_Blue_Fighter_Totals_Row.append(z)
                    elif R5_Fighter1_Totals_Table_List[0].strip() == red_fighter:
                        for z in R5_Fighter1_Totals_Table_List:
                            R5_Red_Fighter_Totals_Row.append(z)
                    if R5_Fighter2_Totals_Table_List[0].strip() == blue_fighter:
                        for z in R5_Fighter2_Totals_Table_List:
                            R5_Blue_Fighter_Totals_Row.append(z)
                    elif R5_Fighter2_Totals_Table_List[0] == red_fighter:
                        for z in R5_Fighter2_Totals_Table_List:
                            R5_Red_Fighter_Totals_Row.append(z)

            # fighter values being assigned for each round.
                ## ROUND 1 RED FIGHTER STATS
            if R1_Red_Fighter_Totals_Row != empty_list:
                R_Round_One_Knockdowns = R1_Red_Fighter_Totals_Row[1].strip()
                R_Round_One_Significant_Strikes_Landed = R1_Red_Fighter_Totals_Row[2].split("of")[0].strip()
                R_Round_One_Significant_Strikes_Attempted= R1_Red_Fighter_Totals_Row[2].split("of")[1].strip()
                R_Round_One_Significant_Strike_Perc= R1_Red_Fighter_Totals_Row[3].strip("%\n ").strip()
                R_Round_One_Total_Strikes_Landed = R1_Red_Fighter_Totals_Row[4].split("of")[0].strip()
                R_Round_One_Total_Strikes_Attempted= R1_Red_Fighter_Totals_Row[4].split("of")[1].strip()
                R_Round_One_Takedowns_Landed = R1_Red_Fighter_Totals_Row[5].split("of")[0].strip()
                R_Round_One_Takedowns_Attempted= R1_Red_Fighter_Totals_Row[5].split("of")[1].strip()
                R_Round_One_Takedown_Perc= R1_Red_Fighter_Totals_Row[6].strip("%\n ").strip()
                R_Round_One_Submission_Attempts= R1_Red_Fighter_Totals_Row[7].strip()
                R_Round_One_Grappling_Reversals= R1_Red_Fighter_Totals_Row[8].strip()
                R_Round_One_Grappling_Control_Time= R1_Red_Fighter_Totals_Row[9].strip()

                ## ROUND 1 BLUE FIGHTER STATS
            if R1_Blue_Fighter_Totals_Row != empty_list:
                B_Round_One_Knockdowns = R1_Blue_Fighter_Totals_Row[1].strip()
                B_Round_One_Significant_Strikes_Landed = R1_Blue_Fighter_Totals_Row[2].split("of")[0].strip()
                B_Round_One_Significant_Strikes_Attempted= R1_Blue_Fighter_Totals_Row[2].split("of")[1].strip()
                B_Round_One_Significant_Strike_Perc= R1_Blue_Fighter_Totals_Row[3].strip("%\n ").strip()
                B_Round_One_Total_Strikes_Landed = R1_Blue_Fighter_Totals_Row[4].split("of")[0].strip()
                B_Round_One_Total_Strikes_Attempted= R1_Blue_Fighter_Totals_Row[4].split("of")[1].strip()
                B_Round_One_Takedowns_Landed = R1_Blue_Fighter_Totals_Row[5].split("of")[0].strip()
                B_Round_One_Takedowns_Attempted= R1_Blue_Fighter_Totals_Row[5].split("of")[1].strip()
                B_Round_One_Takedown_Perc= R1_Blue_Fighter_Totals_Row[6].strip("%\n ").strip()
                B_Round_One_Submission_Attempts= R1_Blue_Fighter_Totals_Row[7].strip()
                B_Round_One_Grappling_Reversals= R1_Blue_Fighter_Totals_Row[8].strip()
                B_Round_One_Grappling_Control_Time= R1_Blue_Fighter_Totals_Row[9].strip()



            if R2_Red_Fighter_Totals_Row != empty_list:
                    ## ROUND 2 RED FIGHTER STATS
                R_Round_Two_Knockdowns = R2_Red_Fighter_Totals_Row[1].strip()
                R_Round_Two_Significant_Strikes_Landed = R2_Red_Fighter_Totals_Row[2].split("of")[0].strip()
                R_Round_Two_Significant_Strikes_Attempted = R2_Red_Fighter_Totals_Row[2].split("of")[1].strip()
                R_Round_Two_Significant_Strike_Perc = R2_Red_Fighter_Totals_Row[3].strip("%\n ").strip()
                R_Round_Two_Total_Strikes_Landed = R2_Red_Fighter_Totals_Row[4].split("of")[0].strip()
                R_Round_Two_Total_Strikes_Attempted = R2_Red_Fighter_Totals_Row[4].split("of")[1].strip()
                R_Round_Two_Takedowns_Landed = R2_Red_Fighter_Totals_Row[5].split("of")[0].strip()
                R_Round_Two_Takedowns_Attempted = R2_Red_Fighter_Totals_Row[5].split("of")[1].strip()
                R_Round_Two_Takedown_Perc = R2_Red_Fighter_Totals_Row[6].strip("%\n ").strip()
                R_Round_Two_Submission_Attempts = R2_Red_Fighter_Totals_Row[7].strip()
                R_Round_Two_Grappling_Reversals = R2_Red_Fighter_Totals_Row[8].strip()
                R_Round_Two_Grappling_Control_Time = R2_Red_Fighter_Totals_Row[9].strip()

                ## ROUND 2 BLUE FIGHTER STATS
            if R2_Blue_Fighter_Totals_Row != empty_list:
                B_Round_Two_Knockdowns = R2_Blue_Fighter_Totals_Row[1].strip()
                B_Round_Two_Significant_Strikes_Landed = R2_Blue_Fighter_Totals_Row[2].split("of")[0].strip()
                B_Round_Two_Significant_Strikes_Attempted = R2_Blue_Fighter_Totals_Row[2].split("of")[1].strip()
                B_Round_Two_Significant_Strike_Perc = R2_Blue_Fighter_Totals_Row[3].strip("%\n ").strip()
                B_Round_Two_Total_Strikes_Landed = R2_Blue_Fighter_Totals_Row[4].split("of")[0].strip()
                B_Round_Two_Total_Strikes_Attempted = R2_Blue_Fighter_Totals_Row[4].split("of")[1].strip()
                B_Round_Two_Takedowns_Landed = R2_Blue_Fighter_Totals_Row[5].split("of")[0].strip()
                B_Round_Two_Takedowns_Attempted = R2_Blue_Fighter_Totals_Row[5].split("of")[1].strip()
                B_Round_Two_Takedown_Perc = R2_Blue_Fighter_Totals_Row[6].strip("%\n ").strip()
                B_Round_Two_Submission_Attempts = R2_Blue_Fighter_Totals_Row[7].strip()
                B_Round_Two_Grappling_Reversals = R2_Blue_Fighter_Totals_Row[8].strip()
                B_Round_Two_Grappling_Control_Time = R2_Blue_Fighter_Totals_Row[9].strip()


            if R3_Red_Fighter_Totals_Row != empty_list:
                    ## ROUND 3 RED FIGHTER STATS
                R_Round_Three_Knockdowns = R3_Red_Fighter_Totals_Row[1].strip()
                R_Round_Three_Significant_Strikes_Landed = R3_Red_Fighter_Totals_Row[2].split("of")[0].strip()
                R_Round_Three_Significant_Strikes_Attempted = R3_Red_Fighter_Totals_Row[2].split("of")[1].strip()
                R_Round_Three_Significant_Strike_Perc = R3_Red_Fighter_Totals_Row[3].strip("%\n ").strip()
                R_Round_Three_Total_Strikes_Landed = R3_Red_Fighter_Totals_Row[4].split("of")[0].strip()
                R_Round_Three_Total_Strikes_Attempted = R3_Red_Fighter_Totals_Row[4].split("of")[1].strip()
                R_Round_Three_Takedowns_Landed = R3_Red_Fighter_Totals_Row[5].split("of")[0].strip()
                R_Round_Three_Takedowns_Attempted = R3_Red_Fighter_Totals_Row[5].split("of")[1].strip()
                R_Round_Three_Takedown_Perc = R3_Red_Fighter_Totals_Row[6].strip("%\n ").strip()
                R_Round_Three_Submission_Attempts = R3_Red_Fighter_Totals_Row[7].strip()
                R_Round_Three_Grappling_Reversals = R3_Red_Fighter_Totals_Row[8].strip()
                R_Round_Three_Grappling_Control_Time = R3_Red_Fighter_Totals_Row[9].strip()

                    ## ROUND 3 BLUE FIGHTER STATS
            if R3_Blue_Fighter_Totals_Row != empty_list:
                B_Round_Three_Knockdowns = R3_Blue_Fighter_Totals_Row[1].strip()
                B_Round_Three_Significant_Strikes_Landed = R3_Blue_Fighter_Totals_Row[2].split("of")[0].strip()
                B_Round_Three_Significant_Strikes_Attempted = R3_Blue_Fighter_Totals_Row[2].split("of")[1].strip()
                B_Round_Three_Significant_Strike_Perc = R3_Blue_Fighter_Totals_Row[3].strip("%\n ").strip()
                B_Round_Three_Total_Strikes_Landed = R3_Blue_Fighter_Totals_Row[4].split("of")[0].strip()
                B_Round_Three_Total_Strikes_Attempted = R3_Blue_Fighter_Totals_Row[4].split("of")[1].strip()
                B_Round_Three_Takedowns_Landed = R3_Blue_Fighter_Totals_Row[5].split("of")[0].strip()
                B_Round_Three_Takedowns_Attempted = R3_Blue_Fighter_Totals_Row[5].split("of")[1].strip()
                B_Round_Three_Takedown_Perc = R3_Blue_Fighter_Totals_Row[6].strip("%\n ").strip()
                B_Round_Three_Submission_Attempts = R3_Blue_Fighter_Totals_Row[7].strip()
                B_Round_Three_Grappling_Reversals = R3_Blue_Fighter_Totals_Row[8].strip()
                B_Round_Three_Grappling_Control_Time = R3_Blue_Fighter_Totals_Row[9].strip()


                ## ROUND 4 RED FIGHTER STATS
            if R4_Red_Fighter_Totals_Row != empty_list:
                R_Round_Four_Knockdowns = R4_Red_Fighter_Totals_Row[1].strip()
                R_Round_Four_Significant_Strikes_Landed = R4_Red_Fighter_Totals_Row[2].split("of")[0].strip()
                R_Round_Four_Significant_Strikes_Attempted = R4_Red_Fighter_Totals_Row[2].split("of")[1].strip()
                R_Round_Four_Significant_Strike_Perc = R4_Red_Fighter_Totals_Row[3].strip("%\n ").strip()
                R_Round_Four_Total_Strikes_Landed = R4_Red_Fighter_Totals_Row[4].split("of")[0].strip()
                R_Round_Four_Total_Strikes_Attempted = R4_Red_Fighter_Totals_Row[4].split("of")[1].strip()
                R_Round_Four_Takedowns_Landed = R4_Red_Fighter_Totals_Row[5].split("of")[0].strip()
                R_Round_Four_Takedowns_Attempted = R4_Red_Fighter_Totals_Row[5].split("of")[1].strip()
                R_Round_Four_Takedown_Perc = R4_Red_Fighter_Totals_Row[6].strip("%\n ").strip()
                R_Round_Four_Submission_Attempts = R4_Red_Fighter_Totals_Row[7].strip()
                R_Round_Four_Grappling_Reversals = R4_Red_Fighter_Totals_Row[8].strip()
                R_Round_Four_Grappling_Control_Time = R4_Red_Fighter_Totals_Row[9].strip()

                ## ROUND 4 BLUE FIGHTER STATS
            if R4_Blue_Fighter_Totals_Row != empty_list:
                B_Round_Four_Knockdowns = R4_Blue_Fighter_Totals_Row[1].strip()
                B_Round_Four_Significant_Strikes_Landed = R4_Blue_Fighter_Totals_Row[2].split("of")[0].strip()
                B_Round_Four_Significant_Strikes_Attempted = R4_Blue_Fighter_Totals_Row[2].split("of")[1].strip()
                B_Round_Four_Significant_Strike_Perc = R4_Blue_Fighter_Totals_Row[3].strip("%\n ").strip()
                B_Round_Four_Total_Strikes_Landed = R4_Blue_Fighter_Totals_Row[4].split("of")[0].strip()
                B_Round_Four_Total_Strikes_Attempted = R4_Blue_Fighter_Totals_Row[4].split("of")[1].strip()
                B_Round_Four_Takedowns_Landed = R4_Blue_Fighter_Totals_Row[5].split("of")[0].strip()
                B_Round_Four_Takedowns_Attempted = R4_Blue_Fighter_Totals_Row[5].split("of")[1].strip()
                B_Round_Four_Takedown_Perc = R4_Blue_Fighter_Totals_Row[6].strip("%\n ").strip()
                B_Round_Four_Submission_Attempts = R4_Blue_Fighter_Totals_Row[7].strip()
                B_Round_Four_Grappling_Reversals = R4_Blue_Fighter_Totals_Row[8].strip()
                B_Round_Four_Grappling_Control_Time = R4_Blue_Fighter_Totals_Row[9].strip()

            if R5_Red_Fighter_Totals_Row != empty_list:
                R_Round_Five_Knockdowns = R5_Red_Fighter_Totals_Row[1].strip()
                R_Round_Five_Significant_Strikes_Landed = R5_Red_Fighter_Totals_Row[2].split("of")[0].strip()
                R_Round_Five_Significant_Strikes_Attempted = R5_Red_Fighter_Totals_Row[2].split("of")[1].strip()
                R_Round_Five_Significant_Strike_Perc = R5_Red_Fighter_Totals_Row[3].strip("%\n ").strip()
                R_Round_Five_Total_Strikes_Landed = R5_Red_Fighter_Totals_Row[4].split("of")[0].strip()
                R_Round_Five_Total_Strikes_Attempted = R5_Red_Fighter_Totals_Row[4].split("of")[1].strip()
                R_Round_Five_Takedowns_Landed = R5_Red_Fighter_Totals_Row[5].split("of")[0].strip()
                R_Round_Five_Takedowns_Attempted = R5_Red_Fighter_Totals_Row[5].split("of")[1].strip()
                R_Round_Five_Takedown_Perc = R5_Red_Fighter_Totals_Row[6].strip("%\n ").strip()
                R_Round_Five_Submission_Attempts = R5_Red_Fighter_Totals_Row[7].strip()
                R_Round_Five_Grappling_Reversals = R5_Red_Fighter_Totals_Row[8].strip()
                R_Round_Five_Grappling_Control_Time = R5_Red_Fighter_Totals_Row[9].strip()

                ## ROUND 5 BLUE FIGHTER STATS
            if R5_Blue_Fighter_Totals_Row != empty_list:
                B_Round_Five_Knockdowns = R5_Blue_Fighter_Totals_Row[1].strip()
                B_Round_Five_Significant_Strikes_Landed = R5_Blue_Fighter_Totals_Row[2].split("of")[0].strip()
                B_Round_Five_Significant_Strikes_Attempted = R5_Blue_Fighter_Totals_Row[2].split("of")[1].strip()
                B_Round_Five_Significant_Strike_Perc = R5_Blue_Fighter_Totals_Row[3].strip("%\n ").strip()
                B_Round_Five_Total_Strikes_Landed = R5_Blue_Fighter_Totals_Row[4].split("of")[0].strip()
                B_Round_Five_Total_Strikes_Attempted = R5_Blue_Fighter_Totals_Row[4].split("of")[1].strip()
                B_Round_Five_Takedowns_Landed = R5_Blue_Fighter_Totals_Row[5].split("of")[0].strip()
                B_Round_Five_Takedowns_Attempted = R5_Blue_Fighter_Totals_Row[5].split("of")[1].strip()
                B_Round_Five_Takedown_Perc = R5_Blue_Fighter_Totals_Row[6].strip("%\n ").strip()
                B_Round_Five_Submission_Attempts = R5_Blue_Fighter_Totals_Row[7].strip()
                B_Round_Five_Grappling_Reversals = R5_Blue_Fighter_Totals_Row[8].strip()
                B_Round_Five_Grappling_Control_Time = R5_Blue_Fighter_Totals_Row[9].strip()


            R1_Fighter1_SS_Table_List = []
            R1_Fighter2_SS_Table_List = []
            R1_Blue_Fighter_SS_Row = []
            R1_Red_Fighter_SS_Row = []

            R2_Fighter1_SS_Table_List = []
            R2_Fighter2_SS_Table_List = []
            R2_Blue_Fighter_SS_Row = []
            R2_Red_Fighter_SS_Row = []

            R3_Fighter1_SS_Table_List = []
            R3_Fighter2_SS_Table_List = []
            R3_Blue_Fighter_SS_Row = []
            R3_Red_Fighter_SS_Row = []

            R4_Fighter1_SS_Table_List = []
            R4_Fighter2_SS_Table_List = []
            R4_Blue_Fighter_SS_Row = []
            R4_Red_Fighter_SS_Row = []

            R5_Fighter1_SS_Table_List = []
            R5_Fighter2_SS_Table_List = []
            R5_Blue_Fighter_SS_Row = []
            R5_Red_Fighter_SS_Row = []

            # SIG STRIKE TABLE ROUND VALUES INITIALIZED
            ## ROUND 1
                # BLUE
            B_Round_One_Significant_Strikes_Distance_Landed= ""
            B_Round_One_Significant_Strikes_Distance_Attempted= ""
            B_Round_One_Significant_Strikes_Clinch_Landed= ""
            B_Round_One_Significant_Strikes_Clinch_Attempted= ""
            B_Round_One_Significant_Strikes_Ground_Landed= ""
            B_Round_One_Significant_Strikes_Ground_Attempted= ""
            B_Round_One_Head_Significant_Strikes_Attempted= ""
            B_Round_One_Head_Significant_Strikes_Landed= ""
            B_Round_One_Body_Significant_Strikes_Attempted= ""
            B_Round_One_Body_Significant_Strikes_Landed= ""
            B_Round_One_Leg_Significant_Strikes_Attempted= ""
            B_Round_One_Leg_Significant_Strikes_Landed= ""

                # RED
            R_Round_One_Significant_Strikes_Distance_Landed= ""
            R_Round_One_Significant_Strikes_Distance_Attempted= ""
            R_Round_One_Significant_Strikes_Clinch_Landed= ""
            R_Round_One_Significant_Strikes_Clinch_Attempted= ""
            R_Round_One_Significant_Strikes_Ground_Landed= ""
            R_Round_One_Significant_Strikes_Ground_Attempted= ""
            R_Round_One_Head_Significant_Strikes_Attempted= ""
            R_Round_One_Head_Significant_Strikes_Landed= ""
            R_Round_One_Body_Significant_Strikes_Attempted= ""
            R_Round_One_Body_Significant_Strikes_Landed= ""
            R_Round_One_Leg_Significant_Strikes_Attempted= ""
            R_Round_One_Leg_Significant_Strikes_Landed= ""

            ## ROUND 2
                # BLUE
            B_Round_Two_Significant_Strikes_Distance_Landed = ""
            B_Round_Two_Significant_Strikes_Distance_Attempted = ""
            B_Round_Two_Significant_Strikes_Clinch_Landed = ""
            B_Round_Two_Significant_Strikes_Clinch_Attempted = ""
            B_Round_Two_Significant_Strikes_Ground_Landed = ""
            B_Round_Two_Significant_Strikes_Ground_Attempted = ""
            B_Round_Two_Head_Significant_Strikes_Attempted = ""
            B_Round_Two_Head_Significant_Strikes_Landed = ""
            B_Round_Two_Body_Significant_Strikes_Attempted = ""
            B_Round_Two_Body_Significant_Strikes_Landed = ""
            B_Round_Two_Leg_Significant_Strikes_Attempted = ""
            B_Round_Two_Leg_Significant_Strikes_Landed = ""

                # RED
            R_Round_Two_Significant_Strikes_Distance_Landed = ""
            R_Round_Two_Significant_Strikes_Distance_Attempted = ""
            R_Round_Two_Significant_Strikes_Clinch_Landed = ""
            R_Round_Two_Significant_Strikes_Clinch_Attempted = ""
            R_Round_Two_Significant_Strikes_Ground_Landed = ""
            R_Round_Two_Significant_Strikes_Ground_Attempted = ""
            R_Round_Two_Head_Significant_Strikes_Attempted = ""
            R_Round_Two_Head_Significant_Strikes_Landed = ""
            R_Round_Two_Body_Significant_Strikes_Attempted = ""
            R_Round_Two_Body_Significant_Strikes_Landed = ""
            R_Round_Two_Leg_Significant_Strikes_Attempted = ""
            R_Round_Two_Leg_Significant_Strikes_Landed = ""

            ## ROUND 3
                # BLUE
            B_Round_Three_Significant_Strikes_Distance_Landed = ""
            B_Round_Three_Significant_Strikes_Distance_Attempted = ""
            B_Round_Three_Significant_Strikes_Clinch_Landed = ""
            B_Round_Three_Significant_Strikes_Clinch_Attempted = ""
            B_Round_Three_Significant_Strikes_Ground_Landed = ""
            B_Round_Three_Significant_Strikes_Ground_Attempted = ""
            B_Round_Three_Head_Significant_Strikes_Attempted = ""
            B_Round_Three_Head_Significant_Strikes_Landed = ""
            B_Round_Three_Body_Significant_Strikes_Attempted = ""
            B_Round_Three_Body_Significant_Strikes_Landed = ""
            B_Round_Three_Leg_Significant_Strikes_Attempted = ""
            B_Round_Three_Leg_Significant_Strikes_Landed = ""

                # RED
            R_Round_Three_Significant_Strikes_Distance_Landed = ""
            R_Round_Three_Significant_Strikes_Distance_Attempted = ""
            R_Round_Three_Significant_Strikes_Clinch_Landed = ""
            R_Round_Three_Significant_Strikes_Clinch_Attempted = ""
            R_Round_Three_Significant_Strikes_Ground_Landed = ""
            R_Round_Three_Significant_Strikes_Ground_Attempted = ""
            R_Round_Three_Head_Significant_Strikes_Attempted = ""
            R_Round_Three_Head_Significant_Strikes_Landed = ""
            R_Round_Three_Body_Significant_Strikes_Attempted = ""
            R_Round_Three_Body_Significant_Strikes_Landed = ""
            R_Round_Three_Leg_Significant_Strikes_Attempted = ""
            R_Round_Three_Leg_Significant_Strikes_Landed = ""

            ## ROUND 4
                # BLUE
            B_Round_Four_Significant_Strikes_Distance_Landed = ""
            B_Round_Four_Significant_Strikes_Distance_Attempted = ""
            B_Round_Four_Significant_Strikes_Clinch_Landed = ""
            B_Round_Four_Significant_Strikes_Clinch_Attempted = ""
            B_Round_Four_Significant_Strikes_Ground_Landed = ""
            B_Round_Four_Significant_Strikes_Ground_Attempted = ""
            B_Round_Four_Head_Significant_Strikes_Attempted = ""
            B_Round_Four_Head_Significant_Strikes_Landed = ""
            B_Round_Four_Body_Significant_Strikes_Attempted = ""
            B_Round_Four_Body_Significant_Strikes_Landed = ""
            B_Round_Four_Leg_Significant_Strikes_Attempted = ""
            B_Round_Four_Leg_Significant_Strikes_Landed = ""

                # RED
            R_Round_Four_Significant_Strikes_Distance_Landed = ""
            R_Round_Four_Significant_Strikes_Distance_Attempted = ""
            R_Round_Four_Significant_Strikes_Clinch_Landed = ""
            R_Round_Four_Significant_Strikes_Clinch_Attempted = ""
            R_Round_Four_Significant_Strikes_Ground_Landed = ""
            R_Round_Four_Significant_Strikes_Ground_Attempted = ""
            R_Round_Four_Head_Significant_Strikes_Attempted = ""
            R_Round_Four_Head_Significant_Strikes_Landed = ""
            R_Round_Four_Body_Significant_Strikes_Attempted = ""
            R_Round_Four_Body_Significant_Strikes_Landed = ""
            R_Round_Four_Leg_Significant_Strikes_Attempted = ""
            R_Round_Four_Leg_Significant_Strikes_Landed = ""

            ## ROUND 5
                # BLUE
            B_Round_Five_Significant_Strikes_Distance_Landed = ""
            B_Round_Five_Significant_Strikes_Distance_Attempted = ""
            B_Round_Five_Significant_Strikes_Clinch_Landed = ""
            B_Round_Five_Significant_Strikes_Clinch_Attempted = ""
            B_Round_Five_Significant_Strikes_Ground_Landed = ""
            B_Round_Five_Significant_Strikes_Ground_Attempted = ""
            B_Round_Five_Head_Significant_Strikes_Attempted = ""
            B_Round_Five_Head_Significant_Strikes_Landed = ""
            B_Round_Five_Body_Significant_Strikes_Attempted = ""
            B_Round_Five_Body_Significant_Strikes_Landed = ""
            B_Round_Five_Leg_Significant_Strikes_Attempted = ""
            B_Round_Five_Leg_Significant_Strikes_Landed = ""

                # RED
            R_Round_Five_Significant_Strikes_Distance_Landed = ""
            R_Round_Five_Significant_Strikes_Distance_Attempted = ""
            R_Round_Five_Significant_Strikes_Clinch_Landed = ""
            R_Round_Five_Significant_Strikes_Clinch_Attempted = ""
            R_Round_Five_Significant_Strikes_Ground_Landed = ""
            R_Round_Five_Significant_Strikes_Ground_Attempted = ""
            R_Round_Five_Head_Significant_Strikes_Attempted = ""
            R_Round_Five_Head_Significant_Strikes_Landed = ""
            R_Round_Five_Body_Significant_Strikes_Attempted = ""
            R_Round_Five_Body_Significant_Strikes_Landed = ""
            R_Round_Five_Leg_Significant_Strikes_Attempted = ""
            R_Round_Five_Leg_Significant_Strikes_Landed = ""

            # Using Beautiful soup to find Significant Strikes Rounds table
            Rounds_totals_round_table2 = \
            stat_soup.find_all("section", {"class": "b-fight-details__section js-fight-section"})[4]
            totals_round_table2 = Rounds_totals_round_table2.find("table",
                                                                  {"class": "b-fight-details__table js-fight-table"})

            # Finding all round headers within the Totals table
            roundHeaders2 = totals_round_table2.find_all("thead", {
                "class": "b-fight-details__table-row b-fight-details__table-row_type_head"})

            # GETS Significant Strikes (table) values of each round:
            for i in roundHeaders2:
                # ROUND 1
                # If the loop encounters the header "Round 1", continue...
                if i.text.strip() == round_one:
                    # Since the header matches the round we are looking for, we grab the next sibling, which is a
                    # <tbody> ceontaining the round information
                    round_one_tbody = i.find_next_siblings(limit=1)
                    # Even though there is only 1, we must loop through the results
                    for x in round_one_tbody:
                        round_one_td = x.find_all("td")
                        for y in round_one_td:
                            R1_Fighter1_SS_Table_List.append(y.select_one(":nth-child(1)").text)
                            R1_Fighter2_SS_Table_List.append(y.select_one(":nth-child(2)").text)

                    # Assigning the values to a list based on the fighters corner color
                    if R1_Fighter1_SS_Table_List[0].strip() == blue_fighter:
                        for z in R1_Fighter1_SS_Table_List:
                            R1_Blue_Fighter_SS_Row.append(z)
                    elif R1_Fighter1_SS_Table_List[0].strip() == red_fighter:
                        for z in R1_Fighter1_SS_Table_List:
                            R1_Red_Fighter_SS_Row.append(z)
                    if R1_Fighter2_SS_Table_List[0].strip() == blue_fighter:
                        for z in R1_Fighter2_SS_Table_List:
                            R1_Blue_Fighter_SS_Row.append(z)
                    elif R1_Fighter2_SS_Table_List[0] == red_fighter:
                        for z in R1_Fighter2_SS_Table_List:
                            R1_Red_Fighter_SS_Row.append(z)

                # ROUND 2
                if i.text.strip() == round_two:
                    # Since the header matches the round we are looking for, we grab the next sibling, which is a
                    # <tbody> ceontaining the round information
                    round_two_tbody = i.find_next_siblings(limit=1)
                    # Even though there is only 1, we must loop through the results
                    for x in round_two_tbody:
                        round_two_td = x.find_all("td")
                        for y in round_two_td:
                            R2_Fighter1_SS_Table_List.append(y.select_one(":nth-child(1)").text)
                            R2_Fighter2_SS_Table_List.append(y.select_one(":nth-child(2)").text)

                    # Assigning the values to a list based on the fighters corner color
                    if R2_Fighter1_SS_Table_List[0].strip() == blue_fighter:
                        for z in R2_Fighter1_SS_Table_List:
                            R2_Blue_Fighter_SS_Row.append(z)
                    elif R2_Fighter1_SS_Table_List[0].strip() == red_fighter:
                        for z in R2_Fighter1_SS_Table_List:
                            R2_Red_Fighter_SS_Row.append(z)
                    if R2_Fighter2_SS_Table_List[0].strip() == blue_fighter:
                        for z in R2_Fighter2_SS_Table_List:
                            R2_Blue_Fighter_SS_Row.append(z)
                    elif R2_Fighter2_SS_Table_List[0] == red_fighter:
                        for z in R2_Fighter2_SS_Table_List:
                            R2_Red_Fighter_SS_Row.append(z)

                # ROUND 3
                if i.text.strip() == round_three:
                    # Since the header matches the round we are looking for, we grab the next sibling, which is a
                    # <tbody> ceontaining the round information
                    round_three_tbody = i.find_next_siblings(limit=1)
                    # Even though there is only 1, we must loop through the results
                    for x in round_three_tbody:
                        round_three_td = x.find_all("td")
                        for y in round_three_td:
                            R3_Fighter1_SS_Table_List.append(y.select_one(":nth-child(1)").text)
                            R3_Fighter2_SS_Table_List.append(y.select_one(":nth-child(2)").text)

                    # Assigning the values to a list based on the fighters corner color
                    if R3_Fighter1_SS_Table_List[0].strip() == blue_fighter:
                        for z in R3_Fighter1_SS_Table_List:
                            R3_Blue_Fighter_SS_Row.append(z)
                    elif R3_Fighter1_SS_Table_List[0].strip() == red_fighter:
                        for z in R3_Fighter1_SS_Table_List:
                            R3_Red_Fighter_SS_Row.append(z)
                    if R3_Fighter2_SS_Table_List[0].strip() == blue_fighter:
                        for z in R3_Fighter2_SS_Table_List:
                            R3_Blue_Fighter_SS_Row.append(z)
                    elif R3_Fighter2_SS_Table_List[0] == red_fighter:
                        for z in R3_Fighter2_SS_Table_List:
                            R3_Red_Fighter_SS_Row.append(z)

                # ROUND 4
                if i.text.strip() == round_four:
                    # Since the header matches the round we are looking for, we grab the next sibling, which is a
                    # <tbody> ceontaining the round information
                    round_four_tbody = i.find_next_siblings(limit=1)
                    # Even though there is only 1, we must loop through the results
                    for x in round_four_tbody:
                        round_four_td = x.find_all("td")
                        for y in round_four_td:
                            R4_Fighter1_SS_Table_List.append(y.select_one(":nth-child(1)").text)
                            R4_Fighter2_SS_Table_List.append(y.select_one(":nth-child(2)").text)

                    # Assigning the values to a list based on the fighters corner color
                    if R4_Fighter1_SS_Table_List[0].strip() == blue_fighter:
                        for z in R4_Fighter1_SS_Table_List:
                            R4_Blue_Fighter_SS_Row.append(z)
                    elif R4_Fighter1_SS_Table_List[0].strip() == red_fighter:
                        for z in R4_Fighter1_SS_Table_List:
                            R4_Red_Fighter_SS_Row.append(z)
                    if R4_Fighter2_SS_Table_List[0].strip() == blue_fighter:
                        for z in R4_Fighter2_SS_Table_List:
                            R4_Blue_Fighter_SS_Row.append(z)
                    elif R4_Fighter2_SS_Table_List[0] == red_fighter:
                        for z in R4_Fighter2_SS_Table_List:
                            R4_Red_Fighter_SS_Row.append(z)


                # ROUND 5
                if i.text.strip() == round_five:
                    # Since the header matches the round we are looking for, we grab the next sibling, which is a
                    # <tbody> ceontaining the round information
                    round_five_tbody = i.find_next_siblings(limit=1)
                    # Even though there is only 1, we must loop through the results
                    for x in round_five_tbody:
                        round_five_td = x.find_all("td")
                        for y in round_five_td:
                            R5_Fighter1_SS_Table_List.append(y.select_one(":nth-child(1)").text)
                            R5_Fighter2_SS_Table_List.append(y.select_one(":nth-child(2)").text)

                    # Assigning the values to a list based on the fighters corner color
                    if R5_Fighter1_SS_Table_List[0].strip() == blue_fighter:
                        for z in R5_Fighter1_SS_Table_List:
                            R5_Blue_Fighter_SS_Row.append(z)
                    elif R5_Fighter1_SS_Table_List[0].strip() == red_fighter:
                        for z in R5_Fighter1_SS_Table_List:
                            R5_Red_Fighter_SS_Row.append(z)
                    if R5_Fighter2_SS_Table_List[0].strip() == blue_fighter:
                        for z in R5_Fighter2_SS_Table_List:
                            R5_Blue_Fighter_SS_Row.append(z)
                    elif R5_Fighter2_SS_Table_List[0] == red_fighter:
                        for z in R5_Fighter2_SS_Table_List:
                            R5_Red_Fighter_SS_Row.append(z)

            # SIG STRIKE TABLE ROUND VALUES ASSIGNED THEIR VALUES
            # ROUND1
                #BLUE
            if R1_Blue_Fighter_SS_Row != empty_list:
                B_Round_One_Head_Significant_Strikes_Attempted = R1_Blue_Fighter_SS_Row[3].split("of")[1].strip()
                B_Round_One_Head_Significant_Strikes_Landed = R1_Blue_Fighter_SS_Row[3].split("of")[0].strip()
                B_Round_One_Body_Significant_Strikes_Attempted = R1_Blue_Fighter_SS_Row[4].split("of")[1].strip()
                B_Round_One_Body_Significant_Strikes_Landed = R1_Blue_Fighter_SS_Row[4].split("of")[0].strip()
                B_Round_One_Leg_Significant_Strikes_Attempted = R1_Blue_Fighter_SS_Row[5].split("of")[1].strip()
                B_Round_One_Leg_Significant_Strikes_Landed = R1_Blue_Fighter_SS_Row[5].split("of")[0].strip()
                B_Round_One_Significant_Strikes_Distance_Landed = R1_Blue_Fighter_SS_Row[6].split("of")[0].strip()
                B_Round_One_Significant_Strikes_Distance_Attempted = R1_Blue_Fighter_SS_Row[6].split("of")[1].strip()
                B_Round_One_Significant_Strikes_Clinch_Landed = R1_Blue_Fighter_SS_Row[7].split("of")[0].strip()
                B_Round_One_Significant_Strikes_Clinch_Attempted = R1_Blue_Fighter_SS_Row[7].split("of")[1].strip()
                B_Round_One_Significant_Strikes_Ground_Landed = R1_Blue_Fighter_SS_Row[8].split("of")[0].strip()
                B_Round_One_Significant_Strikes_Ground_Attempted = R1_Blue_Fighter_SS_Row[8].split("of")[1].strip()

                # RED
            if R1_Red_Fighter_SS_Row != empty_list:
                R_Round_One_Head_Significant_Strikes_Attempted = R1_Red_Fighter_SS_Row[3].split("of")[1].strip()
                R_Round_One_Head_Significant_Strikes_Landed = R1_Red_Fighter_SS_Row[3].split("of")[0].strip()
                R_Round_One_Body_Significant_Strikes_Attempted = R1_Red_Fighter_SS_Row[4].split("of")[1].strip()
                R_Round_One_Body_Significant_Strikes_Landed = R1_Red_Fighter_SS_Row[4].split("of")[0].strip()
                R_Round_One_Leg_Significant_Strikes_Attempted = R1_Red_Fighter_SS_Row[5].split("of")[1].strip()
                R_Round_One_Leg_Significant_Strikes_Landed = R1_Red_Fighter_SS_Row[5].split("of")[0].strip()
                R_Round_One_Significant_Strikes_Distance_Landed = R1_Red_Fighter_SS_Row[6].split("of")[0].strip()
                R_Round_One_Significant_Strikes_Distance_Attempted = R1_Red_Fighter_SS_Row[6].split("of")[1].strip()
                R_Round_One_Significant_Strikes_Clinch_Landed = R1_Red_Fighter_SS_Row[7].split("of")[0].strip()
                R_Round_One_Significant_Strikes_Clinch_Attempted = R1_Red_Fighter_SS_Row[7].split("of")[1].strip()
                R_Round_One_Significant_Strikes_Ground_Landed = R1_Red_Fighter_SS_Row[8].split("of")[0].strip()
                R_Round_One_Significant_Strikes_Ground_Attempted = R1_Red_Fighter_SS_Row[8].split("of")[1].strip()

            # ROUND2
                #BLUE
            if R2_Blue_Fighter_SS_Row != empty_list:
                B_Round_Two_Head_Significant_Strikes_Attempted = R2_Blue_Fighter_SS_Row[3].split("of")[1].strip()
                B_Round_Two_Head_Significant_Strikes_Landed = R2_Blue_Fighter_SS_Row[3].split("of")[0].strip()
                B_Round_Two_Body_Significant_Strikes_Attempted = R2_Blue_Fighter_SS_Row[4].split("of")[1].strip()
                B_Round_Two_Body_Significant_Strikes_Landed = R2_Blue_Fighter_SS_Row[4].split("of")[0].strip()
                B_Round_Two_Leg_Significant_Strikes_Attempted = R2_Blue_Fighter_SS_Row[5].split("of")[1].strip()
                B_Round_Two_Leg_Significant_Strikes_Landed = R2_Blue_Fighter_SS_Row[5].split("of")[0].strip()
                B_Round_Two_Significant_Strikes_Distance_Landed = R2_Blue_Fighter_SS_Row[6].split("of")[0].strip()
                B_Round_Two_Significant_Strikes_Distance_Attempted = R2_Blue_Fighter_SS_Row[6].split("of")[1].strip()
                B_Round_Two_Significant_Strikes_Clinch_Landed = R2_Blue_Fighter_SS_Row[7].split("of")[0].strip()
                B_Round_Two_Significant_Strikes_Clinch_Attempted = R2_Blue_Fighter_SS_Row[7].split("of")[1].strip()
                B_Round_Two_Significant_Strikes_Ground_Landed = R2_Blue_Fighter_SS_Row[8].split("of")[0].strip()
                B_Round_Two_Significant_Strikes_Ground_Attempted = R2_Blue_Fighter_SS_Row[8].split("of")[1].strip()

                # RED
            if R2_Red_Fighter_SS_Row != empty_list:
                R_Round_Two_Head_Significant_Strikes_Attempted = R2_Red_Fighter_SS_Row[3].split("of")[1].strip()
                R_Round_Two_Head_Significant_Strikes_Landed = R2_Red_Fighter_SS_Row[3].split("of")[0].strip()
                R_Round_Two_Body_Significant_Strikes_Attempted = R2_Red_Fighter_SS_Row[4].split("of")[1].strip()
                R_Round_Two_Body_Significant_Strikes_Landed = R2_Red_Fighter_SS_Row[4].split("of")[0].strip()
                R_Round_Two_Leg_Significant_Strikes_Attempted = R2_Red_Fighter_SS_Row[5].split("of")[1].strip()
                R_Round_Two_Leg_Significant_Strikes_Landed = R2_Red_Fighter_SS_Row[5].split("of")[0].strip()
                R_Round_Two_Significant_Strikes_Distance_Landed = R2_Red_Fighter_SS_Row[6].split("of")[0].strip()
                R_Round_Two_Significant_Strikes_Distance_Attempted = R2_Red_Fighter_SS_Row[6].split("of")[1].strip()
                R_Round_Two_Significant_Strikes_Clinch_Landed = R2_Red_Fighter_SS_Row[7].split("of")[0].strip()
                R_Round_Two_Significant_Strikes_Clinch_Attempted = R2_Red_Fighter_SS_Row[7].split("of")[1].strip()
                R_Round_Two_Significant_Strikes_Ground_Landed = R2_Red_Fighter_SS_Row[8].split("of")[0].strip()
                R_Round_Two_Significant_Strikes_Ground_Attempted = R2_Red_Fighter_SS_Row[8].split("of")[1].strip()

            # ROUND3
                #BLUE
            if R3_Blue_Fighter_SS_Row != empty_list:
                B_Round_Three_Head_Significant_Strikes_Attempted = R3_Blue_Fighter_SS_Row[3].split("of")[1].strip()
                B_Round_Three_Head_Significant_Strikes_Landed = R3_Blue_Fighter_SS_Row[3].split("of")[0].strip()
                B_Round_Three_Body_Significant_Strikes_Attempted = R3_Blue_Fighter_SS_Row[4].split("of")[1].strip()
                B_Round_Three_Body_Significant_Strikes_Landed = R3_Blue_Fighter_SS_Row[4].split("of")[0].strip()
                B_Round_Three_Leg_Significant_Strikes_Attempted = R3_Blue_Fighter_SS_Row[5].split("of")[1].strip()
                B_Round_Three_Leg_Significant_Strikes_Landed = R3_Blue_Fighter_SS_Row[5].split("of")[0].strip()
                B_Round_Three_Significant_Strikes_Distance_Landed = R3_Blue_Fighter_SS_Row[6].split("of")[0].strip()
                B_Round_Three_Significant_Strikes_Distance_Attempted = R3_Blue_Fighter_SS_Row[6].split("of")[1].strip()
                B_Round_Three_Significant_Strikes_Clinch_Landed = R3_Blue_Fighter_SS_Row[7].split("of")[0].strip()
                B_Round_Three_Significant_Strikes_Clinch_Attempted = R3_Blue_Fighter_SS_Row[7].split("of")[1].strip()
                B_Round_Three_Significant_Strikes_Ground_Landed = R3_Blue_Fighter_SS_Row[8].split("of")[0].strip()
                B_Round_Three_Significant_Strikes_Ground_Attempted = R3_Blue_Fighter_SS_Row[8].split("of")[1].strip()

                # RED
            if R3_Red_Fighter_SS_Row != empty_list:
                R_Round_Three_Head_Significant_Strikes_Attempted = R3_Red_Fighter_SS_Row[3].split("of")[1].strip()
                R_Round_Three_Head_Significant_Strikes_Landed = R3_Red_Fighter_SS_Row[3].split("of")[0].strip()
                R_Round_Three_Body_Significant_Strikes_Attempted = R3_Red_Fighter_SS_Row[4].split("of")[1].strip()
                R_Round_Three_Body_Significant_Strikes_Landed = R3_Red_Fighter_SS_Row[4].split("of")[0].strip()
                R_Round_Three_Leg_Significant_Strikes_Attempted = R3_Red_Fighter_SS_Row[5].split("of")[1].strip()
                R_Round_Three_Leg_Significant_Strikes_Landed = R3_Red_Fighter_SS_Row[5].split("of")[0].strip()
                R_Round_Three_Significant_Strikes_Distance_Landed = R3_Red_Fighter_SS_Row[6].split("of")[0].strip()
                R_Round_Three_Significant_Strikes_Distance_Attempted = R3_Red_Fighter_SS_Row[6].split("of")[1].strip()
                R_Round_Three_Significant_Strikes_Clinch_Landed = R3_Red_Fighter_SS_Row[7].split("of")[0].strip()
                R_Round_Three_Significant_Strikes_Clinch_Attempted = R3_Red_Fighter_SS_Row[7].split("of")[1].strip()
                R_Round_Three_Significant_Strikes_Ground_Landed = R3_Red_Fighter_SS_Row[8].split("of")[0].strip()
                R_Round_Three_Significant_Strikes_Ground_Attempted = R3_Red_Fighter_SS_Row[8].split("of")[1].strip()


            # ROUND4
                #BLUE
            if R4_Blue_Fighter_SS_Row != empty_list:
                B_Round_Four_Head_Significant_Strikes_Attempted = R4_Blue_Fighter_SS_Row[3].split("of")[1].strip()
                B_Round_Four_Head_Significant_Strikes_Landed = R4_Blue_Fighter_SS_Row[3].split("of")[0].strip()
                B_Round_Four_Body_Significant_Strikes_Attempted = R4_Blue_Fighter_SS_Row[4].split("of")[1].strip()
                B_Round_Four_Body_Significant_Strikes_Landed = R4_Blue_Fighter_SS_Row[4].split("of")[0].strip()
                B_Round_Four_Leg_Significant_Strikes_Attempted = R4_Blue_Fighter_SS_Row[5].split("of")[1].strip()
                B_Round_Four_Leg_Significant_Strikes_Landed = R4_Blue_Fighter_SS_Row[5].split("of")[0].strip()
                B_Round_Four_Significant_Strikes_Distance_Landed = R4_Blue_Fighter_SS_Row[6].split("of")[0].strip()
                B_Round_Four_Significant_Strikes_Distance_Attempted = R4_Blue_Fighter_SS_Row[6].split("of")[1].strip()
                B_Round_Four_Significant_Strikes_Clinch_Landed = R4_Blue_Fighter_SS_Row[7].split("of")[0].strip()
                B_Round_Four_Significant_Strikes_Clinch_Attempted = R4_Blue_Fighter_SS_Row[7].split("of")[1].strip()
                B_Round_Four_Significant_Strikes_Ground_Landed = R4_Blue_Fighter_SS_Row[8].split("of")[0].strip()
                B_Round_Four_Significant_Strikes_Ground_Attempted = R4_Blue_Fighter_SS_Row[8].split("of")[1].strip()

                # RED
            if R4_Red_Fighter_SS_Row != empty_list:
                R_Round_Four_Head_Significant_Strikes_Attempted = R4_Red_Fighter_SS_Row[3].split("of")[1].strip()
                R_Round_Four_Head_Significant_Strikes_Landed = R4_Red_Fighter_SS_Row[3].split("of")[0].strip()
                R_Round_Four_Body_Significant_Strikes_Attempted = R4_Red_Fighter_SS_Row[4].split("of")[1].strip()
                R_Round_Four_Body_Significant_Strikes_Landed = R4_Red_Fighter_SS_Row[4].split("of")[0].strip()
                R_Round_Four_Leg_Significant_Strikes_Attempted = R4_Red_Fighter_SS_Row[5].split("of")[1].strip()
                R_Round_Four_Leg_Significant_Strikes_Landed = R4_Red_Fighter_SS_Row[5].split("of")[0].strip()
                R_Round_Four_Significant_Strikes_Distance_Landed = R4_Red_Fighter_SS_Row[6].split("of")[0].strip()
                R_Round_Four_Significant_Strikes_Distance_Attempted = R4_Red_Fighter_SS_Row[6].split("of")[1].strip()
                R_Round_Four_Significant_Strikes_Clinch_Landed = R4_Red_Fighter_SS_Row[7].split("of")[0].strip()
                R_Round_Four_Significant_Strikes_Clinch_Attempted = R4_Red_Fighter_SS_Row[7].split("of")[1].strip()
                R_Round_Four_Significant_Strikes_Ground_Landed = R4_Red_Fighter_SS_Row[8].split("of")[0].strip()
                R_Round_Four_Significant_Strikes_Ground_Attempted = R4_Red_Fighter_SS_Row[8].split("of")[1].strip()

            # ROUND5
                #BLUE
            if R5_Blue_Fighter_SS_Row != empty_list:
                B_Round_Five_Head_Significant_Strikes_Attempted = R5_Blue_Fighter_SS_Row[3].split("of")[1].strip()
                B_Round_Five_Head_Significant_Strikes_Landed = R5_Blue_Fighter_SS_Row[3].split("of")[0].strip()
                B_Round_Five_Body_Significant_Strikes_Attempted = R5_Blue_Fighter_SS_Row[4].split("of")[1].strip()
                B_Round_Five_Body_Significant_Strikes_Landed = R5_Blue_Fighter_SS_Row[4].split("of")[0].strip()
                B_Round_Five_Leg_Significant_Strikes_Attempted = R5_Blue_Fighter_SS_Row[5].split("of")[1].strip()
                B_Round_Five_Leg_Significant_Strikes_Landed = R5_Blue_Fighter_SS_Row[5].split("of")[0].strip()
                B_Round_Five_Significant_Strikes_Distance_Landed = R5_Blue_Fighter_SS_Row[6].split("of")[0].strip()
                B_Round_Five_Significant_Strikes_Distance_Attempted = R5_Blue_Fighter_SS_Row[6].split("of")[1].strip()
                B_Round_Five_Significant_Strikes_Clinch_Landed = R5_Blue_Fighter_SS_Row[7].split("of")[0].strip()
                B_Round_Five_Significant_Strikes_Clinch_Attempted = R5_Blue_Fighter_SS_Row[7].split("of")[1].strip()
                B_Round_Five_Significant_Strikes_Ground_Landed = R5_Blue_Fighter_SS_Row[8].split("of")[0].strip()
                B_Round_Five_Significant_Strikes_Ground_Attempted = R5_Blue_Fighter_SS_Row[8].split("of")[1].strip()

                # RED
            if R5_Red_Fighter_SS_Row != empty_list:
                R_Round_Five_Head_Significant_Strikes_Attempted = R5_Red_Fighter_SS_Row[3].split("of")[1].strip()
                R_Round_Five_Head_Significant_Strikes_Landed = R5_Red_Fighter_SS_Row[3].split("of")[0].strip()
                R_Round_Five_Body_Significant_Strikes_Attempted = R5_Red_Fighter_SS_Row[4].split("of")[1].strip()
                R_Round_Five_Body_Significant_Strikes_Landed = R5_Red_Fighter_SS_Row[4].split("of")[0].strip()
                R_Round_Five_Leg_Significant_Strikes_Attempted = R5_Red_Fighter_SS_Row[5].split("of")[1].strip()
                R_Round_Five_Leg_Significant_Strikes_Landed = R5_Red_Fighter_SS_Row[5].split("of")[0].strip()
                R_Round_Five_Significant_Strikes_Distance_Landed = R5_Red_Fighter_SS_Row[6].split("of")[0].strip()
                R_Round_Five_Significant_Strikes_Distance_Attempted = R5_Red_Fighter_SS_Row[6].split("of")[1].strip()
                R_Round_Five_Significant_Strikes_Clinch_Landed = R5_Red_Fighter_SS_Row[7].split("of")[0].strip()
                R_Round_Five_Significant_Strikes_Clinch_Attempted = R5_Red_Fighter_SS_Row[7].split("of")[1].strip()
                R_Round_Five_Significant_Strikes_Ground_Landed = R5_Red_Fighter_SS_Row[8].split("of")[0].strip()
                R_Round_Five_Significant_Strikes_Ground_Attempted = R5_Red_Fighter_SS_Row[8].split("of")[1].strip()


            # Dictionary to be used for writing to CSV file.
            fight_stat_dict = {
                "Event_Date": event_date_cleaned,
                "Weight_Class": bout_weight_class,
                "Max_Rounds": max_rounds,
                "Ending_Round": ending_round,
                "Winner": winner,
                "Win_By": fight_win_method,

                "B_Name": blue_fighter,
                "B_Age": blue_fighter_Age,
                "B_Height": blue_fighter_Height,
                "B_Weight": blue_fighter_Weight,
                "B_Reach": blue_fighter_Reach,
                "B_Stance": blue_fighter_Stance,
                "B_Wins": blue_fighter_Wins,
                "B_Losses": blue_fighter_Losses,
                "B_Draws": blue_fighter_Draws,
                "B_Career_Significant_Strikes_Landed_PM": blue_fighter_SLpM,
                "B_Career_Significant_Strikes_Absorbed_PM": blue_fighter_SApM,
                "B_Career_Striking_Accuracy": blue_fighter_Str_Acc,
                "B_Career_Significant_Strike_Defence": blue_fighter_Str_Def,
                "B_Career_Takedown_Average": blue_fighter_Td_Avg,
                "B_Career_Takedown_Accuracy": blue_fighter_Td_Acc,
                "B_Career_Takedown_Defence": blue_fighter_Td_Def,
                "B_Career_Submission_Average": blue_fighter_Sub_Avg,
                "B_Knockdowns": blue_knockdowns,
                "B_Significant_Strikes_Landed": Blue_Significant_Strikes_Landed,
                "B_Significant_Strikes_Attempted": Blue_Significant_Strikes_Attempted,
                "B_Significant_Strike_Perc": Blue_Significant_Strike_Perc,
                "B_Significant_Strikes_Distance_Landed": Blue_Distance_Significant_Strikes_Landed,
                "B_Significant_Strikes_Distance_Attempted": Blue_Distance_Significant_Strikes_Attempted,
                "B_Significant_Strikes_Clinch_Landed": Blue_Clinch_Significant_Strikes_Landed,
                "B_Significant_Strikes_Clinch_Attempted": Blue_Clinch_Significant_Strikes_Attempted,
                "B_Significant_Strikes_Ground_Landed": Blue_Ground_Significant_Strikes_Landed,
                "B_Significant_Strikes_Ground_Attempted": Blue_Ground_Significant_Strikes_Attempted,
                "B_Head_Significant_Strikes_Attempted": Blue_Head_Significant_Strikes_Attempted,
                "B_Head_Significant_Strikes_Landed": Blue_Head_Significant_Strikes_Landed,
                "B_Body_Significant_Strikes_Attempted": Blue_Body_Significant_Strikes_Attempted,
                "B_Body_Significant_Strikes_Landed": Blue_Body_Significant_Strikes_Landed,
                "B_Leg_Significant_Strikes_Attempted": Blue_Leg_Significant_Strikes_Attempted,
                "B_Leg_Significant_Strikes_Landed": Blue_Leg_Significant_Strikes_Landed,
                "B_Total_Strikes_Attempted": Blue_Total_Strikes_Attempted,
                "B_Total_Strikes_Landed": Blue_Total_Strikes_Landed,
                "B_Takedowns_Attempted": Blue_Takedowns_Attempted,
                "B_Takedowns_Landed": Blue_Takedowns_Landed,
                "B_Takedown_Perc": Blue_Takedown_Perc,
                "B_Submission_Attempts": Blue_Submissions_Attempted,
                "B_Grappling_Reversals": Blue_Grappling_Reversals,
                "B_Grappling_Control_Time": Blue_Grappling_Control_Time,
                "B_Round_One_Knockdowns": B_Round_One_Knockdowns,
                "B_Round_One_Significant_Strikes_Landed": B_Round_One_Significant_Strikes_Landed,
                "B_Round_One_Significant_Strikes_Attempted": B_Round_One_Significant_Strikes_Attempted,
                "B_Round_One_Significant_Strike_Perc": B_Round_One_Significant_Strike_Perc,
                "B_Round_One_Significant_Strikes_Distance_Landed": B_Round_One_Significant_Strikes_Distance_Landed,
                "B_Round_One_Significant_Strikes_Distance_Attempted": B_Round_One_Significant_Strikes_Distance_Attempted,
                "B_Round_One_Significant_Strikes_Clinch_Landed": B_Round_One_Significant_Strikes_Clinch_Landed,
                "B_Round_One_Significant_Strikes_Clinch_Attempted": B_Round_One_Significant_Strikes_Clinch_Attempted,
                "B_Round_One_Significant_Strikes_Ground_Landed": B_Round_One_Significant_Strikes_Ground_Landed,
                "B_Round_One_Significant_Strikes_Ground_Attempted": B_Round_One_Significant_Strikes_Ground_Attempted,
                "B_Round_One_Head_Significant_Strikes_Attempted": B_Round_One_Head_Significant_Strikes_Attempted,
                "B_Round_One_Head_Significant_Strikes_Landed": B_Round_One_Head_Significant_Strikes_Landed,
                "B_Round_One_Body_Significant_Strikes_Attempted": B_Round_One_Body_Significant_Strikes_Attempted,
                "B_Round_One_Body_Significant_Strikes_Landed": B_Round_One_Body_Significant_Strikes_Landed,
                "B_Round_One_Leg_Significant_Strikes_Attempted": B_Round_One_Leg_Significant_Strikes_Attempted,
                "B_Round_One_Leg_Significant_Strikes_Landed": B_Round_One_Leg_Significant_Strikes_Landed,
                "B_Round_One_Total_Strikes_Attempted": B_Round_One_Total_Strikes_Attempted,
                "B_Round_One_Total_Strikes_Landed": B_Round_One_Total_Strikes_Landed,
                "B_Round_One_Takedowns_Attempted": B_Round_One_Takedowns_Attempted,
                "B_Round_One_Takedowns_Landed": B_Round_One_Takedowns_Landed,
                "B_Round_One_Takedown_Perc": B_Round_One_Takedown_Perc,
                "B_Round_One_Submission_Attempts": B_Round_One_Submission_Attempts,
                "B_Round_One_Grappling_Reversals": B_Round_One_Grappling_Reversals,
                "B_Round_One_Grappling_Control_Time": B_Round_One_Grappling_Control_Time,
                "B_Round_Two_Knockdowns": B_Round_Two_Knockdowns,
                "B_Round_Two_Significant_Strikes_Landed": B_Round_Two_Significant_Strikes_Landed,
                "B_Round_Two_Significant_Strikes_Attempted": B_Round_Two_Significant_Strikes_Attempted,
                "B_Round_Two_Significant_Strike_Perc": B_Round_Two_Significant_Strike_Perc,
                "B_Round_Two_Significant_Strikes_Distance_Landed": B_Round_Two_Significant_Strikes_Distance_Landed,
                "B_Round_Two_Significant_Strikes_Distance_Attempted": B_Round_Two_Significant_Strikes_Distance_Attempted,
                "B_Round_Two_Significant_Strikes_Clinch_Landed": B_Round_Two_Significant_Strikes_Clinch_Landed,
                "B_Round_Two_Significant_Strikes_Clinch_Attempted": B_Round_Two_Significant_Strikes_Clinch_Attempted,
                "B_Round_Two_Significant_Strikes_Ground_Landed": B_Round_Two_Significant_Strikes_Ground_Landed,
                "B_Round_Two_Significant_Strikes_Ground_Attempted": B_Round_Two_Significant_Strikes_Ground_Attempted,
                "B_Round_Two_Head_Significant_Strikes_Attempted": B_Round_Two_Head_Significant_Strikes_Attempted,
                "B_Round_Two_Head_Significant_Strikes_Landed": B_Round_Two_Head_Significant_Strikes_Landed,
                "B_Round_Two_Body_Significant_Strikes_Attempted": B_Round_Two_Body_Significant_Strikes_Attempted,
                "B_Round_Two_Body_Significant_Strikes_Landed": B_Round_Two_Body_Significant_Strikes_Landed,
                "B_Round_Two_Leg_Significant_Strikes_Attempted": B_Round_Two_Leg_Significant_Strikes_Attempted,
                "B_Round_Two_Leg_Significant_Strikes_Landed": B_Round_Two_Leg_Significant_Strikes_Landed,
                "B_Round_Two_Total_Strikes_Attempted": B_Round_Two_Total_Strikes_Attempted,
                "B_Round_Two_Total_Strikes_Landed": B_Round_Two_Total_Strikes_Landed,
                "B_Round_Two_Takedowns_Attempted": B_Round_Two_Takedowns_Attempted,
                "B_Round_Two_Takedowns_Landed": B_Round_Two_Takedowns_Landed,
                "B_Round_Two_Takedown_Perc": B_Round_Two_Takedown_Perc,
                "B_Round_Two_Submission_Attempts": B_Round_Two_Submission_Attempts,
                "B_Round_Two_Grappling_Reversals": B_Round_Two_Grappling_Reversals,
                "B_Round_Two_Grappling_Control_Time": B_Round_Two_Grappling_Control_Time,
                "B_Round_Three_Knockdowns": B_Round_Three_Knockdowns,
                "B_Round_Three_Significant_Strikes_Landed": B_Round_Three_Significant_Strikes_Landed,
                "B_Round_Three_Significant_Strikes_Attempted": B_Round_Three_Significant_Strikes_Attempted,
                "B_Round_Three_Significant_Strike_Perc": B_Round_Three_Significant_Strike_Perc,
                "B_Round_Three_Significant_Strikes_Distance_Landed": B_Round_Three_Significant_Strikes_Distance_Landed,
                "B_Round_Three_Significant_Strikes_Distance_Attempted": B_Round_Three_Significant_Strikes_Distance_Attempted,
                "B_Round_Three_Significant_Strikes_Clinch_Landed": B_Round_Three_Significant_Strikes_Clinch_Landed,
                "B_Round_Three_Significant_Strikes_Clinch_Attempted": B_Round_Three_Significant_Strikes_Clinch_Attempted,
                "B_Round_Three_Significant_Strikes_Ground_Landed": B_Round_Three_Significant_Strikes_Ground_Landed,
                "B_Round_Three_Significant_Strikes_Ground_Attempted": B_Round_Three_Significant_Strikes_Ground_Attempted,
                "B_Round_Three_Head_Significant_Strikes_Attempted": B_Round_Three_Head_Significant_Strikes_Attempted,
                "B_Round_Three_Head_Significant_Strikes_Landed": B_Round_Three_Head_Significant_Strikes_Landed,
                "B_Round_Three_Body_Significant_Strikes_Attempted": B_Round_Three_Body_Significant_Strikes_Attempted,
                "B_Round_Three_Body_Significant_Strikes_Landed": B_Round_Three_Body_Significant_Strikes_Landed,
                "B_Round_Three_Leg_Significant_Strikes_Attempted": B_Round_Three_Leg_Significant_Strikes_Attempted,
                "B_Round_Three_Leg_Significant_Strikes_Landed": B_Round_Three_Leg_Significant_Strikes_Landed,
                "B_Round_Three_Total_Strikes_Attempted": B_Round_Three_Total_Strikes_Attempted,
                "B_Round_Three_Total_Strikes_Landed": B_Round_Three_Total_Strikes_Landed,
                "B_Round_Three_Takedowns_Attempted": B_Round_Three_Takedowns_Attempted,
                "B_Round_Three_Takedowns_Landed": B_Round_Three_Takedowns_Landed,
                "B_Round_Three_Takedown_Perc": B_Round_Three_Takedown_Perc,
                "B_Round_Three_Submission_Attempts": B_Round_Three_Submission_Attempts,
                "B_Round_Three_Grappling_Reversals": B_Round_Three_Grappling_Reversals,
                "B_Round_Three_Grappling_Control_Time": B_Round_Three_Grappling_Control_Time,
                "B_Round_Four_Knockdowns": B_Round_Four_Knockdowns,
                "B_Round_Four_Significant_Strikes_Landed": B_Round_Four_Significant_Strikes_Landed,
                "B_Round_Four_Significant_Strikes_Attempted": B_Round_Four_Significant_Strikes_Attempted,
                "B_Round_Four_Significant_Strike_Perc": B_Round_Four_Significant_Strike_Perc,
                "B_Round_Four_Significant_Strikes_Distance_Landed": B_Round_Four_Significant_Strikes_Distance_Landed,
                "B_Round_Four_Significant_Strikes_Distance_Attempted": B_Round_Four_Significant_Strikes_Distance_Attempted,
                "B_Round_Four_Significant_Strikes_Clinch_Landed": B_Round_Four_Significant_Strikes_Clinch_Landed,
                "B_Round_Four_Significant_Strikes_Clinch_Attempted": B_Round_Four_Significant_Strikes_Clinch_Attempted,
                "B_Round_Four_Significant_Strikes_Ground_Landed": B_Round_Four_Significant_Strikes_Ground_Landed,
                "B_Round_Four_Significant_Strikes_Ground_Attempted": B_Round_Four_Significant_Strikes_Ground_Attempted,
                "B_Round_Four_Head_Significant_Strikes_Attempted": B_Round_Four_Head_Significant_Strikes_Attempted,
                "B_Round_Four_Head_Significant_Strikes_Landed": B_Round_Four_Head_Significant_Strikes_Landed,
                "B_Round_Four_Body_Significant_Strikes_Attempted": B_Round_Four_Body_Significant_Strikes_Attempted,
                "B_Round_Four_Body_Significant_Strikes_Landed": B_Round_Four_Body_Significant_Strikes_Landed,
                "B_Round_Four_Leg_Significant_Strikes_Attempted": B_Round_Four_Leg_Significant_Strikes_Attempted,
                "B_Round_Four_Leg_Significant_Strikes_Landed": B_Round_Four_Leg_Significant_Strikes_Landed,
                "B_Round_Four_Total_Strikes_Attempted": B_Round_Four_Total_Strikes_Attempted,
                "B_Round_Four_Total_Strikes_Landed": B_Round_Four_Total_Strikes_Landed,
                "B_Round_Four_Takedowns_Attempted": B_Round_Four_Takedowns_Attempted,
                "B_Round_Four_Takedowns_Landed": B_Round_Four_Takedowns_Landed,
                "B_Round_Four_Takedown_Perc": B_Round_Four_Takedown_Perc,
                "B_Round_Four_Submission_Attempts": B_Round_Four_Submission_Attempts,
                "B_Round_Four_Grappling_Reversals": B_Round_Four_Grappling_Reversals,
                "B_Round_Four_Grappling_Control_Time": B_Round_Four_Grappling_Control_Time,
                "B_Round_Five_Knockdowns": B_Round_Five_Knockdowns,
                "B_Round_Five_Significant_Strikes_Landed": B_Round_Five_Significant_Strikes_Landed,
                "B_Round_Five_Significant_Strikes_Attempted": B_Round_Five_Significant_Strikes_Attempted,
                "B_Round_Five_Significant_Strike_Perc": B_Round_Five_Significant_Strike_Perc,
                "B_Round_Five_Significant_Strikes_Distance_Landed": B_Round_Five_Significant_Strikes_Distance_Landed,
                "B_Round_Five_Significant_Strikes_Distance_Attempted": B_Round_Five_Significant_Strikes_Distance_Attempted,
                "B_Round_Five_Significant_Strikes_Clinch_Landed": B_Round_Five_Significant_Strikes_Clinch_Landed,
                "B_Round_Five_Significant_Strikes_Clinch_Attempted": B_Round_Five_Significant_Strikes_Clinch_Attempted,
                "B_Round_Five_Significant_Strikes_Ground_Landed": B_Round_Five_Significant_Strikes_Ground_Landed,
                "B_Round_Five_Significant_Strikes_Ground_Attempted": B_Round_Five_Significant_Strikes_Ground_Attempted,
                "B_Round_Five_Head_Significant_Strikes_Attempted": B_Round_Five_Head_Significant_Strikes_Attempted,
                "B_Round_Five_Head_Significant_Strikes_Landed": B_Round_Five_Head_Significant_Strikes_Landed,
                "B_Round_Five_Body_Significant_Strikes_Attempted": B_Round_Five_Body_Significant_Strikes_Attempted,
                "B_Round_Five_Body_Significant_Strikes_Landed": B_Round_Five_Body_Significant_Strikes_Landed,
                "B_Round_Five_Leg_Significant_Strikes_Attempted": B_Round_Five_Leg_Significant_Strikes_Attempted,
                "B_Round_Five_Leg_Significant_Strikes_Landed": B_Round_Five_Leg_Significant_Strikes_Landed,
                "B_Round_Five_Total_Strikes_Attempted": B_Round_Five_Total_Strikes_Attempted,
                "B_Round_Five_Total_Strikes_Landed": B_Round_Five_Total_Strikes_Landed,
                "B_Round_Five_Takedowns_Attempted": B_Round_Five_Takedowns_Attempted,
                "B_Round_Five_Takedowns_Landed": B_Round_Five_Takedowns_Landed,
                "B_Round_Five_Takedown_Perc": B_Round_Five_Takedown_Perc,
                "B_Round_Five_Submission_Attempts": B_Round_Five_Submission_Attempts,
                "B_Round_Five_Grappling_Reversals": B_Round_Five_Grappling_Reversals,
                "B_Round_Five_Grappling_Control_Time": B_Round_Five_Grappling_Control_Time,



                "R_Name": red_fighter,
                "R_Age": red_fighter_Age,
                "R_Height": red_fighter_Height,
                "R_Weight": red_fighter_Weight,
                "R_Reach": red_fighter_Reach,
                "R_Stance": red_fighter_Stance,
                "R_Wins": red_fighter_Wins,
                "R_Losses": red_fighter_Losses,
                "R_Draws": red_fighter_Draws,
                "R_Career_Significant_Strikes_Landed_PM": red_fighter_SLpM,
                "R_Career_Significant_Strikes_Absorbed_PM": red_fighter_SApM,
                "R_Career_Striking_Accuracy": red_fighter_Str_Acc,
                "R_Career_Significant_Strike_Defence": red_fighter_Str_Def,
                "R_Career_Takedown_Average": red_fighter_Td_Avg,
                "R_Career_Takedown_Accuracy": red_fighter_Td_Acc,
                "R_Career_Takedown_Defence": red_fighter_Td_Def,
                "R_Career_Submission_Average": red_fighter_Sub_Avg,
                "R_Knockdowns": red_knockdowns,
                "R_Significant_Strikes_Landed": Red_Significant_Strikes_Landed,
                "R_Significant_Strikes_Attempted": Red_Significant_Strikes_Attempted,
                "R_Significant_Strike_Perc": Red_Significant_Strike_Perc,
                "R_Significant_Strikes_Distance_Landed": Red_Distance_Significant_Strikes_Landed,
                "R_Significant_Strikes_Distance_Attempted": Red_Distance_Significant_Strikes_Attempted,
                "R_Significant_Strikes_Clinch_Landed": Red_Clinch_Significant_Strikes_Landed,
                "R_Significant_Strikes_Clinch_Attempted": Red_Clinch_Significant_Strikes_Attempted,
                "R_Significant_Strikes_Ground_Landed": Red_Ground_Significant_Strikes_Landed,
                "R_Significant_Strikes_Ground_Attempted": Red_Ground_Significant_Strikes_Attempted,
                "R_Head_Significant_Strikes_Attempted": Red_Head_Significant_Strikes_Attempted,
                "R_Head_Significant_Strikes_Landed": Red_Head_Significant_Strikes_Landed,
                "R_Body_Significant_Strikes_Attempted": Red_Body_Significant_Strikes_Attempted,
                "R_Body_Significant_Strikes_Landed": Red_Body_Significant_Strikes_Landed,
                "R_Leg_Significant_Strikes_Attempted": Red_Leg_Significant_Strikes_Attempted,
                "R_Leg_Significant_Strikes_Landed": Red_Leg_Significant_Strikes_Landed,
                "R_Total_Strikes_Attempted": Red_Total_Strikes_Attempted,
                "R_Total_Strikes_Landed": Red_Total_Strikes_Landed,
                "R_Takedowns_Attempted": Red_Takedowns_Attepmted,
                "R_Takedowns_Landed": Red_Takedowns_Landed,
                "R_Takedown_Perc": Red_Takedown_Perc,
                "R_Submission_Attempts": Red_Submissions_Attempted,
                "R_Grappling_Reversals": Red_Grappling_Reversals,
                "R_Grappling_Control_Time": Red_Grappling_Control_Time,
                "R_Round_One_Knockdowns": R_Round_One_Knockdowns,
                "R_Round_One_Significant_Strikes_Landed": R_Round_One_Significant_Strikes_Landed,
                "R_Round_One_Significant_Strikes_Attempted": R_Round_One_Significant_Strikes_Attempted,
                "R_Round_One_Significant_Strike_Perc": R_Round_One_Significant_Strike_Perc,
                "R_Round_One_Significant_Strikes_Distance_Attempted": R_Round_One_Significant_Strikes_Distance_Attempted,
                "R_Round_One_Significant_Strikes_Distance_Landed": R_Round_One_Significant_Strikes_Distance_Landed,
                "R_Round_One_Significant_Strikes_Clinch_Attempted": R_Round_One_Significant_Strikes_Clinch_Attempted,
                "R_Round_One_Significant_Strikes_Clinch_Landed": R_Round_One_Significant_Strikes_Clinch_Landed,
                "R_Round_One_Significant_Strikes_Ground_Attempted": R_Round_One_Significant_Strikes_Ground_Attempted,
                "R_Round_One_Significant_Strikes_Ground_Landed": R_Round_One_Significant_Strikes_Ground_Landed,
                "R_Round_One_Head_Significant_Strikes_Attempted": R_Round_One_Head_Significant_Strikes_Attempted,
                "R_Round_One_Head_Significant_Strikes_Landed": R_Round_One_Head_Significant_Strikes_Landed,
                "R_Round_One_Body_Significant_Strikes_Attempted": R_Round_One_Body_Significant_Strikes_Attempted,
                "R_Round_One_Body_Significant_Strikes_Landed": R_Round_One_Body_Significant_Strikes_Landed,
                "R_Round_One_Leg_Significant_Strikes_Attempted": R_Round_One_Leg_Significant_Strikes_Attempted,
                "R_Round_One_Leg_Significant_Strikes_Landed": R_Round_One_Leg_Significant_Strikes_Landed,
                "R_Round_One_Total_Strikes_Attempted": R_Round_One_Total_Strikes_Attempted,
                "R_Round_One_Total_Strikes_Landed": R_Round_One_Total_Strikes_Landed,
                "R_Round_One_Takedowns_Attempted": R_Round_One_Takedowns_Attempted,
                "R_Round_One_Takedowns_Landed": R_Round_One_Takedowns_Landed,
                "R_Round_One_Takedown_Perc": R_Round_One_Takedown_Perc,
                "R_Round_One_Submission_Attempts": R_Round_One_Submission_Attempts,
                "R_Round_One_Grappling_Reversals": R_Round_One_Grappling_Reversals,
                "R_Round_One_Grappling_Control_Time": R_Round_One_Grappling_Control_Time,
                "R_Round_Two_Knockdowns": R_Round_Two_Knockdowns,
                "R_Round_Two_Significant_Strikes_Landed": R_Round_Two_Significant_Strikes_Landed,
                "R_Round_Two_Significant_Strikes_Attempted": R_Round_Two_Significant_Strikes_Attempted,
                "R_Round_Two_Significant_Strike_Perc": R_Round_Two_Significant_Strike_Perc,
                "R_Round_Two_Significant_Strikes_Distance_Attempted": R_Round_Two_Significant_Strikes_Distance_Attempted,
                "R_Round_Two_Significant_Strikes_Distance_Landed": R_Round_Two_Significant_Strikes_Distance_Landed,
                "R_Round_Two_Significant_Strikes_Clinch_Attempted": R_Round_Two_Significant_Strikes_Clinch_Attempted,
                "R_Round_Two_Significant_Strikes_Clinch_Landed": R_Round_Two_Significant_Strikes_Clinch_Landed,
                "R_Round_Two_Significant_Strikes_Ground_Attempted": R_Round_Two_Significant_Strikes_Ground_Attempted,
                "R_Round_Two_Significant_Strikes_Ground_Landed": R_Round_Two_Significant_Strikes_Ground_Landed,
                "R_Round_Two_Head_Significant_Strikes_Attempted": R_Round_Two_Head_Significant_Strikes_Attempted,
                "R_Round_Two_Head_Significant_Strikes_Landed": R_Round_Two_Head_Significant_Strikes_Landed,
                "R_Round_Two_Body_Significant_Strikes_Attempted": R_Round_Two_Body_Significant_Strikes_Attempted,
                "R_Round_Two_Body_Significant_Strikes_Landed": R_Round_Two_Body_Significant_Strikes_Landed,
                "R_Round_Two_Leg_Significant_Strikes_Attempted": R_Round_Two_Leg_Significant_Strikes_Attempted,
                "R_Round_Two_Leg_Significant_Strikes_Landed": R_Round_Two_Leg_Significant_Strikes_Landed,
                "R_Round_Two_Total_Strikes_Attempted": R_Round_Two_Total_Strikes_Attempted,
                "R_Round_Two_Total_Strikes_Landed": R_Round_Two_Total_Strikes_Landed,
                "R_Round_Two_Takedowns_Attempted": R_Round_Two_Takedowns_Attempted,
                "R_Round_Two_Takedowns_Landed": R_Round_Two_Takedowns_Landed,
                "R_Round_Two_Takedown_Perc": R_Round_Two_Takedown_Perc,
                "R_Round_Two_Submission_Attempts": R_Round_Two_Submission_Attempts,
                "R_Round_Two_Grappling_Reversals": R_Round_Two_Grappling_Reversals,
                "R_Round_Two_Grappling_Control_Time": R_Round_Two_Grappling_Control_Time,
                "R_Round_Three_Knockdowns": R_Round_Three_Knockdowns,
                "R_Round_Three_Significant_Strikes_Landed": R_Round_Three_Significant_Strikes_Landed,
                "R_Round_Three_Significant_Strikes_Attempted": R_Round_Three_Significant_Strikes_Attempted,
                "R_Round_Three_Significant_Strike_Perc": R_Round_Three_Significant_Strike_Perc,
                "R_Round_Three_Significant_Strikes_Distance_Attempted": R_Round_Three_Significant_Strikes_Distance_Attempted,
                "R_Round_Three_Significant_Strikes_Distance_Landed": R_Round_Three_Significant_Strikes_Distance_Landed,
                "R_Round_Three_Significant_Strikes_Clinch_Attempted": R_Round_Three_Significant_Strikes_Clinch_Attempted,
                "R_Round_Three_Significant_Strikes_Clinch_Landed": R_Round_Three_Significant_Strikes_Clinch_Landed,
                "R_Round_Three_Significant_Strikes_Ground_Attempted": R_Round_Three_Significant_Strikes_Ground_Attempted,
                "R_Round_Three_Significant_Strikes_Ground_Landed": R_Round_Three_Significant_Strikes_Ground_Landed,
                "R_Round_Three_Head_Significant_Strikes_Attempted": R_Round_Three_Head_Significant_Strikes_Attempted,
                "R_Round_Three_Head_Significant_Strikes_Landed": R_Round_Three_Head_Significant_Strikes_Landed,
                "R_Round_Three_Body_Significant_Strikes_Attempted": R_Round_Three_Body_Significant_Strikes_Attempted,
                "R_Round_Three_Body_Significant_Strikes_Landed": R_Round_Three_Body_Significant_Strikes_Landed,
                "R_Round_Three_Leg_Significant_Strikes_Attempted": R_Round_Three_Leg_Significant_Strikes_Attempted,
                "R_Round_Three_Leg_Significant_Strikes_Landed": R_Round_Three_Leg_Significant_Strikes_Landed,
                "R_Round_Three_Total_Strikes_Attempted": R_Round_Three_Total_Strikes_Attempted,
                "R_Round_Three_Total_Strikes_Landed": R_Round_Three_Total_Strikes_Landed,
                "R_Round_Three_Takedowns_Attempted": R_Round_Three_Takedowns_Attempted,
                "R_Round_Three_Takedowns_Landed": R_Round_Three_Takedowns_Landed,
                "R_Round_Three_Takedown_Perc": R_Round_Three_Takedown_Perc,
                "R_Round_Three_Submission_Attempts": R_Round_Three_Submission_Attempts,
                "R_Round_Three_Grappling_Reversals": R_Round_Three_Grappling_Reversals,
                "R_Round_Three_Grappling_Control_Time": R_Round_Three_Grappling_Control_Time,
                "R_Round_Four_Knockdowns": R_Round_Four_Knockdowns,
                "R_Round_Four_Significant_Strikes_Landed": R_Round_Four_Significant_Strikes_Landed,
                "R_Round_Four_Significant_Strikes_Attempted": R_Round_Four_Significant_Strikes_Attempted,
                "R_Round_Four_Significant_Strike_Perc": R_Round_Four_Significant_Strike_Perc,
                "R_Round_Four_Significant_Strikes_Distance_Attempted": R_Round_Four_Significant_Strikes_Distance_Attempted,
                "R_Round_Four_Significant_Strikes_Distance_Landed": R_Round_Four_Significant_Strikes_Distance_Landed,
                "R_Round_Four_Significant_Strikes_Clinch_Attempted": R_Round_Four_Significant_Strikes_Clinch_Attempted,
                "R_Round_Four_Significant_Strikes_Clinch_Landed": R_Round_Four_Significant_Strikes_Clinch_Landed,
                "R_Round_Four_Significant_Strikes_Ground_Attempted": R_Round_Four_Significant_Strikes_Ground_Attempted,
                "R_Round_Four_Significant_Strikes_Ground_Landed": R_Round_Four_Significant_Strikes_Ground_Landed,
                "R_Round_Four_Head_Significant_Strikes_Attempted": R_Round_Four_Head_Significant_Strikes_Attempted,
                "R_Round_Four_Head_Significant_Strikes_Landed": R_Round_Four_Head_Significant_Strikes_Landed,
                "R_Round_Four_Body_Significant_Strikes_Attempted": R_Round_Four_Body_Significant_Strikes_Attempted,
                "R_Round_Four_Body_Significant_Strikes_Landed": R_Round_Four_Body_Significant_Strikes_Landed,
                "R_Round_Four_Leg_Significant_Strikes_Attempted": R_Round_Four_Leg_Significant_Strikes_Attempted,
                "R_Round_Four_Leg_Significant_Strikes_Landed": R_Round_Four_Leg_Significant_Strikes_Landed,
                "R_Round_Four_Total_Strikes_Attempted": R_Round_Four_Total_Strikes_Attempted,
                "R_Round_Four_Total_Strikes_Landed": R_Round_Four_Total_Strikes_Landed,
                "R_Round_Four_Takedowns_Attempted": R_Round_Four_Takedowns_Attempted,
                "R_Round_Four_Takedowns_Landed": R_Round_Four_Takedowns_Landed,
                "R_Round_Four_Takedown_Perc": R_Round_Four_Takedown_Perc,
                "R_Round_Four_Submission_Attempts": R_Round_Four_Submission_Attempts,
                "R_Round_Four_Grappling_Reversals": R_Round_Four_Grappling_Reversals,
                "R_Round_Four_Grappling_Control_Time": R_Round_Four_Grappling_Control_Time,
                "R_Round_Five_Knockdowns": R_Round_Five_Knockdowns,
                "R_Round_Five_Significant_Strikes_Landed": R_Round_Five_Significant_Strikes_Landed,
                "R_Round_Five_Significant_Strikes_Attempted": R_Round_Five_Significant_Strikes_Attempted,
                "R_Round_Five_Significant_Strike_Perc": R_Round_Five_Significant_Strike_Perc,
                "R_Round_Five_Significant_Strikes_Distance_Attempted": R_Round_Five_Significant_Strikes_Distance_Attempted,
                "R_Round_Five_Significant_Strikes_Distance_Landed": R_Round_Five_Significant_Strikes_Distance_Landed,
                "R_Round_Five_Significant_Strikes_Clinch_Attempted": R_Round_Five_Significant_Strikes_Clinch_Attempted,
                "R_Round_Five_Significant_Strikes_Clinch_Landed": R_Round_Five_Significant_Strikes_Clinch_Landed,
                "R_Round_Five_Significant_Strikes_Ground_Attempted": R_Round_Five_Significant_Strikes_Ground_Attempted,
                "R_Round_Five_Significant_Strikes_Ground_Landed": R_Round_Five_Significant_Strikes_Ground_Landed,
                "R_Round_Five_Head_Significant_Strikes_Attempted": R_Round_Five_Head_Significant_Strikes_Attempted,
                "R_Round_Five_Head_Significant_Strikes_Landed": R_Round_Five_Head_Significant_Strikes_Landed,
                "R_Round_Five_Body_Significant_Strikes_Attempted": R_Round_Five_Body_Significant_Strikes_Attempted,
                "R_Round_Five_Body_Significant_Strikes_Landed": R_Round_Five_Body_Significant_Strikes_Landed,
                "R_Round_Five_Leg_Significant_Strikes_Attempted": R_Round_Five_Leg_Significant_Strikes_Attempted,
                "R_Round_Five_Leg_Significant_Strikes_Landed": R_Round_Five_Leg_Significant_Strikes_Landed,
                "R_Round_Five_Total_Strikes_Attempted": R_Round_Five_Total_Strikes_Attempted,
                "R_Round_Five_Total_Strikes_Landed": R_Round_Five_Total_Strikes_Landed,
                "R_Round_Five_Takedowns_Attempted": R_Round_Five_Takedowns_Attempted,
                "R_Round_Five_Takedowns_Landed": R_Round_Five_Takedowns_Landed,
                "R_Round_Five_Takedown_Perc": R_Round_Five_Takedown_Perc,
                "R_Round_Five_Submission_Attempts": R_Round_Five_Submission_Attempts,
                "R_Round_Five_Grappling_Reversals": R_Round_Five_Grappling_Reversals,
                "R_Round_Five_Grappling_Control_Time": R_Round_Five_Grappling_Control_Time,


            }
            print("Fight stats appended...")
            fight_stat_list.append(fight_stat_dict)

        except:
            print("Error occurred")

    path = Path("../newest_dataset.csv")
    keys = fight_stat_list[0].keys()
    # writing fight results to CSV
    if path.is_file():
        with open("../newest_dataset.csv", "a", newline='') as output_file:
            writer = csv.DictWriter(output_file, keys)
            #writer.writeheader()
            writer.writerows(fight_stat_list)
    else:
        with open("../newest_dataset.csv", "w+", newline='') as output_file:
            writer = csv.DictWriter(output_file, keys)
            writer.writeheader()
            writer.writerows(fight_stat_list)

    # storing the urls that have been tested for comparison when rerunning.
    with open("prev_scraped_urls.txt", "r+") as w:
        for link in new_fight_list:
            if link not in w.readlines():
                w.seek(0,0)
                w.write(str(link) + "\n")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    url_scraper(base_url)
    stat_scraper(url_fight_list)
