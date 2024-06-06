import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import pandas as pd

TELEGRAM_TOKEN = '7498097561:AAEpEEkJ6qeLlx_EiTrLF7e6OjN0_2fo1Ys'
CHAT_ID = -4283455561
STARS_THRESHOLD = 150

def fetch_trending_repositories():
    # Fetch the GitHub trending page
    url = "https://github.com/trending"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all repository elements
    repo_elements = soup.find_all('article', class_='Box-row')
    
    # List to hold the repository data
    repos = []
    
    # Extract data from each repository element
    for repo in repo_elements:
        # Find the URL element within the repository
        repo_url_element = repo.find('a')
        
        # Find the element containing stars count
        for elt in repo.findAll('span'):
            if "stars today" in elt.text:
                stars_element = elt
                break
        
        # Check if URL element and stars count element are found
        if repo_url_element:
            # Extract repository URL
            repo_url = 'https://github.com' + repo_url_element['href']
            
            # Extract stars count and remove unnecessary text
            stars = int(stars_element.text.strip().removesuffix(" stars today").replace(',',''))
            
            # Append repository data to the list
            repos.append({'url': repo_url, 'stars': stars})
        else:
            # Print a message if any required element is missing
            print(f"Skipping repository due to missing data: {repo_url_element}, {stars_element}")
    
    return repos

def find_potential_startups(repos, star_threshold=STARS_THRESHOLD) -> pd.DataFrame:
    # Convert repository data to DataFrame
    df = pd.DataFrame(repos)
    
    # Check if 'stars' column exists in the DataFrame
    if 'stars' not in df.columns:
        print("No 'stars' column found in the DataFrame.")
        return pd.DataFrame()  # Return an empty DataFrame
    
    # Filter potential startups based on stars count
    potential_startups = df[df['stars'] > star_threshold]
    return potential_startups

async def main():
    bot = telegram.Bot(TELEGRAM_TOKEN)

    repos = fetch_trending_repositories()
    potential_startups = find_potential_startups(repos)
    message = '\n'.join([f"{repo['url']} with {repo['stars']} stars" for (_, repo) in potential_startups.iterrows()])

    async with bot:
        await bot.send_message(CHAT_ID, message or "No repository could be found")

if __name__ == '__main__':
    asyncio.run(main())

