from decimal import Decimal
import boto3
from botocore.exceptions import ClientError
import re
from .error_email import send_error_email
import datetime
from datetime import datetime, date
import hashlib

def convert_floats_to_decimals(item):
    for key, value in item.items():
        if isinstance(value, float):
            item[key] = Decimal(str(value))
        elif isinstance(value, dict):
            item[key] = convert_floats_to_decimals(value)
    return item

def get_weight_range(avg_weight):

    if not isinstance(avg_weight, (int, float, complex)):
        try:
            avg_weight = int(avg_weight)
        except:
            print(f"COULD NOT convert weight: {avg_weight} into weight range")

    if (avg_weight < 200):
        return "<200"
    elif (avg_weight <= 300):
        return "201-300"
    elif (avg_weight <= 400):
        return "301-400"
    elif (avg_weight <= 500):
        return "401-500"
    elif (avg_weight <= 600):
        return "501-600"
    elif (avg_weight <= 700):
        return "601-700"
    elif (avg_weight <= 800):
        return "701-800"
    elif (avg_weight <= 900):
        return "801-900"
    elif (avg_weight <= 1000):
        return "901-1000"
    elif (avg_weight <= 1100):
        return "1001-1100"
    elif (avg_weight <= 1200):
        return "1101-1200"
    elif (avg_weight <= 1300):
        return "1201-1300"
    elif (avg_weight <= 1400):
        return "1301-1400"
    elif (avg_weight <= 1500):
        return "1401-1500"
    elif (avg_weight <= 1600):
        return "1501-1600"
    elif (avg_weight <= 1700):
        return "1601-1700"
    elif (avg_weight <= 1800):
        return "1701-1800"
    elif (avg_weight <= 1900):
        return "1801-1900"
    elif (avg_weight <= 2000):
        return "1901-2000"
    elif (avg_weight <= 2100):
        return "2001-2100"
    elif (avg_weight <= 2200):
        return "2101-2200"
    elif (avg_weight <= 2300):
        return "2201-2300"
    elif (avg_weight <= 2400):
        return "2301-2400"
    elif (avg_weight <= 2500):
        return "2401-2500"
    else:
        return ">2500"

