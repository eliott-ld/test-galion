import re
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Assuming you have saved the email content to a local HTML file named 'email_content.html'
file_path = 'email_content.html'

# Read the content of the HTML file
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(content, 'html.parser')

# Extract the text from the HTML content
email_text = soup.get_text()



# Define regex patterns to extract relevant information
pattern_founded = re.compile(r'Founded in: (\d{4})', re.MULTILINE)
pattern_series = re.compile(r'Series: (.+?)\n', re.MULTILINE)
pattern_funding = re.compile(r'New Money in press: €([\d.,]+)', re.MULTILINE)
pattern_investors = re.compile(r'Investors: (.+?)\n', re.MULTILINE)
pattern_sector = re.compile(r'#Sector (.*?)\n', re.MULTILINE)
pattern_business_model = re.compile(r'#BusinessModel (.*?)\n', re.MULTILINE)
pattern_focus = re.compile(r'#Focus (.*?)\n', re.MULTILINE)

# Extracting data into lists
soup = BeautifulSoup(content, 'lxml')
res = soup.select('html body div.bodycontainer div.maincontent table.message tbody tr td table tbody tr td div font div div center table#m_330407496311772806x_bodyTable tbody tr td#m_330407496311772806x_bodyCell table tbody tr td#m_330407496311772806x_templateBody table tbody tr td table tbody tr td table tbody tr td table tbody tr td span font strong')
companies = [elt.text for elt in res if elt.text != '' and elt.text != '→\n']
founded_years = pattern_founded.findall(email_text)
series = pattern_series.findall(email_text)
funding_amounts = pattern_funding.findall(email_text)
investors = pattern_investors.findall(email_text)
sectors = pattern_sector.findall(email_text)
business_models = pattern_business_model.findall(email_text)
focuses = pattern_focus.findall(email_text)

# Ensure all lists are of equal length for DataFrame creation
max_len = max(len(companies), len(founded_years), len(series), len(funding_amounts),
              len(investors), len(sectors), len(business_models), len(focuses))

companies.extend([''] * (max_len - len(companies)))
founded_years.extend([''] * (max_len - len(founded_years)))
series.extend([''] * (max_len - len(series)))
funding_amounts.extend([''] * (max_len - len(funding_amounts)))
investors.extend([''] * (max_len - len(investors)))
sectors.extend([''] * (max_len - len(sectors)))
business_models.extend([''] * (max_len - len(business_models)))
focuses.extend([''] * (max_len - len(focuses)))

print(companies, founded_years, series, funding_amounts, investors, sectors, business_models, focuses)

# Create DataFrame
df = pd.DataFrame({
    'Company': companies,
    'Founded Year': founded_years,
    'Series': series,
    'Funding Amount (€)': funding_amounts,
    'Investors': investors,
    'Sector': sectors,
    'Business Model': business_models,
    'Focus': focuses
})

# Output DataFrame to Excel
output_file = 'tech_companies_info.xlsx'
df.to_excel(output_file, index=False)
print(f"Excel file '{output_file}' has been created successfully.")



