import csv
import time
import re

from selenium import webdriver

def scrape_sc2_international(driver, player_tlpd_id):
    driver.get("https://tl.net/tlpd/sc2-international/players/" + str(player_tlpd_id))
    birthday = None

    try:
        el = driver.find_element_by_xpath("//div[@id='main-container']/div[@id='main-content']/div[@class='roundcont']/p[4]")
        text = el.get_attribute("innerText")
        text_split = re.split('(\d{4}-\d{2}-\d{2})', text, 1)
        birthday = text_split[1]
    except Exception as e:
        # print("ERROR: Cound not find birthday for " + player_tlpd_id)
        pass

    return birthday

def scrape_liquipedia(driver, player_tag):
    driver.get("https://liquipedia.net/starcraft2/" + player_tag)
    birthday = None

    try:
        el = driver.find_element_by_xpath('//span[@class="bday"]')
        birthday = el.get_attribute("innerText")
    except Exception as e:
        # print("ERROR: Cound not find birthday for " + player_id)
        pass

    return birthday

def scrape_birthdays(player_dataframe):
    birthday_list = []

    start_time = time.time()
    driver = webdriver.Chrome("tools/chromedriver.exe")

    try:
        for index, player in player_dataframe.iterrows():
            birthday = None

            if player.tlpd_id > -1:
                birthday = scrape_sc2_international(driver, player.tlpd_id)

            if birthday is None:
                birthday = scrape_liquipedia(driver, player.tag)

            birthday_list.append({ "player_id": index, "tlpd_id": player.tlpd_id, "birthday": birthday })
    except Exception as e:
        print("ERROR: ", e)

    driver.close()
    print("Finished scraping in %d", time.time() - start_time)
    
    return birthday_list

def exctract_birthday_csv(player_dataframe, filename):
    birthday_list = scrape_birthdays(player_dataframe)

    csv_columns = ["player_id", "tlpd_id", "birthday"]
    csv_file = filename

    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = csv_columns)
            writer.writeheader()
            for data in birthday_list:
                writer.writerow(data)
    except IOError:
        print("I/O error")