def convert_class(claz):
    claz_upper = claz.upper()
    exact_mappings = {
        'BULL': 'Bulls', 
		'BULL CF': 'Bulls', 
		'COW': 'Cows', 
		'HFR': 'Heifers', 
		'HFR CF': 'Heifers', 
		'HFRETTE': 'Cows', 
		'STR': 'Steers', 
		'STR CF': 'Steers', 
		'STOCK COW': 'Stock Cows', 
		'PAIR': 'Cow-Calf Pairs', 
		'BUTCHER': 'Cows', 
		'STOCK C': 'Stock Cows', 
		'BULCF': 'Bulls', 
		'PR': 'Cow-Calf Pairs', 
		'BCF': 'Bulls', 
		'BRED HFR': 'Bred Heifers', 
		'CALF': 'Cows', 
		'HFRT': 'Cows', 
		'B COW': 'Bred Cows', 
		'B HFR': 'Bred Heifers', 
		'FAMILY': 'Cows', 
		'BCOW': 'Bred Cows', 
		'BCOW SOLID': 'Bred Cows', 
		'BCOW OLD': 'Bred Cows', 
		'BCOW 3-4-APR': 'Bred Cows', 
		'BCOW 3-4': 'Bred Cows', 
		'BHFR': 'Bred Heifers', 
		'STCF': 'Steers', 
		'BHFR-MAR': 'Bred Heifers', 
		'HFRCF': 'Heifers', 
		'BCOW 5-6': 'Bred Cows', 
		'BCOW 5-6-MAR': 'Bred Cows', 
		'PR2-3YR': 'Cow-Calf Pairs', 
		'BCOW 3-6': 'Bred Cows', 
		'BCOW 4-5YR': 'Bred Cows', 
		'BCOW 5-6-APR': 'Bred Cows', 
		'BHFR-FEB': 'Bred Heifers', 
		'BCOW 5-8YR': 'Bred Cows', 
		'BCOW5-8YR': 'Bred Cows', 
		'REPLHFR': 'Heifers', 
		'REPL-HFR': 'Heifers', 
		'BCOW 3': 'Bred Cows', 
		'PR_2-3': 'Cow-Calf Pairs', 
		'BCOW 3-4-MAR': 'Bred Cows', 
		'PR_2yr': 'Cow-Calf Pairs', 
		'PR-OLD': 'Cow-Calf Pairs', 
		'PR-RUNAGE': 'Cow-Calf Pairs', 
		'PR4-7Y': 'Cow-Calf Pairs', 
		'PR-MIDAGE': 'Cow-Calf Pairs', 
		'BHFR-FEBAI': 'Bred Heifers', 
		'BHFR-MAR-APR': 'Bred Heifers', 
		'PR_3-5': 'Cow-Calf Pairs', 
		'PR RUNAGE': 'Cow-Calf Pairs', 
		'PR_3-4': 'Cow-Calf Pairs', 
		'PR_OLD': 'Cow-Calf Pairs', 
		'PR_MxAge': 'Cow-Calf Pairs', 
		'PR3-5YR': 'Cow-Calf Pairs', 
		'PR_6-9': 'Cow-Calf Pairs', 
		'HFRTT': 'Heifers', 
		'BCOW SOLID-APR': 'Bred Cows', 
		'PR_6+': 'Cow-Calf Pairs', 
		'3Y BLK-PR': 'Cow-Calf Pairs', 
		'PR-YOUNG': 'Cow-Calf Pairs', 
		'SOLID-JUN': 'Cows', 
		'BULLCF': 'Bulls', 
		'PR OLD': 'Cow-Calf Pairs', 
		'PR3-5Y': 'Cow-Calf Pairs', 
		'BHFR-APR': 'Heifers', 
		'BV HFR': 'Heifers', 
		'BCOW 3-4YR': 'Bred Cows', 
		'PR-RUNNING AGE': 'Cow-Calf Pairs', 
		'SHTHRN-HFR': 'Heifers', 
		'BHFR-JULY': 'Bred Heifers', 
		'PR 3-5': 'Cow-Calf Pairs', 
		'YRLG BULL': 'Bulls', 
		'PR_RunAge': 'Cow-Calf Pairs', 
		'3y RED-PR': 'Cow-Calf Pairs', 
		'PR 5-6': 'Cow-Calf Pairs', 
		'PR4-6': 'Cow-Calf Pairs', 
		'COW-EXPSD': 'Cows', 
		'BREDHFR': 'Bred Heifers', 
		'PR2YO': 'Cow-Calf Pairs', 
		'PR-RUNNG AGE': 'Cow-Calf Pairs', 
		'PR_YNG': 'Cow-Calf Pairs', 
		'BCOW BRKN': 'Bred Cows', 
		'PR-MDAG': 'Cow-Calf Pairs', 
		'PR-YNG': 'Cow-Calf Pairs', 
		'PR7-9': 'Cow-Calf Pairs', 
		'BHFR-MAY': 'Bred Heifers', 
		'PR YOUNG': 'Cow-Calf Pairs', 
		'PR-RUNNINGAGE': 'Cow-Calf Pairs', 
		'PR_5-6': 'Cow-Calf Pairs', 
		'PR-BLEMISH': 'Cow-Calf Pairs', 
		'APR': 'Cows', 
		'REG BULL': 'Bulls', 
		'PR_THIN': 'Cow-Calf Pairs', 
		'PR8-9Y': 'Cow-Calf Pairs', 
		'PR_10+': 'Cow-Calf Pairs', 
		'PR-2-3YR': 'Cow-Calf Pairs', 
		'BCOW 3-4 MAY': 'Bred Cows', 
		'PR8-11Y': 'Cow-Calf Pairs', 
		'BRKN-JUN': 'Cow-Calf Pairs', 
		'PR-HFR': 'Heifer Pairs', 
		'BCOW-SOLID': 'Bred Cows', 
		'BHFR-SHTEARS': 'Bred Heifers', 
		'BCOW BKN': 'Bred Cows', 
		'PR MX AGE': 'Cow-Calf Pairs', 
		'PR-OLDER': 'Cow-Calf Pairs', 
		'PR_7-8': 'Cow-Calf Pairs', 
		'PRCRIPPLED': 'Cow-Calf Pairs', 
		'SMOOTH-JUN': 'Cows', 
		'BCOW 3-4 THIN': 'Bred Cows', 
		'BCOW 3-4-JN': 'Bred Cows', 
		'HFRCF-XBRD': 'Heifers', 
		'PR OLDER': 'Cow-Calf Pairs', 
		'STCF-XBRED': 'Steers', 
		'PR-HORNS': 'Cow-Calf Pairs', 
		'STCF-FALL': 'Steers', 
		'HFR-PR': 'Heifer Pairs', 
		'PR 3-4': 'Cow-Calf Pairs', 
		'PR_OLD-NR': 'Cow-Calf Pairs', 
		'BHFR-LATE': 'Bred Heifers', 
		'BCOW-APR': 'Bred Cows', 
		'SOLID': 'Cows', 
		'BCOW-JUN': 'Bred Cows', 
		'HFRCF-FALL': 'Heifers', 
		'S.T.-MAY': 'Steers', 
		'PR_4': 'Cow-Calf Pairs', 
		'BBYCF': 'Cows', 
		'BCOW THIN': 'Bred Cows', 
		'PR-OLDER COW': 'Cow-Calf Pairs', 
		'PR LAME 5-6': 'Cow-Calf Pairs', 
		'PR-CRIPLD': 'Cow-Calf Pairs', 
		'BCOW-MAY': 'Bred Cows', 
		'PR 4YR': 'Cow-Calf Pairs', 
		'PR HIP': 'Cow-Calf Pairs', 
		'BRED-PR': 'Cow-Calf Pairs', 
		'PR_3-4NR': 'Cow-Calf Pairs', 
		'PR4-8': 'Cow-Calf Pairs', 
		'BREDCOW': 'Bred Cows', 
		'BHFR-DECMBR': 'Bred Heifers', 
		'BHFR-NOVMBR': 'Bred Heifers', 
		'HFR-EARS': 'Heifers', 
		'PROLD': 'Cow-Calf Pairs', 
		'BCOW SOL': 'Bred Cows', 
		'YRLBULL': 'Bulls', 
		'PRLAME': 'Cow-Calf Pairs', 
		'YRL-EWE': 'Cow-Calf Pairs', 
		'STCF-EARS': 'Steers', 
		'YRLG U': 'Cows', 
		'BBYCF-SHRTEARS': 'Cows', 
		'BBYCF-LHRN': 'Cows', 
		'BRCW 3 & 4 YR OLDS': 'Bred Cows', 
		'BRCW 5 & 6 YR OLDS': 'Bred Cows', 
		'BRCW 6 YR OLDS': 'Bred Cows', 
		'BRCW 6 & 7 YR OLDS': 'Bred Cows', 
		'BRCW SOLID MOUTH': 'Bred Cows', 
		'BRCW SHORT-TERM': 'Bred Cows', 
		'STRCF': 'Steers', 
		'HFT': 'Cows', 
		'BULL CALVES': 'Bulls', 
		'BRCW 4 YR OLDS': 'Bred Cows', 
		'BRCW SHORT TERM': 'Bred Cows', 
		'BRCW': 'Bred Cows', 
		'PAIR 2 YR OLDS': 'Cow-Calf Pairs', 
		'PAIR 3-4 YR OLDS': 'Cow-Calf Pairs', 
		'PAIR SOLID MOUTH': 'Cow-Calf Pairs', 
		'PAIR SHORT-TERM': 'Cow-Calf Pairs', 
		'PAIR 3 & 4 YR OLDS': 'Cow-Calf Pairs', 
		'PAIR 5 & 6 YR OLDS': 'Cow-Calf Pairs', 
		'PAIR 7 YR OLDS': 'Cow-Calf Pairs', 
		'PAIR 8-9 YR OLDS': 'Cow-Calf Pairs', 
		'BRCW 5 & 6 YR OLD': 'Bred Cows', 
		'BRCW 4 & 5 YR OLDS': 'Bred Cows', 
		'BRD COW': 'Bred Cows', 
		'BULL CLF': 'Bulls', 
		'BRD HFR': 'Bred Heifers', 
		'HFR CALF': 'Heifers', 
		'STR CLF': 'Steers', 
		'BABYCLF': 'Cows', 
		'HFR CLF': 'Heifers', 
		'SLBULL': 'Bulls', 
		'YRLG HFR': 'Heifers', 
		'YRLG STR': 'Steers', 
		'BRD CW3-4': 'Bred Cows', 
		'BRD CW5-7': 'Bred Cows', 
		'BRED SOLID': 'Bred Cows', 
		'ST/BROKEN': 'Steers', 
		'X-STR CLF': 'Steers' 
    }

    # Check for exact matches first
    if claz_upper in exact_mappings:
        return exact_mappings[claz_upper]

    simple_mappings = {
        'B COW': 'Bred Cows', 'BCOW': 'Bred Cows',
        'B HFR': 'Bred Heifers', 'BHFR': 'Bred Heifers',
        'PAIR': 'Cow-Calf Pairs', 'PR': 'Cow-Calf Pairs',
        'BULL': 'Bulls', 'BUL': 'Bulls',
        'ST': 'Steers', 'S.T.': 'Steers',
        'CALF': 'Cows', 'CF': 'Cows',
        'BUCK': 'Other', 'BILLY': 'Other', 'NANNY': 'Other', 
        'KID': 'Other', 'RAM': 'Other', 'WETHER': 'Other', 
        'MARE': 'Other', 'EWE': 'Other', 'STUD': 'Other', 
        'SHEEP': 'Other', 'GOAT': 'Other', 'MAY': 'Other',
        'JUNE': 'Other'
    }

    for key, value in simple_mappings.items():
        if key in claz_upper:
            if value == 'Other':
                return 
            else:
                return value

    if 'BRD' in claz_upper or 'BRED' in claz_upper:
        return 'Bred Heifers' if 'HFR' in claz_upper or 'HEIFER' in claz_upper else 'Bred Cows'

    if 'DAIRY' in claz_upper:
        if 'HFR' in claz_upper or 'HEIFER' in claz_upper:
            return 'Dairy Heifers'
        elif 'ST' in claz_upper:
            return 'Dairy Steers'

    if 'STOCK' in claz_upper and ('COW' in claz_upper or 'CW' in claz_upper):
        return 'Stock Cows'

    if ('COW' in claz_upper or 'CW' in claz_upper) and ('CALF' in claz_upper or 'CF' in claz_upper):
        return 'Cow-Calf Pairs'

    if 'COW' in claz_upper or 'CW' in claz_upper or 'HFRETTE' in claz_upper or 'HFRT' in claz_upper or 'HEIFERETTE' in claz_upper or 'BUTCHER' in claz_upper or 'FAMILY' in claz_upper or 'SOLID' in claz_upper:
        return 'Cows'

    if 'HFR' in claz_upper or 'HEIFER' or 'HFCLF' in claz_upper:
        return "Heifers"

    print(f"COULD NOT INTERPRET CLASS FOR {claz}")
    message = f"An error occurred transforming {claz} into a class."
    send_error_email(message)

    return

