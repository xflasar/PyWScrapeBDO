from web_scraping import scrape_links_from_initial_page, test_scrape_links_from_initial_page
from data_processing import CategoryManager
# Entry point for the script
if __name__ == "__main__":
    links, mainCategories, subCategories, subCategoriesCounts = scrape_links_from_initial_page()
    linksVerified = True
    for link in links:
      if link.startswith('/us/items/version'):
        print('/us/items/version link found!')
        linksVerified = False
    if linksVerified:
      cateManager = CategoryManager()
      test_scrape_links_from_initial_page(links, mainCategories, subCategories, subCategoriesCounts, cateManager)