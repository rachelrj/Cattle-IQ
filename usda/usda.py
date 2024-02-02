import clickhouse_connect
import subprocess
import json
import boto3
from botocore.exceptions import ClientError
import certifi
import os
import time
import hashlib
import datetime
from datetime import datetime

def send_clickhouse(date_start, date_end):
        

    # Set the SSL_CERT_FILE environment variable to the path of the certifi bundle
    os.environ['SSL_CERT_FILE'] = certifi.where()

    secret_name = "clickhouse"
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
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = json.loads(get_secret_value_response['SecretString'])
    host = secret['host']
    port = secret['port']
    username = secret['username']
    password = secret['password']
    secure = False

    client = clickhouse_connect.get_client(host=host, port=port, username=username, password=password, connect_timeout=30, secure=True)

    def count_active_queries():
        active_queries = client.query("SELECT * FROM system.processes")

        rows = active_queries.result_rows
        number_of_rows = len(rows)
        print("Number of rows:", number_of_rows)

        return number_of_rows

    def wait_for_available_slots(max_active_queries):
        while count_active_queries() >= max_active_queries:
            print("Waiting for available query slots...")
            time.sleep(5)

    def execute_curl_command(curl_cmd):
        process = subprocess.Popen(curl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(f'Error executing curl: {stderr.decode()}')
            return None
        return json.loads(stdout.decode())

    def identify_data_key(report_data):
        for key, value in report_data.items():
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                return key
        return None

    def get_weight_range(avg_weight):

        if isinstance(avg_weight, (int, float, complex)) and not isinstance(avg_weight, bool):
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
        return None

    api_token = 'D40LZK0SpaO29GNPSMfscpLr7UYai4Dd'
    slug_ids = [ 1234, 1235, 1236, 1237, 1245, 1248, 1249, 1254, 1255, 1280, 1281, 1290, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1510, 1512, 1607, 1608, 1609, 1622, 1651, 1684, 1703, 1704, 1772, 1773, 1774, 1775, 1776, 1777, 1778, 1779, 1781,1782, 1783, 1784, 1785, 1786, 1788, 1789, 1790, 1791, 1792, 1793, 1794, 1795, 1796, 1797, 1798, 1799, 1800, 1801, 1802, 1803, 1804, 1805, 1806, 1807, 1808, 1809, 1810, 1811, 1812, 1813, 1814, 1815, 1816, 1817, 1818, 1819, 1820, 1821, 1822, 1823, 1824, 1825, 1826, 1827, 1828, 1829, 1830, 1831, 1832, 1833, 1834, 1835, 1836, 1837, 1838, 1839, 1840, 1841, 1842, 1843, 1844, 1845, 1847, 1848, 1849, 1850, 1851, 1852, 1853, 1854, 1855, 1856, 1857, 1858, 1859, 1860, 1861, 1863, 1864, 1865, 1866, 1867, 1868, 1869, 1870, 1871, 1872, 1873, 1874, 1876, 1877, 1878, 1879, 1880, 1882, 1883, 1884, 1886, 1887, 1888, 1889, 1890, 1891, 1892, 1893, 1894, 1895, 1896, 1897, 1898, 1899, 1900, 1901, 1902, 1903,
    3059, 3087, 3090, 3096, 3097, 3098, 3102, 3103, 3104, 3161, 3162, 3184, 3237, 3241, 3242, 3338, 3339, 3340, 3365, 3368, 3369, 3370, 3371, 3407, 3410, 3411, 3412, 3414, 3415, 3416, 3417, 3418, 3429, 3453, 3455, 3456, 3459, 3460, 3465, 3467, 3468, 3470, 3473, 3474, 3475, 3476, 3477, 3479, 3483, 3484, 3485, 3486, 3488, 3490, 3491, 3508, 3509, 3615, 3619, 3620, 3622, 3624, 3626, 3627, 3628, 3629, 3631, 3632, 3633, 3634, 3635, 3645, 3646, 3647, 3648, 3649, 3650, 3653, 3654, 3655, 3656, 3659, 3660, 3662, 3665, 3666, 3670, 3671, 3672, 3673, 3674, 3675, 3676, 3677, 3678, 3686, 3692, 1602, 1603, 1613, 1926, 2810, 3454, 3651]

    batch_size = 1000

    record_columns = [
    'report_date',
    'report_begin_date',
    'report_end_date',
    'published_date',
    'office_name',
    'office_state',
    'office_city',
    'office_code',
    'market_type',
    'market_type_category',
    'market_location_name',
    'market_location_state',
    'market_location_city',
    'slug_id',
    'slug_name',
    'report_title',
    'category',
    'commodity',
    'cattle_class',
    'frame',
    'muscle_grade',
    'quality_grade_name',
    'lot_desc',
    'freight',
    'price_unit',
    'age',
    'pregnancy_stage',
    'weight_collect',
    'offspring_weight_est',
    'dressing',
    'yield_grade',
    'head_count',
    'avg_weight_min',
    'avg_weight_max',
    'avg_weight',
    'avg_price_min',
    'avg_price_max',
    'avg_price',
    'weight_break_low',
    'weight_break_high',
    'receipts',
    'receipts_week_ago',
    'receipts_year_ago',
    'comments_commodity',
    'report_narrative',
    'final_ind',
    'market_id',
    'unique_hash',
    'weight_range',
    'insert_date'
    ]

    for slug_id in slug_ids:
        report_command = f'curl -u {api_token}: "https://marsapi.ams.usda.gov/services/v1.2/reports/{slug_id}?q=report_begin_date={date_start}:{date_end}"'
        report_data = execute_curl_command(report_command)

        if report_data and isinstance(report_data, dict):
            data_key = identify_data_key(report_data)
            if data_key:
                records_to_insert = []
                for record in report_data[data_key]:
                    if record.get('category', '').lower() == 'cattle':
                        record["market_id"] = slug_id
                        record['report_date'] = datetime.strptime(record['report_date'], '%m/%d/%Y')
                        record['report_begin_date'] = datetime.strptime(record['report_begin_date'], '%m/%d/%Y')
                        record['report_end_date'] = datetime.strptime(record['report_end_date'], '%m/%d/%Y')
                        record['published_date'] = datetime.strptime(record['published_date'], '%m/%d/%Y %H:%M:%S')
                        record['market_location_state'] = record['market_location_state'] if record['market_location_state'] else ""
                        unique_string = f"{record['market_id']}{record['report_date']}{record['head_count']}{record['avg_price']}{record['avg_weight']}"
                        hash_object = hashlib.md5(unique_string.encode())
                        md5_hash = hash_object.hexdigest()
                        record["unique_hash"] = md5_hash
                        del record["group"]
                        weight_range = get_weight_range(record['avg_weight'])
                        if (weight_range):
                            record['weight_range'] = weight_range
                            record['insert_date'] = datetime.now()
                            records_to_insert.append(record)
                            print(record)
                            if len(records_to_insert) == batch_size:
                                wait_for_available_slots(100)
                                array_of_arrays = [list(record.values()) for record in records_to_insert]
                                response = client.insert('transactions', array_of_arrays, column_names=record_columns)
                                print(response)
                                records_to_insert.clear()
                if records_to_insert:
                    wait_for_available_slots(100)
                    array_of_arrays = [list(record.values()) for record in records_to_insert]
                    response = client.insert('transactions', array_of_arrays, column_names=record_columns)
                    print(response)
                    records_to_insert.clear()
        print()
        print(f"Done with slug: {slug_id}")
        print()