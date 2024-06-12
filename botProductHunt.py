import requests
from bs4 import BeautifulSoup
from lxml import etree
import asyncio
import telegram
import pandas as pd
from datetime import datetime, timedelta
import whois

BASE_URL = "https://www.producthunt.com"
TELEGRAM_TOKEN = '7498097561:AAEpEEkJ6qeLlx_EiTrLF7e6OjN0_2fo1Ys'
CHAT_ID = -4283455561
UPVOTES_THRESHOLD = 150

def get_previous_week_url():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_previous_week = start_of_week - timedelta(days=7)
    previous_week_year = start_of_previous_week.isocalendar()[0]
    previous_week_number = start_of_previous_week.isocalendar()[1]
    url = f"{BASE_URL}/leaderboard/weekly/{previous_week_year}/{previous_week_number}"
    return url

def fetch_trending_repositories():
    url = get_previous_week_url()
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    dom = etree.HTML(str(soup))
    list_items = dom.xpath('//div[contains(@class, "styles_item__Dk_nz")]')
    
    repos = []
    
    for repo in list_items:
        title_element = repo.xpath('.//strong')
        url_element = repo.xpath('.//div/div[contains(@class, "styles_titleContainer__qZRNa")]/a')
        votes_element = repo.xpath('.//div[contains(@class, "styles_voteCountItem__zwuqk")]')
        
        try:
            if title_element and url_element and votes_element:
                title = title_element[0].text.strip()
                url = BASE_URL + url_element[0].attrib["href"].strip()
                votes = int(votes_element[0].text.strip())
            
                repos.append({'title': title, 'url': url, 'votes': votes})
        except Exception as e:
            print(f"Error processing repo: {e}")
    
    return repos

def find_potential_startups(repos, star_threshold=UPVOTES_THRESHOLD) -> pd.DataFrame:
    df = pd.DataFrame(repos)
    if 'votes' not in df.columns:
        print("No 'votes' column found in the DataFrame.")
        return pd.DataFrame()
    
    potential_startups = df[df['votes'] > star_threshold]
    return potential_startups

def get_official_website_url(product_url):
    try:
        response = requests.get(product_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        button = soup.select_one('body > div > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > button:nth-child(1)')
        if button:
            official_url = button.get('href')
            return official_url
    except Exception as e:
        print(f"Error fetching official website URL for {product_url}: {e}")
        return None

def get_country_of_incorporation(official_url):
    try:
        domain = official_url.split("//")[-1].split("/")[0]
        whois_info = whois.whois(domain)
        return whois_info.get("country")
    except Exception as e:
        print(f"Error fetching WHOIS data for {official_url}: {e}")
        return None

async def main():
    bot = telegram.Bot(TELEGRAM_TOKEN)

    repos = fetch_trending_repositories()
    potential_startups = find_potential_startups(repos)
    messages = []

    for _, repo in potential_startups.iterrows():
        official_url = get_official_website_url(repo['url'])
        if official_url:
            country = get_country_of_incorporation(official_url)
            if country:
                messages.append(f"{repo['title']} ({official_url}) with {repo['votes']} votes - Country: {country}")

    message = '\n'.join(messages)
    
    async with bot:
        await bot.send_message(CHAT_ID, message or "No repository could be found")

if __name__ == '__main__':
    asyncio.run(main())

