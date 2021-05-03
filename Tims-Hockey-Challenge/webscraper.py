from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def processTableIntoPlayerList(table):
    player_list = []
    rows = table.find_elements_by_tag_name('tr')
    for row in rows:
        player_element = row.find_element_by_tag_name('a')
        player_link = player_element.get_attribute('href')
        player_id = int(player_link[-7:])
        player_list.append(player_id)
    return player_list

def obtainPlayerSelectionLists():
    path = 'C:\Program Files (x86)\chromedriver.exe'
    driver = webdriver.Chrome(path)

    link = 'https://timmies.zorbane.com/'
    driver.get(link)

    selection_lists = [[], [], []]

    try:
        # wait (10 sec max) until the last table is shown on the page
        page = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'table'))
        )
        time.sleep(2) # Add a delay just to be safe
        print('Tim Hortons Hockey Challenge lists page opened')

        tables = driver.find_elements_by_tag_name('tbody')
        selection_lists[0] = processTableIntoPlayerList(tables[0])
        selection_lists[1] = processTableIntoPlayerList(tables[1])
        selection_lists[2] = processTableIntoPlayerList(tables[2])
        print('All 3 player selection lists obtained')

    finally:
        driver.quit()
        return selection_lists

