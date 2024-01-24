# expiry_date_extractor
Gets expiry dates from the ocado receipts.

## How to use
Following version of python required Python 3.10.11

1. Open a terminal and make sure your in the root of this folder i.e. /EXPIRY_DATE_EXTRACTOR
2. Run `pip install -r requirements.txt` to install dependencies
3. Update the path_to_pdf variable in the main.py page on line 4, or remove the ocado receipt into the folder and make sure it's called "receipt"
4. Run using this command `python3 main.py`
5. This will output a txt file called expiry_dates.txt
6. This file can be used by the corresponding react native app found here: https://github.com/JoWilks25/food-expiry-tracking
