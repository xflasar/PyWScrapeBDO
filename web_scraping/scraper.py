import requests
from bs4 import BeautifulSoup
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

url = "https://bdocodex.com/us/"

def scrape_links_from_initial_page():
    try:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            mainCategories = []
            subCategories = []
            subCategoriesCounts = []
            subCategoryCounter = 0
            linksToGoThru = ['weapon', 'subweapon', 'awakening', 'armor', 'costume', 'accessory', 'items/']
            currentMainCategory = None  # Track the current main category

            for lTGT in linksToGoThru:
                pattern = re.compile(r'^/us/' + lTGT)
                for a_tag in soup.find_all('a', href=pattern):
                    link = a_tag.get('href')
                    if not link.startswith('/us/items/version/'):
                        linkSplited = link.split('/')
                        if link.startswith('/us/items'):
                            if len(linkSplited) > 3:
                                if linkSplited[3] not in mainCategories and linkSplited[3] != '':
                                    if linkSplited[3] == 'adventuretomes' or linkSplited[3] == 'artifacts':
                                        subCategoriesCounts.append(1)
                                        mainCategories.append(linkSplited[3])
                                        links.append(link)
                                    else:
                                      mainCategories.append(linkSplited[3])
                                      # Update subcategory count for the current main category
                                      if currentMainCategory is not None:
                                          subCategoriesCounts.append(subCategoryCounter)
                                      # Reset subcategory counter for new main category
                                      subCategoryCounter = 0
                                if len(linkSplited) > 4:
                                    if linkSplited[4] not in subCategories and linkSplited[4] != '':
                                        subCategories.append(linkSplited[4])
                                        subCategoryCounter += 1  # Increment sub category counter
                                        links.append(link)
                        else:
                            if len(linkSplited) > 2:
                                if linkSplited[2] not in mainCategories and linkSplited[2] != '':
                                    mainCategories.append(linkSplited[2])
                                    # Update subcategory count for the current main category
                                    if currentMainCategory is not None:
                                        subCategoriesCounts.append(subCategoryCounter)
                                    # Reset subcategory counter for new main category
                                    subCategoryCounter = 0
                                if len(linkSplited) > 3:
                                    if linkSplited[3] not in subCategories and linkSplited[3] != '':
                                        subCategories.append(linkSplited[3])
                                        subCategoryCounter += 1  # Increment sub category counter
                                        links.append(link)

                currentMainCategory = linkSplited[2] if len(linkSplited) > 2 else None  # Track the current main category

            # Add the subcategory count for the last main category
            if currentMainCategory is not None:
                subCategoriesCounts.append(subCategoryCounter)

            print("Total number of links found: ", len(links))
            print("Total number of main categories found: ", len(mainCategories))
            print("Total number of sub categories found: ", len(subCategories))
            print("Total number of sub categories counts found: ", len(subCategoriesCounts))

            print("Sub categories counts: ", subCategoriesCounts)

            return links, mainCategories, subCategories, subCategoriesCounts

        else:
            print("Failed to retrieve the initial page. Status code: ", response.status_code)
            return []

    except Exception as e:
        print("An error occurred while retrieving the initial page: ", e)
        return []

