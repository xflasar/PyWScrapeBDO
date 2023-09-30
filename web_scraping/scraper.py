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
          link_counter = 0
        else:
          if link_counter % subCategoriesCounts[mainCategoriesCounter] == 0:
            mainCategoriesCounter += 1
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
            item_title = soup.find_all('td', attrs={'class': 'dt-title dt-title-search'})
          except NoSuchElementException:
            print("No item ID or item title found.")
            break

          for item in item_id:
            subCategoriesD.append(item.text)
            print(f"Item ID: {item.text}")
          for item in item_title:
            print(f"Item Title: {item.text}")
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
      mainCategoriesD.append(subCategoriesD)
      
    
    driver.quit()

    endTime = time.time() - startTime
    print("Data: ", mainCategoriesD)
    print("Links retrieved: ", counterOk, okLinks)
    print("Links not retrieved: ", counterFail, failLinks)
    print("Total links: ", link_counter_total)
    print("Time elapsed: ", endTime)
  except Exception as e:
    print("An error occurred while retrieving the initial page: ", e)
    return []