import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
import lxml


# Assuming you have saved the email content to a local HTML file named 'email_content.html'
file_path = 'email_content.html'

# Read the content of the HTML file
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Parse the HTML content using BeautifulSoup with lxml parser
soup = BeautifulSoup(content, 'lxml')
res = soup.select('html body div.bodycontainer div.maincontent table.message tbody tr td table tbody tr td div font div div center table#m_330407496311772806x_bodyTable tbody tr td#m_330407496311772806x_bodyCell table tbody tr td#m_330407496311772806x_templateBody table tbody tr td table tbody tr td table tbody tr td table tbody tr td span font strong')
res = [elt.text for elt in res if elt.text != '' and elt.text != '→\n']

print(res)
print(len(res))
