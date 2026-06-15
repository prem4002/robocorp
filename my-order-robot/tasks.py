# import necessary libraries for the task
from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
#to create ZIP files
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_the_store()
    close_pop_up()
    orders = get_orders()

    for order in orders:
        fill_the_form(order)
        submit_the_order()
        pdf_path = store_receipt_as_pdf(order["Order number"])
        screenshot_path = screenshot_robot(order["Order number"])
        embed_screenshot_to_pdf(screenshot_path, pdf_path)
        go_to_next_order()

    archive_receipts()

def open_the_store():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

    table = Tables()
    orders = table.read_table_from_csv("orders.csv", header=True)

    return orders

def close_pop_up():
    page = browser.page()
    page.click("button:text('I guess so...')")

def fill_the_form(order):
    page = browser.page()

    page.select_option("#head", str(order["Head"])) #dropdown
    page.click(f"#id-body-{order['Body']}") #radio
    page.fill("input[placeholder='Enter the part number for the legs']", str(order["Legs"])) #id changing textbox
    page.fill("#address", str(order["Address"])) #textbox
    page.click("text=Preview")

def submit_the_order():
    page = browser.page()
    while True:                            # keep looping
        page.click("button:text('Order')")       # try to submit
        error = page.query_selector(".alert-danger") # check if error message appeared
        if not error:                 # if NO error...
            break        # exit

def go_to_next_order():
    page = browser.page()
    page.click("button:text('Order another robot')")
    close_pop_up()

def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    #to store it as pdf
    pdf = PDF()
    pdf_path = f"output/receipts/{order_number}.pdf"
    pdf.html_to_pdf(receipt_html, pdf_path)
    return pdf_path

def screenshot_robot(order_number):
    """Take a screenshot of the page"""
    page = browser.page()
    screenshot_path = f"output/receipts/{order_number}.png"
    page.locator("#robot-preview-image").screenshot(path=screenshot_path) #multi keyword to locate the image and screen shot it specifically
    return screenshot_path

def embed_screenshot_to_pdf(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf(
        files=[screenshot],
        target_document=pdf_file,
        append = True # apparently this parameter is required
    )

def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip(
        "output/receipts", # the folder which needs to be zipped
        "output/receipts.zip" # the save name for the zip folder
    )