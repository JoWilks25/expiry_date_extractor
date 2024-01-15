from datetime import datetime, timedelta
from PyPDF2 import PdfReader

path_to_pdf = "receipt.pdf"
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def generate_item_date_dict(section_text):
  # Remove the "Section Title" from the list
  split_section_text = section_text.strip().split("\n")[1:]
  expiry_items = {}
  current_day = None
  merge_with_next_line = False
  for line_text in split_section_text:
    if "Use by end of" in line_text:
      current_day = line_text.split(" ")[-1]
      expiry_items[current_day] = []
    elif "Products with a 'use-by' date over one week" in line_text:
      current_day = "Over one week"
      expiry_items[current_day] = []
    elif "Products with no 'use-by' date" in line_text:
      current_day = "No use-by date"
      expiry_items[current_day] = []
    elif line_text in days_of_week:
      current_day = line_text
      expiry_items[current_day] = []
    elif merge_with_next_line is True:
      if len(expiry_items[current_day]) > 0:
        expiry_items[current_day][-1] += " " + line_text
      merge_with_next_line = False
    else:
      # Assume line should end in price or *, otherwise merge with next line
      if line_text[-1].isnumeric() is False and line_text[-1] != "*":
        merge_with_next_line = True
      expiry_items[current_day].append(line_text)
  return expiry_items

def next_weekday(date, weekday):
  days_ahead = weekday - date.weekday()
  if days_ahead <= 0: # Target day already happened this week
    days_ahead += 7
  return date + timedelta(days_ahead)