def test_scrape_links_from_initial_page(links, mainCategories, subCategories, subCategoriesCounts, cateManager):
  # Bugs:
  """
    Problem with data being moved 1 subcategory backwards or basically sometimes subcategory name doesnt translate onto its items
    "furniture": {
        "cupboard": {
            "53802": "Large Wagon Lamp", -> This is wrong should be in different subcategory
            "53801": "Wagon Lamp"
        },
        "chair": {},
        "chandelier": {},
        "carpet": {},
        "walls": {}
    }
  """
  try:
    counterOk = 0
    counterFail = 0
    okLinks = []
    failLinks = []

    startTime = time.time()

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 5)

    mainCategoriesCounter = 0
    link_counter = 0
    link_counter_total = 0
    mainCategoriesD = []
    mainCategoriesD.append({ "mainCategoryName": mainCategories[mainCategoriesCounter]  , "subCategoriesData":[]})

    for link in links:
      link_counter += 1
      link_counter_total += 1

      print(f"Scraping data from page {link_counter} of {len(links)}")
      print(f"Total number of links scraped: {link_counter_total}")
      print(f"Main Category: {mainCategoriesCounter}")
      print(f"Sub Category: {mainCategoriesCounter}")

      full_url = 'https://bdocodex.com' + link
      page_number = 0

      if mainCategoriesCounter != len(mainCategories):
        if subCategoriesCounts[mainCategoriesCounter] == 0:
          mainCategoriesCounter += 1
          mainCategoriesD.append({ "mainCategoryName": mainCategories[mainCategoriesCounter]  , "subCategoriesData":[]})
          link_counter = 0
        else:
          if link_counter % subCategoriesCounts[mainCategoriesCounter] == 0 and not mainCategoriesCounter + 1 >= len(mainCategories):
            mainCategoriesCounter += 1
            mainCategoriesD.append({ "mainCategoryName": mainCategories[mainCategoriesCounter]  , "subCategoriesData":[]})
            link_counter = 0
   
      driver.get(full_url)

      subCategoriesD = []

      try:
        data_misc = driver.find_element(By.CSS_SELECTOR, "[id='WeaponTable_misc_0'], [id='EquipmentTable_misc_0'], [id='MainItemTable_misc_0'], [id='ConsumablesTable_misc_0']")
        if data_misc:
          data_misc.click()
          time.sleep(2)
      except NoSuchElementException:
        print("No input check button found.")

      while True:
      
        table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dataTables_scrollBody")))

        if table:
          counterOk += 1
          soup = BeautifulSoup(driver.page_source, 'html.parser')
          print(f"Scraping data from page {page_number} of {full_url}")

          
          try:
            item_id = soup.find_all('td', attrs={'class': 'dt-id'})
            item_title = soup.find_all('td', class_=re.compile(r'\b(dt-title|dt-title-search)\b'))
          except NoSuchElementException:
            print("No item ID or item title found.")
            break

          for itemId,itemTitle in zip(item_id,item_title):
            try:
              item = {
                "id": itemId.text,
               "name": itemTitle.next_element.next_element.contents[1]
              }
              subCategoriesD.append(item)
            except IndexError:
              print("Index out of range. HERE!1")

          next_page_button = driver.find_element(By.CLASS_NAME, "next")
          if next_page_button and not next_page_button.get_attribute('class').__contains__('disabled'):
            next_page_button.click()
            page_number += 1
          else:
            print("No more pages to be scraped")
            break
        else:
          counterFail += 1
          failLinks.append(full_url)
          break
      print('link_counter: ', link_counter - 1)
      print('link_counter: ', mainCategoriesCounter)
      print('link_counter: ', mainCategoriesD[mainCategoriesCounter])
      try:
        mainCategoriesD[mainCategoriesCounter]["subCategoriesData"].append({"subcategoryName": subCategories[link_counter_total - 1], "DropItems": subCategoriesD})
      except IndexError:
        print("Index out of range. HERE!")
    
    driver.quit()

    endTime = time.time() - startTime
    print("Data: ", mainCategoriesD)
    print("Links retrieved: ", counterOk, okLinks)
    print("Links not retrieved: ", counterFail, failLinks)
    print("Total links: ", link_counter_total)
    print("Time elapsed: ", endTime)
    return mainCategoriesD, mainCategories, subCategories
  except Exception as e:
    print("An error occurred while retrieving the initial page: ", e)
    return []

def scrape_links_from_id_list(data):
  data = []
  seen_ids = set(item[id] for item in data)
  try:
    links = []
    for item in data:
      if item["id"] in seen_ids:
        continue

      link = f'/us/item/{item["id"]}'
      links.append(link)
    
    if len(links) > 0:
      link_counter = 0

      for link in links:
        link_counter += 1
        print(f"Scraping data from page {link_counter} of {len(links)}")
        full_url = 'https://bdocodex.com' + link
        response = requests.get(full_url)

        if response.status_code == 200:
          soup = BeautifulSoup(response.text, 'html.parser')

          td_elements = soup.find_all('td')

          for td in td_elements:
            text = td.get_text(strip=True)

            if 'Sell price:' in text:
                price = text.split('Sell price:')[1].split('Repair')[0].strip()

                if price == '-':
                    price = '0'

                print("Id: ", link.split('/')[3], "basePrice: ", price)
                data.append({"id": link.split('/')[3], "name": item["name"], "basePrice": price})
                break
  except Exception as e:
    print("An error occurred while retrieving the initial page: ", e)
    return []
  return data

def scrape_links_from_json_list(data):
  dataToStore = []
  
  driver = webdriver.Chrome()
  wait = WebDriverWait(driver, 5)

  driver.get('https://bdocodex.com')
  for dat in data:
    if "&#39;" in dat:
      dat = dat.replace("&#39;", "'")
    try:
      searchField = driver.find_element(By.ID, "searchfield")

      if searchField:
        searchField.send_keys(dat)
        searchField.submit()

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dt-title")))

        dt_items = driver.find_elements(By.CLASS_NAME, "dt-title")
        if dt_items:
          for dt_item in dt_items:
            try:
              a_item = dt_item.find_element(By.TAG_NAME, "a")
              if a_item.text == dat:
                a_item.click()
                break
              else:
                continue
            except NoSuchElementException:
              continue
            

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card-header")))

        card_header = driver.find_element(By.CLASS_NAME, "card-header")
        item_id = card_header.text.split("ID:")[1].split("\n")[0].strip()

        item_name = driver.find_element(By.ID, "item_name")

        smallerText = driver.find_element(By.CLASS_NAME, "smallertext")
        soup = BeautifulSoup(smallerText.get_attribute('innerHTML'), 'html.parser')
        sell_price = soup.text.split("Sell price: ")[1].split("\n")[0].split("Repair")[0].strip()
        if sell_price == '-':
          sell_price = '0'
        print(f"Item name: {item_name.text}, Item id: {item_id}, Sell price: {sell_price}")
        dataToStore.append({"id": item_id, "name": item_name.text, "basePrice": sell_price})
    except Exception as e:
      print("An error occurred while retrieving the initial page: ", e)