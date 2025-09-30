# Overview

This project automates the process of logging into the Hyundai Tech Info website and downloading technical PDF documents for vehicle components and replacements. It uses Selenium WebDriver to control Chrome and Firefox browsers, navigate the site, and save PDFs for offline reference. 

Scripts are provided for both Chrome and Firefox, and can be used to:

- Log in to the Hyundai Tech Info portal
- Navigate to specific vehicle/component sections
- Download and save PDF documents automatically

## Folder Structure 

- chrome: Scripts for Chrome automation (compare files, save component PDFs, save replacement PDFs) 
- firefox: Scripts for Firefox automation (save component PDFs) 
- docs: Default output directory for downloaded PDFs 
- requirements.txt: Python dependencies

## Getting Started 

### 1. Clone the Repository 

git clone https://github.com/taylor2464/download-hyundai-tech-info.git 

cd hyundaitechinfo

### 2. Set Up Python Environment 

It is recommended to use a virtual environment: python -m venv env 

(on linux)
source env/bin/activate

(on Windows)
.\env\bin\activate.ps1

### 3. Install Dependencies 

pip install -r requirements.txt

### 4. Download WebDriver 

- For Chrome: Download ChromeDriver and ensure it matches your Chrome version. 
- For Firefox: Download geckodriver and ensure it matches your Firefox version. 
- Place the driver in your PATH or the project root.

### 5. Configure Credentials 

Edit the relevant script(s) in chrome or firefox and set your Hyundai Tech Info username and password at the top of the file: 

username = "your_username"

password = "your_password"

### 6. Configure Vehicle

```python
Select(driver.find_element(By.XPATH, '//*[@id="modelid_select"]')).select_by_value("1234") 
time.sleep(5)  
Select(driver.find_element(By.XPATH, '//*[@id="year_select"]')).select_by_value("2020")  
```

Find the above lines in the script and enter your vehicle information. You may need to use devtools in your browser of choice to find out that information.


### 7. Run a Script 

For example, to save component PDFs using Chrome: python save_component_pdfs.py

PDFs will be saved in the docs directory by default.

## Notes 

Adjust timeouts and waits in the scripts if you encounter issues with slow page loads. Make sure your browser and WebDriver versions are compatible.

Please respect https://hyundaitechinfo.com/ terms of services and don't abuse it.
