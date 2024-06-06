import requests
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler

# Function to fetch trending repositories
def fetch_trending_repositories():
    url = 'https://github.com/trending'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    repos = []
    
    for repo in soup.find_all('article', class_='Box-row'):
        name = repo.h1.a.get('href').strip('/')
        stars = repo.find('a', class_='Link--muted d-inline-block mr-3').text.strip()
        stars = int(stars.replace(',', ''))
        repos.append({'name': name, 'stars': stars})
    
    return repos

# Function to find potential startups
def find_potential_startups(repos):
    threshold = 1000  # Define a threshold for potential startups
    potential_startups = [repo for repo in repos if repo['stars'] > threshold]
    return potential_startups

# Define the command handler function
def start(update, context):
    repos = fetch_trending_repositories()
    potential_startups = find_potential_startups(repos)
    message = '\n'.join([f"{repo['name']} with {repo['stars']} stars" for repo in potential_startups])
    context.bot.send_message(chat_id=update.effective_chat.id, text=message or "No potential startups found.")

def main():
    # Your bot token from BotFather
    TOKEN = '7498097561:AAEpEEkJ6qeLlx_EiTrLF7e6OjN0_2fo1Ys'
    
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Add command handler to dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    
    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

