import os
import re
import time
import base64
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options

def save_pdf_with_retry(driver, output_path, retries=2, wait_between=5):
    """
    Attempts to save a PDF via Firefox's print_page(), retrying on timeout or failure.
    """
    for attempt in range(retries):
        try:
            # Simple call for older Selenium versions
            pdf_base64 = driver.print_page()
            time.sleep(4)

            with open(output_path, "wb") as f:
                f.write(base64.b64decode(pdf_base64))
            return True
        except Exception as e:
            print(f"PDF save failed (attempt {attempt+1}): {e}")
            time.sleep(wait_between)
    return False
  
username = ""
password = ""
download_dir = "../docs"
  
# Firefox options
firefox_opts = Options()
firefox_opts.add_argument("--width=1800")
firefox_opts.add_argument("--height=1080")
# Headless is required for print_page() in most cases
firefox_opts.add_argument("--headless")
  
driver = webdriver.Firefox(options=firefox_opts)
driver.set_page_load_timeout(120)
driver.set_script_timeout(120)
  
# Step 1: Login
driver.get("https://hyundaitechinfo.com/")
time.sleep(4)
driver.find_element(By.XPATH, '//*[@id="user_id"]').send_keys(username)
driver.find_element(By.XPATH, '//*[@id="user_pw"]').send_keys(password)
driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/div').click()
time.sleep(5)

# Navigate to section
driver.get("https://hyundaitechinfo.com/viewer/default.aspx?menu_id=13&sel_topmenu=337&sel_submenu=13&group=COMP")
time.sleep(5)

# Select(driver.find_element(By.XPATH, '//*[@id="modelid_select"]')).select_by_value("1234")
Select(driver.find_element(By.XPATH, '//*[@id="modelid_select"]')).select_by_value("1234")
time.sleep(5)
Select(driver.find_element(By.XPATH, '//*[@id="year_select"]')).select_by_value("2020")
time.sleep(5)
driver.find_element(By.XPATH, '//*[@id="ID_1"]').click()
time.sleep(4)
  
# Get list of print links
list_container = driver.find_element(By.XPATH, '//*[@id="S_1"]')
links = list_container.find_elements(By.XPATH, ".//a[contains(@onclick, 'onclick_toc_print')]")
print(f"Found {len(links)} list items.")
  
# Loop through links
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
  
    # Open in new tab
    driver.execute_script(f"window.open('{full_url}', '_blank');")
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(25)  # wait for page to load
  
    # Save PDF using Firefox's print_page
    output_path = os.path.join(download_dir, f"{safe_name}.pdf")
    success = save_pdf_with_retry(driver, output_path, retries=3, wait_between=10)
    if success:
        print(f"Saved: {output_path}")
        time.sleep(12)
    else:
        print(f"Skipping {safe_name} after repeated failures.")
  
    # Close tab and return to main list
    # driver.close()
    driver.switch_to.window(driver.window_handles[0])
  
driver.quit()