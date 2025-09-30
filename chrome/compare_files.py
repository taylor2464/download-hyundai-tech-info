import os
import re
import time
import shutil
import base64
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

def save_pdf_with_retry(driver, output_path, retries=2, wait_between=5):
    """
    Attempts to save a PDF via Page.printToPDF, retrying on timeout or failure.
    """
    for attempt in range(retries):
        try:
            pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {
                "printBackground": True,
                "landscape": False
            })
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(pdf_data['data']))
            return True  # Success
        except Exception as e:
            print(f"PDF save failed (attempt {attempt+1}): {e}")
            time.sleep(wait_between)  # Wait before retry
    return False  # All retries failed

username = ""
password = ""
download_dir = "../docs"

# --- Step 1: Login in normal (non-headless) Chrome session ---
chrome_opts = Options()
driver = webdriver.Chrome(options=chrome_opts)
driver.set_page_load_timeout(120)# Wait up to 2 minutes for page loads
driver.set_script_timeout(120) # Wait up to 2 minutes for scripts/CDP commands


driver.get("https://hyundaitechinfo.com/")
time.sleep(4)

driver.find_element(By.XPATH, '//*[@id="user_id"]').send_keys(username)
driver.find_element(By.XPATH, '//*[@id="user_pw"]').send_keys(password)
driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/div').click()
time.sleep(5)

# Navigate to the section
driver.get("https://hyundaitechinfo.com/viewer/default.aspx?menu_id=12&sel_topmenu=337&sel_submenu=12&group=REPL")
time.sleep(5)
Select(driver.find_element(By.XPATH, '//*[@id="modelid_select"]')).select_by_value("1234")
time.sleep(5)
Select(driver.find_element(By.XPATH, '//*[@id="year_select"]')).select_by_value("2020")
time.sleep(5)
driver.find_element(By.XPATH, '//*[@id="ID_1"]').click()
time.sleep(4)

# Get the list of print links
list_container = driver.find_element(By.XPATH, '//*[@id="S_1"]')
links = list_container.find_elements(By.XPATH, ".//a[contains(@onclick, 'onclick_toc_print')]")

# Build the set of expected filenames
expected_files = set()
for link in links:
    onclick_val = link.get_attribute("onclick")
    match_name = re.search(r"nodedesc=([^&']+)", onclick_val)
    if match_name:
        raw_name = unquote(match_name.group(1))
        safe_name = re.sub(r'[\\/*?:"<>|&]', "_", raw_name)
        expected_files.add(f"{safe_name}.pdf")

# Get the set of already downloaded files
downloaded_files = set(os.listdir(download_dir))

# Find missing ones
missing_files = expected_files - downloaded_files

print(f"Total expected: {len(expected_files)}")
print(f"Already downloaded: {len(downloaded_files)}")
print(f"Missing: {len(missing_files)}")
print("\nMissing filenames:")
for filename in sorted(missing_files):
    print(filename)