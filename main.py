from web_scraping import scrape_links_from_initial_page, scrape_links_from_initial_page
from data_processing import save_into_file
# Entry point for the script
if __name__ == "__main__":
    links, mainCategories, subCategories, subCategoriesCounts = scrape_links_from_initial_page()
    linksVerified = True
    for link in links:
      if link.startswith('/us/items/version'):
        print('/us/items/version link found!')
        linksVerified = False
    if linksVerified:
      test = scrape_links_from_initial_page(links, mainCategories, subCategories, subCategoriesCounts)
      save_into_file('test.json', test[0], test[1], test[2])
