import psycopg2
from psycopg2.extras import execute_values
import json
from datetime import datetime
import boto3
from .conversions import convert_floats_to_decimals, convert_class, remove_except_dots_and_numbers, extract_number
from .error_email import send_error_email

def get_secret():
    secret_name = "redshift!cattleiq-admin"
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        raise e

    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    else:
        raise Exception("Secret not found")

# TODO: CHANGE THIS TO BATCH QUERIES TO SAVE COSTS
def store_redshift(date, city, state, market_location_name, market_type, claz, market_id, price_unit, head_count, avg_weight, avg_price, auction_name=None, report_title=None, commodity=None, age=None, breed=None, buyer=None, seller=None):
    if (not avg_price or avg_price == 0):
        print(f"Record not stored. Response: price is {avg_price} from {market_location_name}")
        return
    converted_class = convert_class(claz)
    if (not converted_class):
        print(f"Record not stored. Response: {claz} cannot be interpreted for {market_location_name}")
        return

    try:
        date_object = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = date_object.strftime("%m-%d-%Y")
        pregnancy = converted_class == 'Bred Cows' or converted_class == 'Bred Heifers'
        record = {
            'report_date': formatted_date,
            'office_name': f"{city}, {state}",
            'office_state': state,
            'office_city': city,
            'market_type': 'Auction Livestock',
            'market_type_category': market_type,
            'buyer': buyer if buyer else None,
            'market_location_name': auction_name if auction_name else market_location_name,
            'market_location_state': state,
            'market_location_city': city,
            'commodity': commodity if commodity else None,
            'class': converted_class,
            'report_title': report_title if report_title else None,
            'price_unit': price_unit,
            'freight': 'F.O.B.',
            'market_id': market_id,
            'age': age if age else None,
            'seller': seller if seller else None,
            'head_count': head_count,
            'avg_weight': extract_number(avg_weight),
            'avg_price': convert_floats_to_decimals(remove_except_dots_and_numbers(avg_price)),
            'breed': breed if breed else None,
            'pregnancy_stage': 'Y' if pregnancy else None
        }

        secret = get_secret()
        username = secret['user']
        password = secret['password']

        conn = psycopg2.connect(dbname='dev', host='workgroup.113365400202.us-east-1.redshift-serverless.amazonaws.com', port='5439', user=username, password=password)
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO transactions (
            report_date, office_name, office_state, office_city, market_type, market_type_category, 
            buyer, market_location_name, market_location_state, market_location_city, commodity, class, 
            report_title, price_unit, freight, market_id, age, seller, head_count, avg_weight, avg_price, 
            breed, pregnancy_stage
        ) VALUES %s
        """

        execute_values(cursor, insert_query, [(record.values())])
        conn.commit()

        print("Record successfully stored in Redshift")

    except (Exception, psycopg2.Error) as e:
        message = f"Error while connecting to PostgreSQL: {e.response['Error']['Message']}"
        print(message)
        send_error_email(message)

    finally:
        if conn is not None:
            conn.close()