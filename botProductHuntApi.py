import json
import requests
import whois
from graphene import ObjectType, String, Schema
import pandas as pd

API_KEY_PH = "FsLe8vVtRveM1I47ANnjIQfYJrW_at6l2rlB2eJPXKw"

def fetch_data(query, api_key):
    url = 'https://api.producthunt.com/v2/api/graphql'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    response = requests.post(url, headers=headers, json={'query': query})
    return response.json()

class ProductHunt:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_top_weekly(self):
        query = '''
            query {
              posts(order: VOTES, first: 10, postedAfter:  "2024-06-05T00:00:00Z" ) {
                edges {
                  node {
                    id
                    name
                    tagline
                    votesCount
                    productLinks{
                      url
                    }
                  }
                }
              }
            }
        '''
        data = fetch_data(query, self.api_key)
        products = data.get('data', {}).get('posts', {}).get('edges', [])
        
        product_list = []
        for edge in products:
            product = edge.get('node', {})
            product_list.append({
                'ID': product.get('id'),
                'Name': product.get('name'),
                'Tagline': product.get('tagline'),
                'Url': product.get('productLinks')[0].get('url'),
            })
        
        return product_list

    def add_country_field(self, data):
        result = []
        for elt in data:
            real_url = get_redirect_url(elt["Url"])
            elt["Url"] = real_url
            country =  is_us(real_url)
            if country:
                elt["Country"] = country
                result.append(elt)


def is_us(official_url):
    domain = official_url.split("//")[-1].split("/")[0]
    try:
        whois_info = whois.whois(domain)
    except Exception as e:
        print(f"Error fetching WHOIS data for {official_url}: {e}")
        return False
    country = whois_info is not None and pass_the_filter(whois_info)
    if country:
        return country
    return False

def pass_the_filter(data):
    for val in data.values():
        if val in ["US", "us"]:
            return val
        if val is list and ("US" in val or "us" in val):
            return val
    return False


def get_redirect_url(url):
    response = requests.head(url, allow_redirects=True)
    print("url "+url+" is " +response.url)
    return response.url

def render_md_table(data):
    """
    data = [
       {"symbol": "ABC", "Price":20.85,"Change":1.626}, ...,  {"symbol": "JKL", "Price":98.85,"Change":0.292}
    ] 
    output =
    | Symbol | Price | Change |
    |--------|-------|--------|
    | ABC    | 20.85 |  1.626 |
    | DEF    | 78.95 |  0.099 |
    | GHI    | 23.45 |  0.192 |
    | JKL    | 98.85 |  0.292 |
    """
    return pd.DataFrame(data)[["Name", "Country"]].to_markdown()

def main():
    # bot =  ProductHunt(API_KEY_PH)
    # products = bot.get_top_weekly()
    # bot.add_country_field(products)
    # print(products)
    products = [{'ID': '461713', 'Name': 'Sleepytales', 'Tagline': 'Have AI read and write personalized bedtime stories', 'Url': 'https://www.sleepytales.ai/?ref=producthunt'}, {'ID': '456730', 'Name': 'Active Recall', 'Tagline': 'Summarize anything, forget nothing', 'Url': 'https://www.getrecall.ai?ref=producthunt'}, {'ID': '461186', 'Name': 'FlowMapp 3.0', 'Tagline': 'Visual website planning in the most powerful way', 'Url': 'https://www.flowmapp.com/?ref=producthunt'}, {'ID': '461543', 'Name': 'Fliki', 'Tagline': 'Turn text into videos with AI voices', 'Url': 'https://fliki.ai/?ref=producthunt'}, {'ID': '461189', 'Name': 'Second V2', 'Tagline': 'AI powered codebase maintenance', 'Url': 'https://www.second.dev?ref=producthunt'}, {'ID': '460619', 'Name': 'Elai', 'Tagline': 'Generate interactive AI videos with quizzes & hotspots', 'Url': 'https://elai.io?ref=producthunt'}, {'ID': '461771', 'Name': 'TeamCreate', 'Tagline': "AI's for hundreds of roles in sales, finance & more", 'Url': 'https://www.teamcreate.ai/?ref=producthunt'}, {'ID': '461406', 'Name': 'Syfly', 'Tagline': 'Trusted partner for simplified data storage & easy sharing ', 'Url': 'https://play.google.com/store/apps/details?id=com.syfly.io&ref=producthunt', 'Country': 'US'}, {'ID': '460094', 'Name': 'Databutton', 'Tagline': 'Let AI build your next SaaS application', 'Url': 'https://databutton.com/'}, {'ID': '450319', 'Name': 'Zeacon', 'Tagline': 'The 24/7 video marketer', 'Url': 'https://zeacon.com/?ref=producthunt', 'Country': 'US'}]
    print("```\n"+render_md_table(products)+"\n```")

if __name__ == "__main__":
    main()
