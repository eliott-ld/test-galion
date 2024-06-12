import requests
from bs4 import BeautifulSoup
from lxml import etree

BASE_URL = "https://www.producthunt.com"

def fetch_trending_repositories():
    # Fetch the Product Hunt leaderboard page
    url = BASE_URL +"/leaderboard/weekly/2024/24"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    dom = etree.HTML(str(soup))
    # Adjust the XPath to target the specific elements of interest
    list_items = dom.xpath('//div[contains(@class, "styles_item__Dk_nz")]')
    
    # List to hold the repository data
    repos = []
    
    # Extract data from each repository element
    for repo in list_items:
        # Extract necessary information, this example assumes some possible structure
        # Adjust according to the actual structure of the page
        title_element = repo.xpath('.//strong')
        url_element = repo.xpath('.//div/div[contains(@class, "styles_titleContainer__qZRNa")]/a')
        votes_element = repo.xpath('.//div[contains(@class, "styles_voteCountItem__zwuqk")]')
        # print(title_element, url_element, votes_element)

        try:
            if title_element and url_element and votes_element:
                title = title_element[0].text.strip()
                url = BASE_URL + url_element[0].attrib["href"].strip()
                votes = int(votes_element[0].text.strip())
            
                # Append repository data to the list
                repos.append({'title': title, 'url': url, 'votes': votes})
        except:
            pass
    
    return repos

def main():
    repos = fetch_trending_repositories()
    print(repos)

if __name__ == '__main__':
    main()
