import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
from datetime import datetime

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def load_iso_reference(filename):
    iso_dict = {}
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            iso_dict[row[0].strip()] = row[1].strip()
    return iso_dict

def accept_cookies(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//button[text()="Allow all"]')))
        accept_button = driver.find_element(By.XPATH, '//button[text()="Allow all"]')
        accept_button.click()
    except Exception as e:
        pass
        #print(f"Could not find or click cookie acceptance: {str(e)}")

def navigate_and_apply_filters(driver, url, film_type_selector, film_format, film_type):
    driver.get(url)
    accept_cookies(driver)

    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-xs:nth-child(1) > i:nth-child(1)"))).click()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.select2:nth-child(11) > span:nth-child(1) > span:nth-child(1) > span:nth-child(2)"))).click()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, film_type_selector))).click()
        time.sleep(2)

        print(f"Collecting prices for films {film_format} - {film_type}")

    except Exception as e:
        print(f"An error occurred while interacting with the dropdown: {e}")
        driver.save_screenshot("error_screenshot.png")

def collect_film_data(driver, film_format, film_type):
    film_data = []
    try:
        films = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.os_list_wrap_all")))
        for film in films:
            try:
                name = film.find_element(By.CLASS_NAME, "os_list_title").text
                prices = film.find_element(By.CLASS_NAME, "os_list_price2").text.split('\n')
                price_vat = prices[0].split('EUR')[1].strip().replace('*', '').replace(',', '.')
                availability_element = film.find_element(By.CSS_SELECTOR, "div[class^='os_list_shipt']")
                availability_text = availability_element.text
                availability = "In stock" if "In stock" in availability_text else "Out of stock"
                film_data.append({
                    "Film Name": name,
                    "Format": film_format,
                    "Type": film_type,
                    "Price": price_vat,
                    "Availability": availability
                })
            except Exception as e:
                print(f"Error while extracting data for a film: {e}")
    except Exception as e:
        print(f"Error while collecting film data: {e}")
    
    return film_data

def save_data_to_csv(data, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Film Name", "Format", "Type", "Price", "Availability"])
        writer.writeheader()
        writer.writerows(data)

def main():
    driver = setup_driver()
    all_data = []
    urls_and_types = [
        ("https://www.fotoimpex.com/films/35mm-films/", "#os_filter_AFilmtype > option:nth-child(2)", "35mm", "BW"),  # 35mm BW
        ("https://www.fotoimpex.com/films/35mm-films/", "#os_filter_AFilmtype > option:nth-child(4)", "35mm", "C41"),  # 35mm Color C41
        ("https://www.fotoimpex.com/films/medium-format-films-120/", "#os_filter_AFilmtype > option:nth-child(2)", "120", "BW"),  # 120 BW
        ("https://www.fotoimpex.com/films/medium-format-films-120/", "#os_filter_AFilmtype > option:nth-child(3)", "120", "C41"),  # 120 Color C41
        
        # the following can be added to collect Slide films as well
        #("https://www.fotoimpex.com/films/35mm-films/", "#os_filter_AFilmtype > option:nth-child(3)", "35mm", "BW Slide"),  # 35mm BW Slide
        #("https://www.fotoimpex.com/films/35mm-films/", "#os_filter_AFilmtype > option:nth-child(5)", "35mm", "Color Slide"),  # 35mm Color Slide
        #("https://www.fotoimpex.com/films/35mm-films/", "#os_filter_AFilmtype > option:nth-child(6)", "35mm", "Color ECN2"),  # 35mm Color ECN2
        #("https://www.fotoimpex.com/films/medium-format-films-120/", "#os_filter_AFilmtype > option:nth-child(4)", "120", "Color Slide"),  # 120 Color Slide
                      
        ]
    for url, film_type_selector, film_format, film_type in urls_and_types:
        navigate_and_apply_filters(driver, url, film_type_selector, film_format, film_type)
        while True:
            data = collect_film_data(driver, film_format, film_type)
            all_data.extend(data)
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".col-sm-9 > a:nth-child(3)")
                if next_button.is_displayed() and "forward" in next_button.text:
                    next_button.click()
                    time.sleep(5)
                else:
                    break
            except Exception as e:
                #print(f"No more pages or an error occurred: {e}")
                break

    filename = f"prices/film_prices_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_FI.csv"
    save_data_to_csv(all_data, filename)
    print(f"All data succesfully store in {filename}")
    driver.quit()

if __name__ == "__main__":
    main()
