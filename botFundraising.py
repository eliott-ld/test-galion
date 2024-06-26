import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
from datetime import date
import imaplib
import email
from email.policy import default
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os
import shutil
import glob

"""

TODO


-description chaque ligne OK
-website (via other email)
-automatiser pour qu'il download online (le slide + le newsletter) , OK
-automatiser pour qu'il run tous les lundis OK

-ré upload le spreadsheet

"""


# Email account credentials
username = "galiontest@outlook.com"
password = "irbetxtmdvatmkzy"
imap_server = 'outlook.office365.com'





def save_last_email_html(username, password, imap_server):
    # Connect to the server
    mail = imaplib.IMAP4_SSL(imap_server)
    
    # Login to your account
    mail.login(username, password)
    
    # Select the mailbox you want to use (in this case, the inbox)
    mail.select('inbox')
    
    # Search for all emails in the inbox
    status, data = mail.search(None, 'ALL')
    
    # Get the list of email IDs
    mail_ids = data[0].split()
    
    # Get the latest email ID
    latest_email_id = mail_ids[-1]
    
    # Fetch the latest email
    status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
    
    # Parse the email
    msg = email.message_from_bytes(msg_data[0][1], policy=default)
    
    # Find the HTML part
    html_content = None
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            html_content = part.get_payload(decode=True)
            break
    
    # Save the HTML content to a file
    if html_content:
        with open('email_content.html', 'wb') as f:
            f.write(html_content)
        print("HTML content saved to 'email_content.html'")
    else:
        print("No HTML content found in the latest email.")
    
    # Logout and close the connection
    mail.logout()

# Replace with your email credentials and server details
save_last_email_html(username, password, imap_server)



def download_google_folder(folder_id, output_folder):
    shutil.rmtree(output_folder, ignore_errors=True)
    os.makedirs(output_folder, exist_ok=True)
    # Authenticate and create a GoogleDrive instance
    drive = authenticate_and_create_drive()
    
    # List all files in the specified folder
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    
    # Download each file in the folder
    for file in file_list:
        file.GetContentFile(os.path.join(output_folder, file['title']))
        print(f"Downloaded file '{file['title']}'")

def get_latest_file(folder):
    list_of_files = glob.glob(folder + '/*') # * means all if need specific format then *.csv
    dates = [f.split('/')[-1].split('.')[0] for f in list_of_files]
    latest_file = max(dates)
    print(f'{latest_file}.report.xlsx')
    return f'{latest_file}.report.xlsx'









# Assuming you have saved the email content to a local HTML file named 'email_content.html'
file_path = 'email_content.html'

# Read the content of the HTML file
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(content, 'html.parser')

# Extract the text from the HTML content
email_text = soup.get_text()

# print(email_text)

# Define regex patterns to extract relevant information
pattern_founded = re.compile(r'Founded in:\s* (\d{4})', re.MULTILINE)
pattern_series = re.compile(r'Series:\s* (.+?)\n', re.MULTILINE)
pattern_funding = re.compile(r'New\s* Money in\s* press:\s* \€([\d.,]+[km])', re.MULTILINE)
pattern_investors = re.compile(r'Investors:\s* (.+?)\n', re.MULTILINE)


def normalize_funding(amount):
    amount = amount.replace(",", "")  # Remove any commas
    if 'k' in amount:
        return str(float(amount.replace('k', '')) * 1000)
    elif 'm' in amount:
        return str(float(amount.replace('m', '')) * 1000000)
    return amount
    

# Extracting data into lists
soup = BeautifulSoup(content, 'lxml')
res = soup.select('tbody tr td.mcnImageCardRightContentInner table.mcnImageCardRightTextContentContainer tbody tr td.mcnTextContent span font strong')


companies = [elt.text for elt in res if elt.text != '' and elt.text != '→\n']


res2 = soup.select('tbody.mcnImageCardBlockOuter tr td.mcnImageCardBlockInner table.mcnImageCardRightContentOuter tbody tr td.mcnImageCardRightContentInner table.mcnImageCardRightTextContentContainer tbody tr td.mcnTextContent span' )
descriptions_V1 = [elt.text for elt in res2 if elt.text != '']
descriptions_V2 = descriptions_V1[1::5]
descriptions= [elt for elt in descriptions_V2 if elt != '\xa0']

#print("Descriptions:", descriptions_V1)


founded_years = pattern_founded.findall(email_text)
series = pattern_series.findall(email_text)
funding_amounts = [normalize_funding(amount) for amount in pattern_funding.findall(email_text)]
investors = pattern_investors.findall(email_text)


# Ensure all lists are of equal length for DataFrame creation
max_len = max(len(companies), len(founded_years), len(series), len(funding_amounts),
              len(investors),len(descriptions))

companies.extend([''] * (max_len - len(companies)))
founded_years.extend([''] * (max_len - len(founded_years)))
series.extend([''] * (max_len - len(series)))
funding_amounts.extend([''] * (max_len - len(funding_amounts)))
investors.extend([''] * (max_len - len(investors)))
descriptions.extend([''] * (max_len - len(descriptions)))

#print(companies, founded_years, series, funding_amounts, investors)

# Create DataFrame
df = pd.DataFrame({
    'Organization Name': companies,
    'Founded Year': founded_years,
    'Series': series,
    'Money Raised': funding_amounts,
    'Money Raised Currency' : 'EUR',
    'Investor Names': investors,
    'Organization Description': descriptions,
})


today = date.today()
df['Announced Date'] = today


print(df)


df = df.replace('', np.nan, regex=True) 
df = df.dropna(axis=0)

#print(df)
# Output DataFrame to Excel
output_file = 'tech_companies_info_test.xlsx'
df.to_excel(output_file, index=False)
print(f"Excel file '{output_file}' has been created successfully.")




# Function to authenticate and create a GoogleDrive instance
def authenticate_and_create_drive():
    gauth = GoogleAuth()
    # Try to load saved client credentials
    try:
        gauth.LoadCredentialsFile("credentials.json")
    except:
        gauth.LoadClientConfigFile("client_secrets")

    if gauth.credentials is None:
        # Authenticate if credentials are not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved credentials
        gauth.Authorize()

    # Save the current credentials to a file
    gauth.SaveCredentialsFile("credentials.json")

    return GoogleDrive(gauth)


#######################################################



#######################################################


# Function to upload a file to Google Drive
def upload_file_to_drive(drive, file_path, folder_id=None):
    file_name = os.path.basename(file_path)
    file_drive = drive.CreateFile({'title': file_name, 'parents': [{'id': folder_id}] if folder_id else []})
    file_drive.SetContentFile(file_path)
    file_drive.Upload()
    print(f'Uploaded file "{file_name}" to Google Drive')

if __name__ == "__main__":
    drive = authenticate_and_create_drive()
    folder_id = '1f1IJNpubNhh5xImT1AbDPTNCjN0gixv2'
    outputFolder = 'output_folder'
    download_google_folder(folder_id, outputFolder)
    spreadsheet = get_latest_file(outputFolder)
    dfMain = pd.read_excel(outputFolder + '/' + spreadsheet)
    #print(dfMain.head(20))
    dfMain=pd.concat([df,dfMain], join='outer', ignore_index=True)
    #print(dfMain.head(20))
    filename = f'{today}.report.xlsx'
    dfMain.to_excel(filename, index=False)
    print(f"Results addded to the main spreadsheet")
    upload_file_to_drive(drive, filename, folder_id)









