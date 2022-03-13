
import requests
from bs4 import BeautifulSoup


base_url = "http://ufcstats.com/statistics/events/completed?page=all"


# Instantiating the list to hold the URL of each fight of each event
url_fight_list = []

#Funtion created to scrape the URLs needed for fight data
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
    print("Event URL Extraction COMPLETE. Moving on...\n
            Extracting fight stat URLs...")

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

    # USER MESSAGE
    print("Fight stat URL Extraction COMPLETED.")




# Function that intakes the fight urls and gathers stats.
def stat_scraper(fight_list):

    # Looping through the urls in fight_list
    for url in fight_list:

        fight_stat_page = requests.get(url)
        stat_soup = BeautifulSoup(fight_stat_page.content, "html.parser")
        # Div that hold essentially all the pages elements
        fighter_name_main_div = stat_soup.find("div", {"class": "b-fight-details"})

        # Getting fighter corner color
        red_fighter_div = fighter_name_main_div.find("i", {"class": "b-fight-details__charts-name b-fight-details__charts-name_pos_left js-chart-name"})
        blue_fighter_div = fighter_name_main_div.find("i", {"class": "b-fight-details__charts-name b-fight-details__charts-name_pos_right js-chart-name"})

        # fighter name assigned to corner color
        blue_fighter = blue_fighter_div.text.strip()
        red_fighter = red_fighter_div.text.strip()

        winner = ""

        # Getting the winners name
        for div in fighter_name_main_div.find_all("div", {"class": "b-fight-details__person"}):
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
        method_div  = outcome_div.find("i", {"style": "font-style: normal"})

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
                max_rounds_split = i.next_sibling.text.split("Rnd", 1)
                max_rounds = max_rounds_split[0]





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


            # Splitting total table stats assigning to each color
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
        Red_Head_Significant_Strikes_Landed = red_sig_strike_fighter_row[3].split("of")[0]
        Red_Head_Significant_Strikes_Attempted = red_sig_strike_fighter_row[3].split("of")[1]
        Blue_Head_Significant_Strikes_Landed = blue_sig_strike_fighter_row[3].split("of")[0]
        Blue_Head_Significant_Strikes_Attempted = blue_sig_strike_fighter_row[3].split("of")[1]

        Red_Body_Significant_Strikes_Landed = red_sig_strike_fighter_row[4].split("of")[0]
        Red_Body_Significant_Strikes_Attempted = red_sig_strike_fighter_row[4].split("of")[1]
        Blue_Body_Significant_Strikes_Landed = blue_sig_strike_fighter_row[4].split("of")[0]
        Blue_Body_Significant_Strikes_Attempted = blue_sig_strike_fighter_row[4].split("of")[1]

        Red_Leg_Significant_Strikes_Landed = red_sig_strike_fighter_row[5].split("of")[0]
        Red_Leg_Significant_Strikes_Attempted = red_sig_strike_fighter_row[5].split("of")[1]
        Blue_Leg_Significant_Strikes_Landed = blue_sig_strike_fighter_row[5].split("of")[0]
        Blue_Leg_Significant_Strikes_Attempted = blue_sig_strike_fighter_row[5].split("of")[1]

        Red_Distance_Significant_Strikes_Landed = red_sig_strike_fighter_row[6].split("of")[0]
        Red_Distance_Significant_Strikes_Attempted = red_sig_strike_fighter_row[6].split("of")[1]
        Blue_Distance_Significant_Strikes_Landed = blue_sig_strike_fighter_row[6].split("of")[0]
        Blue_Distance_Significant_Strikes_Attempted = blue_sig_strike_fighter_row[6].split("of")[1]

        Red_Clinch_Significant_Strikes_Landed = red_sig_strike_fighter_row[7].split("of")[0]
        Red_Clinch_Significant_Strikes_Attempted = red_sig_strike_fighter_row[7].split("of")[1]
        Blue_Clinch_Significant_Strikes_Landed = blue_sig_strike_fighter_row[7].split("of")[0]
        Blue_Clinch_Significant_Strikes_Attempted = blue_sig_strike_fighter_row[7].split("of")[1]

        Red_Ground_Significant_Strikes_Landed = red_sig_strike_fighter_row[8].split("of")[0]
        Red_Ground_Significant_Strikes_Attempted = red_sig_strike_fighter_row[8].split("of")[1]
        Blue_Ground_Significant_Strikes_Landed = blue_sig_strike_fighter_row[8].split("of")[0]
        Blue_Ground_Significant_Strikes_Attempted = blue_sig_strike_fighter_row[8].split("of")[1]




        R1_TotalRedRow = []
        R2_TotalRedRow = []
        R3_TotalRedRow = []
        R4_TotalRedRow = []
        R5_TotalRedRow = []

        R1_TotalBlueRow = []
        R2_TotalBlueRow = []
        R3_TotalBlueRow = []
        R4_TotalBlueRow = []
        R5_TotalBlueRow = []

        R1_fighter1TotalRowList = []
        R1_fighter2TotalRowList = []

        R2_fighter1TotalRowList = []
        R2_fighter2TotalRowList = []

        R3_fighter1TotalRowList = []
        R3_fighter2TotalRowList = []

        R4_fighter1TotalRowList = []
        R4_fighter2TotalRowList = []

        R5_fighter1TotalRowList = []
        R5_fighter2TotalRowList = []
        round_title_list = []

        ## WORK IN PROGRESS....
        Rounds_totals_round_table = stat_soup.find_all("section", {"class": "b-fight-details__section js-fight-section"})[2]
        totals_round_table = Rounds_totals_round_table.find("table", {"class": "b-fight-details__table js-fight-table"})

        #round_title = totals_round_table.find_all("thead", {"class": "b-fight-details__table-row b-fight-details__table-row_type_head"})

        #for i in round_title:
        #    round_title_list.append(i.text.strip())

        #print(len(round_title_list))
        column = totals_round_table.findChildren("tbody")[1]
        # ROUND 1 Totals
        for i in column:
            row = i.findChildren("td")
            for x in row:
                print(x.select_one(":nth-child(1)").text)








        # Dictionary to be used for writing to CSV file.
        fight_stat_dict = {
            "Fight Details": {
                "Max_Rounds": max_rounds

            },
            "Blue": {
                "Totals": {
                    
                    ### QUESTION: Do we want the keys here to match base data headers? If so
                    ###     we should scrub to be sure they match up
                    "B_Name": blue_fighter,
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
                    "B_Body_Significant_Strikes_Laned": Blue_Body_Significant_Strikes_Landed,
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
                },
                "Rounds": {
                    1: {
                        "B_Round_One_Knockdowns":"",
                        "B_Round_One_Significant_Strikes_Landed": "",
                        "B_Round_One_Significant_Strikes_Attempted": "",
                        "B_Round_One_Significant_Strike_Perc": "",
                        "B_Round_One_Significant_Strikes_Distance": "",
                        "B_Round_One_Significant_Strikes_Clinch": "",
                        "B_Round_One_Significant_Strikes_Ground": "",
                        "B_Round_One_Head_Significant_Strikes_Attempted": "",
                        "B_Round_One_Head_Significant_Strikes_Landed": "",
                        "B_Round_One_Body_Significant_Strikes_Attempted": "",
                        "B_Round_One_Body_Significant_Strikes_Laned": "",
                        "B_Round_One_Leg_Significant_Strikes_Attempted": "",
                        "B_Round_One_Leg_Significant_Strikes_Landed": "",
                        "B_Round_One_Total_Strikes_Attempted": "",
                        "B_Round_One_Total_Strikes_Landed": "",
                        "B_Round_One_Takedowns_Attempted": "",
                        "B_Round_One_Takedowns_Landed": "",
                        "B_Round_One_Takedown_Perc": "",
                        "B_Round_One_Submission_Attempts": "",
                        "B_Round_One_Grappling_Reversals": "",
                        "B_Round_One_Grappling_Control_Time": "",



                    },
                    2: {
                        "B_Round_Two_Knockdowns": "",
                        "B_Round_Two_Significant_Strikes_Landed": "",
                        "B_Round_Two_Significant_Strikes_Attempted": "",
                        "B_Round_Two_Significant_Strike_Perc": "",
                        "B_Round_Two_Significant_Strikes_Distance": "",
                        "B_Round_Two_Significant_Strikes_Clinch": "",
                        "B_Round_Two_Significant_Strikes_Ground": "",
                        "B_Round_Two_Head_Significant_Strikes_Attempted": "",
                        "B_Round_Two_Head_Significant_Strikes_Landed": "",
                        "B_Round_Two_Body_Significant_Strikes_Attempted": "",
                        "B_Round_Two_Body_Significant_Strikes_Laned": "",
                        "B_Round_Two_Leg_Significant_Strikes_Attempted": "",
                        "B_Round_Two_Leg_Significant_Strikes_Landed": "",
                        "B_Round_Two_Total_Strikes_Attempted": "",
                        "B_Round_Two_Total_Strikes_Landed": "",
                        "B_Round_Two_Takedowns_Attempted": "",
                        "B_Round_Two_Takedowns_Landed": "",
                        "B_Round_Two_Takedown_Perc": "",
                        "B_Round_Two_Submission_Attempts": "",
                        "B_Round_Two_Grappling_Reversals": "",
                        "B_Round_Two_Grappling_Control_Time": "",
                    },
                    3: {
                        "B_Round_Three_Knockdowns": "",
                        "B_Round_Three_Significant_Strikes_Landed": "",
                        "B_Round_Three_Significant_Strikes_Attempted": "",
                        "B_Round_Three_Significant_Strike_Perc": "",
                        "B_Round_Three_Significant_Strikes_Distance": "",
                        "B_Round_Three_Significant_Strikes_Clinch": "",
                        "B_Round_Three_Significant_Strikes_Ground": "",
                        "B_Round_Three_Head_Significant_Strikes_Attempted": "",
                        "B_Round_Three_Head_Significant_Strikes_Landed": "",
                        "B_Round_Three_Body_Significant_Strikes_Attempted": "",
                        "B_Round_Three_Body_Significant_Strikes_Laned": "",
                        "B_Round_Three_Leg_Significant_Strikes_Attempted": "",
                        "B_Round_Three_Leg_Significant_Strikes_Landed": "",
                        "B_Round_Three_Total_Strikes_Attempted": "",
                        "B_Round_Three_Total_Strikes_Landed": "",
                        "B_Round_Three_Takedowns_Attempted": "",
                        "B_Round_Three_Takedowns_Landed": "",
                        "B_Round_Three_Takedown_Perc": "",
                        "B_Round_Three_Submission_Attempts": "",
                        "B_Round_Three_Grappling_Reversals": "",
                        "B_Round_Three_Grappling_Control_Time": "",
                    },
                    4: {
                        "B_Round_Four_Knockdowns": "",
                        "B_Round_Four_Significant_Strikes_Landed": "",
                        "B_Round_Four_Significant_Strikes_Attempted": "",
                        "B_Round_Four_Significant_Strike_Perc": "",
                        "B_Round_Four_Significant_Strikes_Distance": "",
                        "B_Round_Four_Significant_Strikes_Clinch": "",
                        "B_Round_Four_Significant_Strikes_Ground": "",
                        "B_Round_Four_Head_Significant_Strikes_Attempted": "",
                        "B_Round_Four_Head_Significant_Strikes_Landed": "",
                        "B_Round_Four_Body_Significant_Strikes_Attempted": "",
                        "B_Round_Four_Body_Significant_Strikes_Laned": "",
                        "B_Round_Four_Leg_Significant_Strikes_Attempted": "",
                        "B_Round_Four_Leg_Significant_Strikes_Landed": "",
                        "B_Round_Four_Total_Strikes_Attempted": "",
                        "B_Round_Four_Total_Strikes_Landed": "",
                        "B_Round_Four_Takedowns_Attempted": "",
                        "B_Round_Four_Takedowns_Landed": "",
                        "B_Round_Four_Takedown_Perc": "",
                        "B_Round_Four_Submission_Attempts": "",
                        "B_Round_Four_Grappling_Reversals": "",
                        "B_Round_Four_Grappling_Control_Time": "",
                    },
                    5: {
                        "B_Round_Five_Knockdowns": "",
                        "B_Round_Five_Significant_Strikes_Landed": "",
                        "B_Round_Five_Significant_Strikes_Attempted": "",
                        "B_Round_Five_Significant_Strike_Perc": "",
                        "B_Round_Five_Significant_Strikes_Distance": "",
                        "B_Round_Five_Significant_Strikes_Clinch": "",
                        "B_Round_Five_Significant_Strikes_Ground": "",
                        "B_Round_Five_Head_Significant_Strikes_Attempted": "",
                        "B_Round_Five_Head_Significant_Strikes_Landed": "",
                        "B_Round_Five_Body_Significant_Strikes_Attempted": "",
                        "B_Round_Five_Body_Significant_Strikes_Laned": "",
                        "B_Round_Five_Leg_Significant_Strikes_Attempted": "",
                        "B_Round_Five_Leg_Significant_Strikes_Landed": "",
                        "B_Round_Five_Total_Strikes_Attempted": "",
                        "B_Round_Five_Total_Strikes_Landed": "",
                        "B_Round_Five_Takedowns_Attempted": "",
                        "B_Round_Five_Takedowns_Landed": "",
                        "B_Round_Five_Takedown_Perc": "",
                        "B_Round_Five_Submission_Attempts": "",
                        "B_Round_Five_Grappling_Reversals": "",
                        "B_Round_Five_Grappling_Control_Time": "",
                    }

                }

            },

            "Red": {
                "Totals": {
                    "R_Name": red_fighter,
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
                    "R_Body_Significant_Strikes_Laned": Red_Body_Significant_Strikes_Landed,
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
                },

                "Rounds": {

                    1: {
                        "R_Round_One_Knockdowns": "",
                        "R_Round_One_Significant_Strikes_Landed": "",
                        "R_Round_One_Significant_Strikes_Attempted": "",
                        "R_Round_One_Significant_Strike_Perc": "",
                        "R_Round_One_Significant_Strikes_Distance": "",
                        "R_Round_One_Significant_Strikes_Clinch": "",
                        "R_Round_One_Significant_Strikes_Ground": "",
                        "R_Round_One_Head_Significant_Strikes_Attempted": "",
                        "R_Round_One_Head_Significant_Strikes_Landed": "",
                        "R_Round_One_Body_Significant_Strikes_Attempted": "",
                        "R_Round_One_Body_Significant_Strikes_Laned": "",
                        "R_Round_One_Leg_Significant_Strikes_Attempted": "",
                        "R_Round_One_Leg_Significant_Strikes_Landed": "",
                        "R_Round_One_Total_Strikes_Attempted": "",
                        "R_Round_One_Total_Strikes_Landed": "",
                        "R_Round_One_Takedowns_Attempted": "",
                        "R_Round_One_Takedowns_Landed": "",
                        "R_Round_One_Takedown_Perc": "",
                        "R_Round_One_Submission_Attempts": "",
                        "R_Round_One_Grappling_Reversals": "",
                        "R_Round_One_Grappling_Control_Time": "",

                    },
                    2: {
                        "R_Round_Two_Knockdowns": "",
                        "R_Round_Two_Significant_Strikes_Landed": "",
                        "R_Round_Two_Significant_Strikes_Attempted": "",
                        "R_Round_Two_Significant_Strike_Perc": "",
                        "R_Round_Two_Significant_Strikes_Distance": "",
                        "R_Round_Two_Significant_Strikes_Clinch": "",
                        "R_Round_Two_Significant_Strikes_Ground": "",
                        "R_Round_Two_Head_Significant_Strikes_Attempted": "",
                        "R_Round_Two_Head_Significant_Strikes_Landed": "",
                        "R_Round_Two_Body_Significant_Strikes_Attempted": "",
                        "R_Round_Two_Body_Significant_Strikes_Laned": "",
                        "R_Round_Two_Leg_Significant_Strikes_Attempted": "",
                        "R_Round_Two_Leg_Significant_Strikes_Landed": "",
                        "R_Round_Two_Total_Strikes_Attempted": "",
                        "R_Round_Two_Total_Strikes_Landed": "",
                        "R_Round_Two_Takedowns_Attempted": "",
                        "R_Round_Two_Takedowns_Landed": "",
                        "R_Round_Two_Takedown_Perc": "",
                        "R_Round_Two_Submission_Attempts": "",
                        "R_Round_Two_Grappling_Reversals": "",
                        "R_Round_Two_Grappling_Control_Time": "",
                    },
                    3: {
                        "R_Round_Three_Knockdowns": "",
                        "R_Round_Three_Significant_Strikes_Landed": "",
                        "R_Round_Three_Significant_Strikes_Attempted": "",
                        "R_Round_Three_Significant_Strike_Perc": "",
                        "R_Round_Three_Significant_Strikes_Distance": "",
                        "R_Round_Three_Significant_Strikes_Clinch": "",
                        "R_Round_Three_Significant_Strikes_Ground": "",
                        "R_Round_Three_Head_Significant_Strikes_Attempted": "",
                        "R_Round_Three_Head_Significant_Strikes_Landed": "",
                        "R_Round_Three_Body_Significant_Strikes_Attempted": "",
                        "R_Round_Three_Body_Significant_Strikes_Laned": "",
                        "R_Round_Three_Leg_Significant_Strikes_Attempted": "",
                        "R_Round_Three_Leg_Significant_Strikes_Landed": "",
                        "R_Round_Three_Total_Strikes_Attempted": "",
                        "R_Round_Three_Total_Strikes_Landed": "",
                        "R_Round_Three_Takedowns_Attempted": "",
                        "R_Round_Three_Takedowns_Landed": "",
                        "R_Round_Three_Takedown_Perc": "",
                        "R_Round_Three_Submission_Attempts": "",
                        "R_Round_Three_Grappling_Reversals": "",
                        "R_Round_Three_Grappling_Control_Time": "",
                    },
                    4: {
                        "R_Round_Four_Knockdowns": "",
                        "R_Round_Four_Significant_Strikes_Landed": "",
                        "R_Round_Four_Significant_Strikes_Attempted": "",
                        "R_Round_Four_Significant_Strike_Perc": "",
                        "R_Round_Four_Significant_Strikes_Distance": "",
                        "R_Round_Four_Significant_Strikes_Clinch": "",
                        "R_Round_Four_Significant_Strikes_Ground": "",
                        "R_Round_Four_Head_Significant_Strikes_Attempted": "",
                        "R_Round_Four_Head_Significant_Strikes_Landed": "",
                        "R_Round_Four_Body_Significant_Strikes_Attempted": "",
                        "R_Round_Four_Body_Significant_Strikes_Laned": "",
                        "R_Round_Four_Leg_Significant_Strikes_Attempted": "",
                        "R_Round_Four_Leg_Significant_Strikes_Landed": "",
                        "R_Round_Four_Total_Strikes_Attempted": "",
                        "R_Round_Four_Total_Strikes_Landed": "",
                        "R_Round_Four_Takedowns_Attempted": "",
                        "R_Round_Four_Takedowns_Landed": "",
                        "R_Round_Four_Takedown_Perc": "",
                        "R_Round_Four_Submission_Attempts": "",
                        "R_Round_Four_Grappling_Reversals": "",
                        "R_Round_Four_Grappling_Control_Time": "",
                    },
                    5: {
                        "R_Round_Five_Knockdowns": "",
                        "R_Round_Five_Significant_Strikes_Landed": "",
                        "R_Round_Five_Significant_Strikes_Attempted": "",
                        "R_Round_Five_Significant_Strike_Perc": "",
                        "R_Round_Five_Significant_Strikes_Distance": "",
                        "R_Round_Five_Significant_Strikes_Clinch": "",
                        "R_Round_Five_Significant_Strikes_Ground": "",
                        "R_Round_Five_Head_Significant_Strikes_Attempted": "",
                        "R_Round_Five_Head_Significant_Strikes_Landed": "",
                        "R_Round_Five_Body_Significant_Strikes_Attempted": "",
                        "R_Round_Five_Body_Significant_Strikes_Laned": "",
                        "R_Round_Five_Leg_Significant_Strikes_Attempted": "",
                        "R_Round_Five_Leg_Significant_Strikes_Landed": "",
                        "R_Round_Five_Total_Strikes_Attempted": "",
                        "R_Round_Five_Total_Strikes_Landed": "",
                        "R_Round_Five_Takedowns_Attempted": "",
                        "R_Round_Five_Takedowns_Landed": "",
                        "R_Round_Five_Takedown_Perc": "",
                        "R_Round_Five_Submission_Attempts": "",
                        "R_Round_Five_Grappling_Reversals": "",
                        "R_Round_Five_Grappling_Control_Time": "",
                    }

                }
            },




            "Fight Outcome": {
                "Ending_Round": ending_round,
                "Winner": winner,
                "Win_By": fight_win_method
            }
        }







# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    url_scraper(base_url)
    stat_scraper(url_fight_list)


