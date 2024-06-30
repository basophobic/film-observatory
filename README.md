# Film Price Observatory

This project contains two Python scripts for collecting film prices from Analogue Wonderland and Fotoimpex. Each script gathers data on film stock, availability, and price, saving the results to a CSV file.

## Description

The Film Price Observatory automates the collection of film data for analysis, allowing you to track price changes over time and make informed purchasing decisions.

## Installation

1. **Prerequisites**:
   - Python 3.x
   - Google Chrome browser

2. **Install Required Packages**:
   ```bash
   pip install selenium webdriver-manager pandas
   ```

## Usage

### Fotoimpex Film Observatory

This script collects film prices from the Fotoimpex website for 35mm and 120 films, both in black & white and color.

- **Command to run**:
  ```bash
  python filmcost_FI.py
  ```

### Analogue Wonderland Film Observatory

This script collects film prices from the Analogue Wonderland website, collecting information for different categories of films.

- **Command to run**:
  ```bash
  python filmcost_AW.py
  ```

## Output

- **CSV Files**: The scripts generate CSV files with the following columns:
  - Film Name
  - Price in Euros
  - Availability
  - Format (135 or 120)
  - Type (BW or Color)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or features.

## Acknowledgments

- This project uses the Selenium library for web scraping.
- Special thanks to the film photography community for inspiration.
