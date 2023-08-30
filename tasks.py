"""Robocorp Course Level 2 Python."""
from robocorp.tasks import task
from robocorp import browser, http, log
from robocorp.excel.tables import Table, Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
from time import sleep
from pprint import pformat

@task
def order_robots_from_RobotSpareBin() -> None:
    """ Robocorp Level 2 Python Task.
    
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.

    """
    browser.configure(
        slowmo=100,
        headless=True,
    )
    open_robot_order_website()
    orders = get_orders()
    for row in orders:
        order_n = row["Order number"]
        log.console_message(f"*** {order_n} ***\n", "important")
        close_annoying_modal()
        fill_the_form(
            row["Head"],
            row["Body"],
            row["Legs"],
            row["Address"],
        )
        preview_robot()
        submit_order()
        check_error()
        receipt_pdf = store_receipt_as_pdf(order_n)
        robot_img = screenshot_robot(order_n)
        # receipt_img = screenshot_receipt(order_n)
        # embed_screenshot_to_receipt(receipt_img, receipt_pdf)
        embed_screenshot_to_receipt(robot_img, receipt_pdf)
        new_order()
        # break
    archive_receipts()

def open_robot_order_website() -> None:
    """Opens the website."""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders() -> Table:
    """Download the orders

    Returns:
        Table: Data from the csv.

    """
    path: str = http.download(
        url="https://robotsparebinindustries.com/orders.csv",
        overwrite=True
    )
    tables = Tables()
    orders = tables.read_table_from_csv(path, header=True)
    for i, x in enumerate(orders):
        print(x)
    return orders

def close_annoying_modal() -> None:
    """Close the prompt."""
    locator_ok_button = "//html/body/div/div/div[2]/div/div/div/div/div/button[1]"
    page = browser.page()
    page.click(locator_ok_button)

def fill_the_form(
    head_n: str, body_n: str,
    legs_n: str, address: str
) -> None:
    """Fill the page forms.

    Parameters
    ----------
    head_n : str
        Head number.

    body_n : str
        Body number.

    legs_n : str
        Legs number.

    address : str
        Addres value.

    """
    page = browser.page()
    locator_head = "//html/body/div/div/div[1]/div/div[1]/form/div[1]/select"
    locator_body = "input#id-body-"
    locator_legs = "//html/body/div/div/div[1]/div/div[1]/form/div[3]/input"
    locator_address = "input#address"

    page.select_option(locator_head, head_n)
    page.click(f"{locator_body}{body_n}")
    page.fill(locator_legs, legs_n)
    page.fill(locator_address, address)

def preview_robot() -> None:
    """Click on preview button."""
    page = browser.page()
    locator_preview = "button#preview"
    page.click(locator_preview)

def submit_order() -> None:
    """Submit the order."""
    page = browser.page()
    locator_order = "button#order"
    page.click(locator_order)

def check_error() -> None:
    """Check if there is an error while submiting the order."""
    page = browser.page()
    locator_error = "//html/body/div/div/div[1]/div/div[1]/div"

    while True:
        text = page.locator(locator_error).inner_text(timeout=2000)
        # log.console_message(f"{text = }\n", "important")
        if "Thank you for your order!" in text:
            break
        else:
            submit_order()

def new_order() -> None:
    """Click on new order."""
    page = browser.page()
    locator_another_order = "button#order-another"
    # locator_another_order = "//html/body/div/div/div[1]/div/div[1]/div/button"
    page.click(locator_another_order)

def store_receipt_as_pdf(order_n: str) -> str:
    """Save receipt as pdf.

    Parameters
    ----------
    order_n : str
        Order number.

    Returns
    -------
    str
        filepath to the pdf.

    """
    locator_receipt = "//html/body/div/div/div[1]/div/div[1]/div/div"
    page = browser.page()
    receipt_html = page.locator(locator_receipt).inner_html()

    pdf = PDF()
    filepath = f"output/receipts/receipt-{order_n}.pdf"
    pdf.html_to_pdf(receipt_html, filepath)
    return filepath

def screenshot_receipt(order_n: str) -> str:
    """Takes a screenshot of the receipt.

    I believe this function is a trick and they really want
    you to download is the robot image.

    Parameters
    ----------
    order_n : str
        Order number.

    Returns
    -------
    str
        Filepath of the image.

    """
    page = browser.page()
    locator_receipt = "//html/body/div/div/div[1]/div/div[1]/div/div"
    filepath = f"output/receipts/order-{order_n}.png"
    page.locator(locator_receipt).screenshot(path=filepath)
    return filepath

def screenshot_robot(order_n: str) -> str:
    """Takes a screenshot of the robot.


    Parameters
    ----------
    order_n : str
        Order number.

    Returns
    -------
    str
        Filepath of the image.

    """
    page = browser.page()
    locator_image = "div#robot-preview-image"

    filepath = f"output/photos/order-{order_n}.png"
    page.locator(locator_image).screenshot(path=filepath)
    return filepath

def embed_screenshot_to_receipt(screenshot: str, pdf_file: str) -> None:
    """Embed the robot to the pdf.

    Parameters
    ----------
    screenshot : str
        Path to the image of the robot.

    pdf_file : str
        Path to the pdf.

    """
    pdf = PDF()
    pdf.add_files_to_pdf([screenshot], pdf_file, True)

def archive_receipts() -> None:
    """Zip the generated files."""
    archive = Archive()
    archive.archive_folder_with_zip(
        "output/receipts",
        "output/pdfs_zip.zip",
        include="*.pdf"
    )
