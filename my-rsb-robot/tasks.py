from robocorp.tasks import task
# import the browser library to access websites 
from robocorp import browser
# to download files from the site
from RPA.HTTP import HTTP
# to read excel files
from RPA.Excel.Files import Files
# to download information as a pdf file
from RPA.PDF import PDF

@task
def robot_spare_bin_python():
    """Insert the sales data for the week and export it as a PDF"""
    browser.configure(
        slowmo=0,
    )
    open_the_intranet_website()
    log_in()
    download_excel_file()
    fill_form_with_excel_data()
    collect_results()
    export_as_pdf()
    log_out()

# this function is to access the site
def open_the_intranet_website():
    # add the link here
    browser.goto("https://robotsparebinindustries.com/")

# this is to login to the webpage using the womans credentials
def log_in():
    """Fill in the login form and clicks the 'log in' button"""
    page = browser.page()
    page.fill("#username", "maria")
    page.fill("#password", "thoushallnotpass")
    page.click("button:text('Log In')")

def fill_and_submit_sales_form(sales_rep):
    """Fills in the sales data and click the 'Submit' button"""
    page = browser.page()

    page.fill("#firstname", sales_rep["First Name"])
    page.fill("#lastname", sales_rep["Last Name"])
    page.select_option("#salestarget", str(sales_rep["Sales Target"]))
    page.fill("#salesresult", str(sales_rep["Sales"]))
    page.click("text=Submit")

def download_excel_file():
    """Downloads the excel file from the given url"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/SalesData.xlsx", overwrite=True)

# to auto fill the information from the excel file
def fill_form_with_excel_data():
    """Read data from excel and fill in the sales form"""
    excel = Files()
    excel.open_workbook("SalesData.xlsx")
    worksheet = excel.read_worksheet_as_table("data", header=True)
    excel.close_workbook()

    for row in worksheet:
        fill_and_submit_sales_form(row)

#to get proof
def collect_results():
    """Take a screenshot of the page"""
    page = browser.page()
    page.screenshot(path="output/sales_summary.png")

def export_as_pdf():
    """Export the data to a pdf file"""
    page = browser.page()
    sales_results_html = page.locator("#sales-results").inner_html()

    pdf = PDF()
    pdf.html_to_pdf(sales_results_html, "output/sales_results.pdf")

def log_out():
    """Presses the 'Log out' button"""
    page = browser.page()  
    page.click("text=Log out")