import requests 
import json
import logging
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

# Logger config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('my_log_file.log', mode='a'),
        logging.StreamHandler(sys.stdout)  # Optional: also print to console
    ]
)

headers = {
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'en-US,en;q=0.5',
  'cache-control': 'no-cache',
  'content-type': 'application/json; charset=UTF-8',
  'origin': 'https://www.roommatch.nl',
  'pragma': 'no-cache',
  'priority': 'u=1, i',
  'referer': 'https://www.roommatch.nl/',
  'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Linux"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'cross-site',
  'sec-gpc': '1',
  'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
  'x-requested-with': 'XMLHttpRequest'
}

payload = "{\"filters\":{\"$and\":[{\"$and\":[{\"city.id\":{\"$eq\":\"4\"}},{\"municipality.id\":{\"$eq\":\"23\"}},{\"regio.id\":{\"$eq\":\"1\"}}]}]},\"hidden-filters\":{\"$and\":[{\"dwellingType.categorie\":{\"$eq\":\"woning\"}},{\"rentBuy\":{\"$eq\":\"Huur\"}},{\"isExtraAanbod\":{\"$eq\":\"\"}},{\"isWoningruil\":{\"$eq\":\"\"}},{\"$and\":[{\"$or\":[{\"street\":{\"$like\":\"\"}},{\"houseNumber\":{\"$like\":\"\"}},{\"houseNumberAddition\":{\"$like\":\"\"}}]},{\"$or\":[{\"street\":{\"$like\":\"\"}},{\"houseNumber\":{\"$like\":\"\"}},{\"houseNumberAddition\":{\"$like\":\"\"}}]}]}]}}"
url = "https://roommatching-aanbodapi.zig365.nl/api/v1/actueel-aanbod?limit=30&locale=en_GB&page=0&sort=%2BreactionData.aangepasteTotaleHuurprijs"


def save_data(data, filename="scraped_data.json"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False, indent=4))

def load_existing_data(filename="scraped_data.json"):
    """Load existing data from a JSON file."""
    try:
      with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)
    except FileNotFoundError:
        print("No existing data found!")
        return None
  
def get_id_list(data):
    """Extract IDs from the data."""
    return [item['id'] for item in data.get('data', [])]

def check_for_direct_offers(data):
    """Check for direct offers in the listings"""
    direct_offers = []
    for item in data:
        # If its direct offer or registration period or smthing else
        try:
            type = item["model"]["modelCategorie"]["code"]
            if type == "reactiedatum": direct_offers.append(item)
        except (KeyError, TypeError) as e:
            logging.error(f"Key error: {e} in item: {item['id']}")
            continue

    return direct_offers

def build_urls(data):
    """Build URLs to send in the email."""
    base_url = "https://www.roommatch.nl/en/offerings/to-rent/details/"
    urls = []
    for item in data:
        try:
            url = f"{base_url}{item['urlKey']}"
            urls.append(url)
        except KeyError as e:
            logging.error(f"Key error: {e} in item: {item['id']}")
            continue
    return urls

def send_email(sender_email, sender_password, recipient_email, subject, body):
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    # Add body
    msg.attach(MIMEText(body, 'plain'))
    
    # Gmail SMTP configuration
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()  # Enable encryption
    server.login(sender_email, sender_password)
    
    # Send email
    text = msg.as_string()
    server.sendmail(sender_email, recipient_email, text)
    server.quit()
    logging.info(f"Email sent")

def main():
  logger = logging.getLogger()
  response = requests.post(url, headers=headers, data=payload)

  if response.status_code == 200:
      logger.info("Call was successful!")
      data = response.json()
      logger.info(f"Number of listings found: {len(data['data'])}")

      existing_data = load_existing_data()
      if not existing_data:
          save_data(data)
          return
      
      old_ids = get_id_list(existing_data)
      new_ids = get_id_list(data)
      added_ids = [id for id in new_ids if id not in old_ids]

      if added_ids:
          logger.info(f"New listings id's found: {added_ids}")
          # get the listings corresponding to the new ids
          new_data = [item for item in data['data'] if item['id'] in added_ids]
          direct_offers = check_for_direct_offers(new_data)
          url_list = build_urls(direct_offers)

          send_email(
              sender_email=os.getenv('SENDER_EMAIL'),
              sender_password=os.getenv('SENDER_PASSWORD'),
              recipient_email=os.getenv('RECIPIENT_EMAIL'),
              subject="AUTOMATED: ROOM.NL new direct offer",
              body=f"New listings found: {url_list}"
          )

      save_data(data)
  else:
      logger.error(f"Failed to retrieve data. Status code: {response.status_code}")

if __name__ == "__main__":
    main()