import pytz
import requests
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
import os
from googletrans import Translator  # Import translator
from urllib.parse import urlparse

class ScrapeService:
    translator = Translator()  # Initialize translator for translating league names

    @staticmethod
    def should_skip_league(league_title):
        return (
            any(keyword in league_title.lower() for keyword in ["open", "volleyball", "basketball", "wells"])
            or league_title.lower() == "nba"
        )
    
    @staticmethod
    def scrape_matches():
        # Define the base URL for scraping
        BASE_URL = "https://v12.cakeo36.diy"
        response = requests.get(f'{BASE_URL}')
        html = response.content

        if html:
            soup = BeautifulSoup(html, 'html.parser')

            # For live matches
            live_div = soup.select('.tag_content')[0]
            live_matches = []
            tournaments = live_div.select('.tourz')

            for tour in tournaments:
                league_title = tour.select_one('.league_title').get_text()
                english_league_title = ScrapeService.auto_translate(league_title)
                if ScrapeService.should_skip_league(english_league_title):
                    continue

                matches = tour.select('.match')

                for match in matches:
                    date = match.select_one('.grid-match__date_m').get_text()
                    href = match['href']
                    link = BASE_URL + href
                    id = ScrapeService.extract_id(link)
                    home = match.select_one('.team--home')
                    if home is None:
                        continue
                    home_logo = ScrapeService.replace_logo_link(home.select_one('.team__logo')['data-src'])
                    home_name = home.select_one('.team__name').get_text()
                    home_score = match.select_one('.match__ts .score-home').get_text() if match.select_one('.match__ts .score-home') else ''

                    away = match.select_one('.team--away')
                    if away is None:
                        continue
                    away_logo = ScrapeService.replace_logo_link(away.select_one('.team__logo')['data-src'])
                    away_name = away.select_one('.team__name').get_text()
                    away_score = match.select_one('.match__ts .score-away').get_text() if match.select_one('.match__ts .score-away') else ''

                    video_links = ScrapeService.get_video_links(id)

                    if not video_links:
                        continue

                    live_matches.append({
                        'video_links': video_links,
                        'date': ScrapeService.format_date(date),
                        'league': english_league_title.strip(),
                        'home': {
                            'name': home_name,
                            'logo': home_logo,
                            'score': home_score
                        },
                        'away': {
                            'name': away_name,
                            'logo': away_logo,
                            'score': away_score
                        }
                    })

            # For today
            today_div = soup.select('.tag_content')[1]
            today_matches = []
            tournaments = today_div.select('.tourz')

            for tour in tournaments:
                league_title = tour.select_one('.league_title').get_text()
                english_league_title = ScrapeService.auto_translate(league_title)
                if ScrapeService.should_skip_league(english_league_title):
                    continue

                matches = tour.select('.match')

                for match in matches:
                    date = match.select_one('.grid-match__date_m').get_text()
                    if not date:
                        continue
                    href = match['href']
                    link = BASE_URL + href
                    id = ScrapeService.extract_id(link)
                    home = match.select_one('.team--home')
                    if home is None:
                        continue
                    home_logo = ScrapeService.replace_logo_link(home.select_one('.team__logo')['data-src'])
                    home_name = home.select_one('.team__name').get_text()

                    away = match.select_one('.team--away')
                    if away is None:
                        continue
                    away_logo = ScrapeService.replace_logo_link(away.select_one('.team__logo')['data-src'])
                    away_name = away.select_one('.team__name').get_text()
                    video_links = ScrapeService.get_video_links(id)

                    today_matches.append({
                        'video_links': video_links,
                        'date': ScrapeService.format_date(date),
                        'league': english_league_title.strip(),
                        'home': {
                            'name': home_name,
                            'logo': home_logo,
                            'score': ""
                        },
                        'away': {
                            'name': away_name,
                            'logo': away_logo,
                            'score': ""
                        }
                    })

            # For tomorrow
            tomorrow_div = soup.select('.tag_content')[2]
            tomorrow_matches = []
            tournaments = tomorrow_div.select('.tourz')

            for tour in tournaments:
                league_title = tour.select_one('.league_title').get_text()
                english_league_title = ScrapeService.auto_translate(league_title)
                if ScrapeService.should_skip_league(english_league_title):
                    continue

                matches = tour.select('.match')

                for match in matches:
                    date = match.select_one('.grid-match__date_m').get_text()
                    if not date:
                        continue
                    href = match['href']
                    link = BASE_URL + href
                    home = match.select_one('.team--home')
                    if home is None:
                        continue
                    home_logo = ScrapeService.replace_logo_link(home.select_one('.team__logo')['data-src'])
                    home_name = home.select_one('.team__name').get_text()

                    away = match.select_one('.team--away')
                    if away is None:
                        continue
                    away_logo = ScrapeService.replace_logo_link(away.select_one('.team__logo')['data-src'])
                    away_name = away.select_one('.team__name').get_text()
                    video_links = []

                    tomorrow_matches.append({
                        'video_links': video_links,
                        'date': ScrapeService.format_date(date),
                        'league': english_league_title.strip(),
                        'home': {
                            'name': home_name,
                            'logo': home_logo,
                            'score': ""
                        },
                        'away': {
                            'name': away_name,
                            'logo': away_logo,
                            'score': ""
                        }
                    })

            # For next day
            tomo_div = soup.select('.tag_content')[3]
            tomo_matches = []
            tournamen = tomo_div.select('.tourz')

            for tour in tournamen:
                league_title = tour.select_one('.league_title').get_text()
                english_league_title = ScrapeService.auto_translate(league_title)
                if ScrapeService.should_skip_league(english_league_title):
                    continue

                matches = tour.select('.match')

                for match in matches:
                    date = match.select_one('.grid-match__date_m').get_text()
                    if not date:
                        continue
                    href = match['href']
                    link = BASE_URL + href
                    home = match.select_one('.team--home')
                    if home is None:
                        continue
                    home_logo = ScrapeService.replace_logo_link(home.select_one('.team__logo')['data-src'])
                    home_name = home.select_one('.team__name').get_text()

                    away = match.select_one('.team--away')
                    if away is None:
                        continue
                    away_logo = ScrapeService.replace_logo_link(away.select_one('.team__logo')['data-src'])
                    away_name = away.select_one('.team__name').get_text()
                    video_links = []

                    tomo_matches.append({
                        'video_links': video_links,
                        'date': ScrapeService.format_date(date),
                        'league': english_league_title.strip(),
                        'home': {
                            'name': home_name,
                            'logo': home_logo,
                            'score': ""
                        },
                        'away': {
                            'name': away_name,
                            'logo': away_logo,
                            'score': ""
                        }
                    })

            # Merge and deduplicate matches
            all_matches = live_matches + today_matches + tomorrow_matches + tomo_matches

            new_match_data = ScrapeService.fetch_new_match_data()
            if new_match_data:
                all_matches = new_match_data + all_matches

            unique_matches = ScrapeService.remove_duplicates(all_matches)

            json_data = json.dumps(unique_matches, indent=4)
            storage_path = os.path.join(os.path.dirname(__file__), '..', '..', 'storage', 'app', 'data', 'scrape.json')

            os.makedirs(os.path.dirname(storage_path), exist_ok=True)

            with open(storage_path, 'w') as json_file:
                json_file.write(json_data)

    @staticmethod
    def fetch_new_match_data():
        # Fetch new match data from the API
        api_url = "https://minkhant.singapore2dmm.com/n4vip/new_match.json"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            try:
                match_data = response.json()
                if isinstance(match_data, list) and len(match_data) > 0:
                    return match_data
                else:
                    return None
            except Exception as e:
                return None
        else:
            return None

    @staticmethod
    def replace_logo_link(logo_url):
        # Replace a specific logo URL with a custom one
        if logo_url == 'https://img.thesports.com/football/team/0a11e714b8ccb1e287520857bd6cf01c.png':
            return 'https://football.redsport.live//storage/01HQNMEPGZC4XHY6ZWW022VAYN.png'
        return logo_url

    @staticmethod
    def auto_translate(text):
        # Translate text from Vietnamese to English
        try:
            translated = ScrapeService.translator.translate(text, src='vi', dest='en')
            return translated.text
        except Exception as e:
            print(f"Translation failed: {e}")
            return text

    @staticmethod
    def extract_id(link):
        # Extract match ID and base URL from a match page
        response = requests.get(link)

        if response.status_code == 200:
            page_content = response.text

            id_match = re.search(r"matchId\s*=\s*'([^']+)'", page_content)
            tag_id = id_match.group(1) if id_match else "ID not found"

            match = re.search(r"let\s+base_embed_url\s*=\s*'([^']+)'", page_content)

            if match:
                base_embed_url = match.group(1)
                parsed_url = urlparse(base_embed_url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

            return tag_id + ':' + base_url
        else:
            return "error"

    @staticmethod
    def get_scraped_matches():
        # Read scraped matches from the JSON file
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'storage', 'app', 'data', 'scrape.json')
        with open(path, 'r') as json_file:
            data = json.load(json_file)
        return data if data else []

    @staticmethod
    def get_video_links(id_value):
        # Fetch video links for a match using its ID
        try:
            value, referer = id_value.split(":", 1)
            url = f'https://api.cakeo.xyz/match/meta-v2/{value}'
            response = requests.get(url)
            match_data = response.json()

            if match_data.get('status') == 1:
                fansites = match_data.get('data', {}).get('fansites', [])
                if fansites:
                    video_links = fansites[0].get('play_urls', [])
                else:
                    video_links = []

                backup_links = []
                other_links = []

                for link in video_links:
                    link['name'] = ScrapeService.auto_translate(link.get('name', ''))
                    
                    skip_names = ["HD", "FullHD", "Radio", "HD1"]

                    if link['name'] in skip_names:
                        continue  # Skip only "HD" and "HD1"

                    link['referer'] = referer
                    if link['name'] == "Backup 2":
                        link['name'] = 'English 2'
                        backup_links.append(link)
                    elif link['name'] == "Backup 1":
                        link['name'] = 'English 1'
                        backup_links.append(link)
                    else:
                        other_links.append(link)

                return other_links + backup_links
            else:
                return match_data
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def format_date(input):
        # Format date from Vietnam time to Myanmar time
        if not input.strip():
            return ''

        current_year = '2025'
        formatted_input = f"{input} {current_year}"

        try:
            vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
            date_time_vietnam = datetime.strptime(formatted_input, '%H:%M %d/%m %Y')
            date_time_vietnam = vietnam_timezone.localize(date_time_vietnam)

            myanmar_timezone = pytz.timezone('Asia/Yangon')
            date_time_myanmar = date_time_vietnam.astimezone(myanmar_timezone)

            return date_time_myanmar.strftime('%Y-%m-%d %H:%M:%S')

        except ValueError as e:
            print(f"Error parsing date '{formatted_input}': {e}")
            return ''

    @staticmethod
    def remove_duplicates(matches):
        # Remove duplicate matches based on team names
        seen = set()
        unique_matches = []

        for match in matches:
            if "off fans" in match['home']['name'].lower() or "off fan" in match['away']['name'].lower():
                continue

            home_name = match['home']['name'].lower()
            away_name = match['away']['name'].lower()

            if home_name in seen or away_name in seen:
                continue
            
            seen.add(home_name)
            seen.add(away_name)
            unique_matches.append(match)

        return unique_matches

    @staticmethod
    def fetch_video_link_from_github():
        # Fetch video links from a GitHub API
        github_api_url = "https://minkhant.singapore2dmm.com/football/video.json"
        response = requests.get(github_api_url)
        
        if response.status_code == 200:
            file_content = response.json()
            return file_content
        else:
            return []

    @staticmethod
    def add_video_links_from_api():
        # Add video links from another API to scraped matches
        api_url = "https://football.redsport.live/api/test"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            try:
                api_data = response.json()
                if isinstance(api_data, list) and len(api_data) > 0:
                    matches = ScrapeService.get_scraped_matches()
                    
                    for match in matches:
                        home_name = match['home']['name']
                        away_name = match['away']['name']

                        for api_match in api_data:
                            api_home = api_match['home']['name']
                            api_away = api_match['away']['name']
                            video_links = api_match.get("video_links", [])

                            if home_name == api_home or away_name == api_away:
                                for video_link in video_links:
                                    if video_link not in match['video_links']:
                                        match['video_links'].insert(0, video_link)
                    
                    # Save updated matches back to the JSON file
                    storage_path = os.path.join(os.path.dirname(__file__), '..', '..', 'storage', 'app', 'data', 'scrape.json')
                    with open(storage_path, 'w') as json_file:
                        json.dump(matches, json_file, indent=4)
            except Exception as e:
                print(f"Error fetching video links: {e}")

if __name__ == '__main__':
    ScrapeService.scrape_matches()
    ScrapeService.add_video_links_from_api()
    matches = ScrapeService.get_scraped_matches()
    new_video_link = ScrapeService.fetch_video_link_from_github()

    if new_video_link:
        for match in matches:
            home_name = match['home']['name']
            away_name = match['away']['name']

            for new_video_links in new_video_link:
                tag_value = new_video_links["tag"]
                if tag_value == home_name or tag_value == away_name:
                    if new_video_links not in match['video_links']:
                        match['video_links'].insert(0, new_video_links)
                        
        storage_path = os.path.join(os.path.dirname(__file__), '..', '..', 'storage', 'app', 'data', 'scrape.json')
        with open('scrape.json', 'w') as json_file:
            json.dump(matches, json_file, indent=4)
