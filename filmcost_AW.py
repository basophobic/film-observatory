import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

def get_exchange_rate(api_key):
    # Fetch the current GBP to EUR exchange rate
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/GBP/EUR"
    response = requests.get(url)
    data = response.json()
    return data['conversion_rate']

def fetch_film_data(url, film_format, film_type, availability_status, exchange_rate):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    film_entries = soup.find_all('div', class_='product-item__info-inner')
    film_data = []

    for film in film_entries:
        name = film.find('a', class_='product-item__title').get_text(strip=True)
        price = film.find('span', class_='money').get_text(strip=True).replace('£', '').strip()
        
        # Convert price from GBP to EUR
        if price.isdigit():
            price = f"{float(price) * exchange_rate:.2f} EUR"

        availability = 'In stock' if availability_status == "1" else 'Out of stock'
        normalized_film_type = "C41" if "Colour" in film_type else "BW"

        film_data.append({
            'Film Name': name,
            'Format': film_format,
            'Type': normalized_film_type,
            'Price': price,
            'Availability': availability
        })
    return film_data

def save_to_csv(data, filename):
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def main():
    api_key = 'replace-with-key-from-https://www.exchangerate-api.com/'  # Replace YOUR_API_KEY with your actual API key
    exchange_rate = get_exchange_rate(api_key)
    
    base_url_template = "https://analoguewonderland.co.uk/collections/bc-all?sort_by=manual&filter.v.price.gte=&filter.v.price.lte=&filter.p.m.custom.product_type={product_type}&filter.p.product_type={film_type}&filter.v.availability={availability}"
    types = [("35mm", "Colour"), ("35mm", "B%26W"), ("120", "Colour"), ("120", "B%26W")]
    availability = [("1", "In stock"), ("0", "Out of stock")]
    all_data = []

    for film_type, product_type in types:
        for avail_code, avail_desc in availability:
            url = base_url_template.format(product_type=product_type, film_type=film_type, availability=avail_code)
            data = fetch_film_data(url, film_type, product_type, avail_code, exchange_rate)
            all_data.extend(data)

    if all_data:
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        save_to_csv(all_data, f'prices/film_prices_{now}_AW.csv')
        print(f"Data saved to 'film_prices_{now}_AW.csv'")
    else:
        print("No data collected.")

if __name__ == "__main__":
    main()
