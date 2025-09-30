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
chrome_opts.add_argument("--window-size=1800,1080")
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
driver.get("https://hyundaitechinfo.com/viewer/default.aspx?menu_id=13&sel_topmenu=337&sel_submenu=13&group=COMP")
time.sleep(5)
# Select(driver.find_element(By.XPATH, '//*[@id="modelid_select"]')).select_by_value("1234")
Select(driver.find_element(By.XPATH, '//*[@id="modelid_select"]')).select_by_value("1234") 
time.sleep(5)
Select(driver.find_element(By.XPATH, '//*[@id="year_select"]')).select_by_value("2020") 
time.sleep(5)
driver.find_element(By.XPATH, '//*[@id="ID_1"]').click()
time.sleep(4)

# Get the list of print links
list_container = driver.find_element(By.XPATH, '//*[@id="S_1"]')
links = list_container.find_elements(By.XPATH, ".//a[contains(@onclick, 'onclick_toc_print')]")

print(f"Found {len(links)} list items.")

# --- Step 2: Loop through links and save PDFs in headless Chrome ---
# links[x:] and start=x+1 if you need to pick up where it may have failed previously
for idx, link in enumerate(links, start=1):
    onclick_val = link.get_attribute("onclick")
    match_name = re.search(r"nodedesc=([^&']+)", onclick_val)
    if not match_name:
        print(f"Skipping link {idx}: no nodedesc found.")
        continue
  
    raw_name = unquote(match_name.group(1))
    safe_name = re.sub(r'[\\/*?:"<>|&]', "_", raw_name)
  
    try:
        base_url = "https://hyundaitechinfo.com/viewer/print_pop.aspx?printtype=toc_print&"
        full_url = base_url + onclick_val.split("cat1=")[1].split("')")[0]
    except IndexError:
        print(f"Skipping {raw_name}: could not parse URL.")
        continue

    print(f"[{idx}] {raw_name} -> {full_url}")

    # Open print page in a new tab
    time.sleep(3)
    driver.execute_script(f"window.open('{full_url}', '_blank');")
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(25)  # wait for page to load
  
    # Capture PDF via Chrome DevTools Protocol
    # pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {
    #     "printBackground": True,
    #     "landscape": False
    # })
  
    # output_path = os.path.join(download_dir, f"{safe_name}.pdf")
    # with open(output_path, "wb") as f:
    #     f.write(base64.b64decode(pdf_data['data']))
    # print(f"Saved: {output_path}")

    output_path = os.path.join(download_dir, f"{safe_name}.pdf")
  
    success = save_pdf_with_retry(driver, output_path, retries=3, wait_between=10)
    if success:
        print(f"Saved: {output_path}")
        time.sleep(12)
    else:
        print(f"Skipping {safe_name} after repeated failures.")

    time.sleep(2)
  
    # Close the tab and return to the main list
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
  
driver.quit()
