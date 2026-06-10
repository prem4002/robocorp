import requests
from robocorp import workitems
from robocorp.tasks import task

@task
def consume_traffic_data():
    """
    Inhuman In
    surance, Inc. Artificial Intelligence System robot.
    Consumes traffic data work items.
    """
    print("consume")
    process_traffic_data()

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
