class CategoryManager: 
  def __init__(self):
    self.categories = {}
  
  def add_id(self, main_category, sub_category, item_id):
    if main_category not in self.categories:
      self.categories[main_category] = {}
    if sub_category not in self.categories[main_category]:
      self.categories[main_category][sub_category] = set()
    self.categories[main_category][sub_category].add(item_id)
  
  def get_categories(self):
    return self.categories