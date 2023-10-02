import json

def save_into_file(filename, data, mainCategories, subCategories):
  structured_data = {}

  # Iterate through the main categories
  for idx, main_category_data in enumerate(data):
    main_category_name = mainCategories[idx]
    main_category = {}

    # Iterate through the subcategories in the main category
    for sub_category in main_category_data["subCategoriesData"]:
        print(sub_category["subcategoryName"])
        sub_category_name = sub_category["subcategoryName"]
        sub_category_items = sub_category["DropItems"]
        sub_category_dict = {}   

        # Add each item to the subcategory dictionary
        for item in sub_category_items:
          try:
            item_id = item["id"]
            item_name = item["name"]
            sub_category_dict[item_id] = item_name.strip()
          except ValueError:
            print("Value Error, ", item)
            continue

        # Add the subcategory dictionary to the main category
        main_category[sub_category_name] = sub_category_dict

    # Add the main category to the structured data
    structured_data[main_category_name] = main_category
  
  with open(filename, "w") as json_file:
        json.dump(structured_data, json_file, indent=4)