def main():
  # Open Ocado pdf receipt file * get all text
  reader = PdfReader(path_to_pdf)
  number_of_pages = len(reader.pages)
  all_text = ""
  for i in range(number_of_pages):
    page = reader.pages[i]
    all_text += page.extract_text()
  # print(all_text)

  # Extract relevant text from pdf
  # Following sections are possible, may not all be visible
  # 1. Fridge
  # 2. Cupboard
  # 3. Freezer
  # 4. Age-restricted products (assume no expiry date)
  # 5. Substituted items
  # 6. Offer savings (Assume should always exist)
  fridge_index_start= all_text.find("Fridge")
  cupboard_index_start = all_text.find("Cupboard")
  freezer_index_start = all_text.find("Freezer")
  age_restrict_index_start = all_text.find("Age-restricted products")
  substituted_items_start = all_text.find("Substituted items")
  offer_savings_index_start = all_text.find("Offers savings", fridge_index_start) # Start at Fridge text so don't get offer savings from grey box

  # TODO - Replace the bazillion if else statements
  # If not found index = -1
  fridge_index_end = None
  if fridge_index_start == -1:
    print("Fridge section not found")
  elif cupboard_index_start != -1:
    fridge_index_end = cupboard_index_start
  elif freezer_index_start != -1:
    fridge_index_end = freezer_index_start
  elif age_restrict_index_start != -1:
    fridge_index_end = age_restrict_index_start
  elif substituted_items_start != -1:
    fridge_index_end = substituted_items_start
  elif offer_savings_index_start != -1:
    fridge_index_end = offer_savings_index_start

  cupboard_index_end = None
  if cupboard_index_start == -1:
    print("Cupboard section not found")
  elif freezer_index_start != -1:
    cupboard_index_end = freezer_index_start
  elif age_restrict_index_start != -1:
    cupboard_index_end = age_restrict_index_start
  elif substituted_items_start != -1:
    fridge_index_end = substituted_items_start
  elif offer_savings_index_start != -1:
    cupboard_index_end = offer_savings_index_start

  freezer_index_end = None
  if freezer_index_start == -1:
    print("Freezer section not found")
  elif age_restrict_index_start != -1:
    freezer_index_end = age_restrict_index_start
  elif substituted_items_start != -1:
    freezer_index_end = substituted_items_start
  elif offer_savings_index_start != -1:
    freezer_index_end = offer_savings_index_start

  age_restrict_index_end = None
  if age_restrict_index_start == -1:
    print("Age Restricted section not found")
  elif substituted_items_start != -1:
    age_restrict_index_end = substituted_items_start
  elif offer_savings_index_start != -1:
    age_restrict_index_end = offer_savings_index_start

  substituted_items_end = None
  if substituted_items_start == -1:
    print("Substituted items section not found")
  elif offer_savings_index_start != -1:
    substituted_items_end = offer_savings_index_start

  # Extract text from each section
  fridge_text = all_text[fridge_index_start:fridge_index_end]
  cupboard_text = all_text[cupboard_index_start:cupboard_index_end]
  freezer_text = all_text[freezer_index_start:freezer_index_end]
  substituted_text = all_text[substituted_items_start:substituted_items_end]

  # Get each specific item under each section
  fridge_dict = generate_item_date_dict(fridge_text)
  cupboard_dict = generate_item_date_dict(cupboard_text)
  freezer_dict = generate_item_date_dict(freezer_text)
  substituted_dict = generate_item_date_dict(substituted_text)

  # Merge all Dicts
  all_items_dict = {}
  for key in fridge_dict.keys():
    if key in all_items_dict:
      all_items_dict[key].extend(fridge_dict[key])
    else:
      all_items_dict[key] = fridge_dict[key]

  for key in cupboard_dict.keys():
    if key in all_items_dict:
      all_items_dict[key].extend(cupboard_dict[key])
    else:
      all_items_dict[key] = cupboard_dict[key]

  for key in freezer_dict.keys():
    if key in all_items_dict:
      all_items_dict[key].extend(freezer_dict[key])
    else:
      all_items_dict[key] = freezer_dict[key]
  
  for key in substituted_dict.keys():
    if key in all_items_dict:
      all_items_dict[key].extend(substituted_dict[key])
    else:
      all_items_dict[key] = substituted_dict[key]

  print(all_items_dict)

  # Determine delivery date
  delivery_date_start = all_text.find("Delivery date:") + 14
  delivery_date_end = all_text.find("Contact us:")
  delivery_date_string = all_text[delivery_date_start:delivery_date_end].strip()
  delivery_date = datetime.strptime(delivery_date_string.split(" ")[1], "%d/%m/%Y")
  print("Delivery date:\n", delivery_date)

  # Update expiry Keys based on delivery date
  final_items_date_dict = {}
  for key in all_items_dict.keys():
    date = None
    if key == "Over one week":
      date = (delivery_date + timedelta(days=7)).strftime("%d/%m/%Y")
    # Exclude items with no use-by date
    # elif key == "No use-by date":
    #   date = (delivery_date + timedelta(days=30)).strftime("%d/%m/%Y")
    elif key in days_of_week:
        date = (next_weekday(delivery_date, days_of_week.index(key))).strftime("%d/%m/%Y")
    
    if date is not None:
      final_items_date_dict[date] = all_items_dict[key]
  
  print(final_items_date_dict)

  # Convert to Text format ExpiryDate,itemName,units
  event_rows = []
  for dateString, itemList in final_items_date_dict.items():
    for item in itemList:
      split_name = item.split('/')
      print("split_name", split_name)
      itemName = ''
      units = ''
      # for item with multiple units i.e. 
      # 'ARLA LACTOFREE SEMI SKIMMED MILK DRINK 2l (£3.00/EACH)2/26.00' = ['ARLA LACTOFREE SEMI SKIMMED MILK DRINK 2l (£3.00', 'EACH)2', '26.00']
      if len(split_name) > 2:
        itemName = split_name[0]
        units = split_name[1][-1]
      else:
        # "JACKSON'S SUPER SEEDED BROWN BLOOMER 800g1/12.00" = ["JACKSON'S SUPER SEEDED BROWN BLOOMER 800g1", '12.00']
        itemName = split_name[0][0:-1]
        units = split_name[0][-1]
      event_rows.append([dateString, f"{itemName}", f"{units}"]) #TODO - strip out units

  # Write to CSV file
  with open("expiry_dates.txt", "w") as f:
    for row in event_rows:
      f.write(",".join(row) + "\n")
  
  return final_items_date_dict

if __name__ == "__main__":
  main()