def convert_price_factor(pf):
    pf = pf.upper()

    if ('WT' in pf or 'C' in pf):
        return 'Per Cwt'
    if ('H' in pf or 'PR' in pf):
        return 'Per Head'
    if ('UNIT' in pf):
        return 'Per Unit'
    if('FAM' in pf):
        return 'Per Family'

    return

def remove_except_dots_and_numbers(s):
    return re.sub(r'[^0-9\.]+', '', s)

def extract_number(string):
    # Remove numbers after decimal point
    string = re.sub(r'\.\d+', '', string)
    # Extract numbers
    number_str = ''.join(re.findall(r'\d+', string))
    return int(number_str) if number_str else None

def convert_entry(date_input, city, state, market_location_name, market_type, claz, market_id, price_unit, head_count, avg_weight, avg_price, auction_name=None, report_title=None, commodity=None, age=None, breed=None, buyer=None, seller=None):
    avg_price = extract_number(avg_price)
    auction_name = auction_name or market_location_name
    if (not avg_price or avg_price == 0):
        print(f"Record not stored. Response: price is {avg_price} from {market_location_name}")
        return
    converted_class = convert_class(claz)
    if (not converted_class):
        if (breed):
            converted_class = convert_class(breed)
        if (not converted_class):
            print(f"Record not stored. Response: {claz} cannot be interpreted for {market_location_name}")
            return
    converted_average_weight = extract_number(avg_weight)
    if (not converted_average_weight or converted_average_weight == 0):
        print(f"Record not stored. Weight {avg_weight} does not exist")
        return  
    if (not date_input):
        print(f"Record not stored for clickhouse. Date does not exist")  
        return
    if (not market_id or market_id == 0):
        print(f"Record not stored for clickhouse. Market ID does not exist") 
        return 
    converted_price_unit = convert_price_factor(price_unit)
    if (not converted_price_unit):
        print(f"Record not stored for clickhouse. Price unit {price_unit} invalid")

    buyer_seller = ''
    if (buyer):
        buyer_seller = buyer
    elif (seller):
        buyer_seller = seller

    date_object = None
    if isinstance(date_input, (datetime, date)):
        date_object = date_input
    else:
        try:
            print("Attempting to convert date:", date_input)
            date_object = datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError as e:
            print("Failed to convert date into formatted date:", e)
            return None
        except Exception as e:
            print("An unexpected error occurred:", e)
            return None

    md5_hash = None

    try: 
        unique_string = f"{market_id}{buyer_seller}{date}{head_count}{avg_price}{avg_weight}"
        hash_object = hashlib.md5(unique_string.encode())
        md5_hash = hash_object.hexdigest()
    except:
        print("Failed to create unique hash")
        return        
    try: 
        return [
            date_object,
            market_location_name,
            state,
            city,
            None,
            "Auction Livestock",
            market_type,
            auction_name,
            state,
            city,
            None,
            None,
            report_title,
            'Cattle',
            commodity,
            converted_class,
            'F.O.B.',
            converted_price_unit,
            extract_number(age) if age else None,
            "Y" if (converted_class == 'Bred Heifers' or converted_class == 'Bred Cows') else None,
            head_count,
            converted_average_weight,
            avg_price,
            market_id,
            md5_hash,
            get_weight_range(converted_average_weight),
            datetime.now(),
            seller if seller else '',
            buyer if buyer else '',
            breed if breed else None
            ]
    except Exception as e:
        message = f"Failed to convert record: {market_location_name}, {date_input}: {e}"
        send_error_email(message)
        print(message)