import requests
from robocorp.tasks import task
from RPA.HTTP import HTTP
from RPA.JSON import JSON
from RPA.Tables import Tables
from robocorp import workitems

http = HTTP()
json = JSON()
table = Tables()

TRAFFIC_JSON_FILE_PATH = "output/traffic.json"  # to maintain duplicates

# JSON data keys
COUNTRY_KEY = "SpatialDim"
YEAR_KEY = "TimeDim"
RATE_KEY = "NumericValue"
GENDER_KEY = "Dim1"

@task
def produce_traffic_data():
    """
    Inhuman Insurance, Inc. Artificial Intelligence System automation.
    Produces traffic data work items.
    """
    http.download(
        url="https://github.com/robocorp/inhuman-insurance-inc/raw/main/RS_198.json",
        target_file=TRAFFIC_JSON_FILE_PATH,
        overwrite=True,
    )
    traffic_data = load_traffic_data_as_table()
    filtered_data = filter_and_sort_traffic_data(traffic_data)
    filtered_data = get_latest_data_by_country(filtered_data)
    payloads = create_work_item_payloads(filtered_data)
    save_work_item_payloads(payloads)

@task
def consume_traffic_data():
    """
    Inhuman Insurance, Inc. Artificial Intelligence System robot.
    Consumes traffic data work items.
    """
    print("consume")
    process_traffic_data()

# ALL PRODUCE TASKS
def load_traffic_data_as_table():
    json_data = json.load_json_from_file(TRAFFIC_JSON_FILE_PATH)
    return table.create_table(json_data["value"])

def filter_and_sort_traffic_data(data):
    max_rate = 5.0
    both_genders = "BTSX"
    table.filter_table_by_column(data, RATE_KEY, "<", max_rate)
    table.filter_table_by_column(data, GENDER_KEY, "==", both_genders)
    table.sort_table_by_column(data, YEAR_KEY, False)
    return data

def get_latest_data_by_country(data):
    data = table.group_table_by_column(data, COUNTRY_KEY)
    latest_data_by_country = []
    for group in data:
        first_row = table.pop_table_row(group)
        latest_data_by_country.append(first_row)
    return latest_data_by_country

def create_work_item_payloads(traffic_data):
    """
    - The `create_work_item_payloads()` function loops the list of traffic data - essentially rows.
    - For each row, you create a new dictionary (a data structure that supports named keys).
    - You append the dictionaries to a list that you then return from the keyword.
    """
    payloads = []  # here payload is the information that needs to be sent
    for row in traffic_data:
        payload = dict(
            country=row[COUNTRY_KEY],
            year=row[YEAR_KEY],
            rate=row[RATE_KEY],
        )
        payloads.append(payload)
    return payloads

def save_work_item_payloads(payloads):
    """
    The robocorp.workitems library provides a useful function for our current need:
    create() creates a new output work item. We store our payload as a dictionary with the given variable name (traffic_data).
    """
    for payload in payloads:
        variables = dict(traffic_data=payload)
        workitems.outputs.create(variables)

# ALL CONSUME TASKS
def process_traffic_data():
    for item in workitems.inputs:
        traffic_data = item.payload["traffic_data"] # data should be proper format that is usable by an API or for other reasons
        if validate_traffic_data(traffic_data):
            status, return_json = post_traffic_data_to_sales_system(traffic_data)
            if status == 200:
                item.done()
            else: # this is to handle failed tries
                item.fail(
                    exception_type="APPLICATION",
                    code="TRAFFIC_DATA_POST_FAILED",
                    message=return_json["message"]
                )
        else:
            item.fail(
                exception_type="BUSINESS",
                code="INVALID_TRAFFIC_DATA",
                message=item.payload,
            )

def validate_traffic_data(traffic_data):
    # this is important in real-time use cases where human made errors are possible
    return len(traffic_data["country"]) == 3

def post_traffic_data_to_sales_system(traffic_data):
    url = "https://robocorp.com/inhuman-insurance-inc/sales-system-api"
    response = requests.post(url, json=traffic_data)
    # response.raise_for_status() # for debugging purposes, to check if the information has been properly recieved or not
    return response.status_code, response.json()