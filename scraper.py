import requests 
import json
from logger import logger
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from responder import automatic_respond
import nodriver as uc
import time

load_dotenv()


headers = {
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'en-US,en;q=0.5',
  'cache-control': 'no-cache',
  'content-type': 'application/json; charset=UTF-8',
  'origin': 'https://www.roommatch.nl',
  'priority': 'u=1, i',
  'referer': 'https://www.roommatch.nl/',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'cross-site',
  'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
  'x-requested-with': 'XMLHttpRequest'
}

payload = "{\"filters\":{\"$and\":[{\"$or\":[{\"$and\":[{\"city.id\":{\"$eq\":\"4\"}},{\"municipality.id\":{\"$eq\":\"23\"}},{\"regio.id\":{\"$eq\":\"1\"}}]},{\"$and\":[{\"municipality.id\":{\"$eq\":\"22\"}},{\"regio.id\":{\"$eq\":\"1\"}}]}]}]},\"hidden-filters\":{\"$and\":[{\"dwellingType.categorie\":{\"$eq\":\"woning\"}},{\"rentBuy\":{\"$eq\":\"Huur\"}},{\"isExtraAanbod\":{\"$eq\":\"\"}},{\"isWoningruil\":{\"$eq\":\"\"}},{\"$and\":[{\"$or\":[{\"street\":{\"$like\":\"\"}},{\"houseNumber\":{\"$like\":\"\"}},{\"houseNumberAddition\":{\"$like\":\"\"}}]},{\"$or\":[{\"street\":{\"$like\":\"\"}},{\"houseNumber\":{\"$like\":\"\"}},{\"houseNumberAddition\":{\"$like\":\"\"}}]}]}]}}"
url = "https://roommatching-aanbodapi.zig365.nl/api/v1/actueel-aanbod?limit=30&locale=en_GB&page=0&sort=%2BreactionData.aangepasteTotaleHuurprijs"


respond_url = "https://www.roommatch.nl/portal/object/frontend/react/format/json"
respond_payload = "__id__=Portal_Form_SubmitOnly&__hash__=269d047318e4b748f6b6b2e5e81efc5f&add=112276&dwellingID=113114"
respon_headers = {
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'en-US,en;q=0.7',
  'cache-control': 'no-cache',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'origin': 'https://www.roommatch.nl',
  'pragma': 'no-cache',
  'priority': 'u=1, i',
  'referer': 'https://www.roommatch.nl/en/offerings/to-rent/details/113114-leemansplein-420-denhaag',
  'sec-ch-ua': '"Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Linux"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'sec-gpc': '1',
  'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
  'x-requested-with': 'XMLHttpRequest',
  'Cookie': 'klaro=%7B%22other-1%22%3Atrue%2C%22analytical-cookies-3%22%3Atrue%2C%22tracking-cookies-5%22%3Atrue%7D; __Host-PHPSESSID=635531e0b287bd1c8e17f117f18573de; staticfilecache=typo_user_logged_in; backendToken=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImN0eSI6IkpXVCJ9.eyJpYXQiOjE3NTQ4NDg1MzAsImV4cCI6MTc1NDg1NzUzMCwic3ViIjoiem9la2VuZGU6MjAyMTA3MTEwMSIsImF1ZCI6Ind6YSIsImp0aSI6IjUxNTk2ZjUxOTg1OTg5ZWNlYzc3ZmI4OGE5YjBlNzUxOGZjOWRkZTZhYTgxNDVjNTA3OTJjZWIzNzhjODZkNThlNmRiZjIwNzIwZDVkMmZjIiwiaXNzIjoicm9vbW1hdGNoaW5ncHJvZHVjdGllIiwicm9sZXMiOlsiUk9MRV9aSUdfWk9FS0VOREVfVVNFUiJdLCJpZCI6MjAyMTA3MTEwMSwic2NvcGVzIjpbInpvZWtlbmRlIl19.r4hd9bFBuOLbS1dIn7C-VK5aBkMDftic3QQp9L9sz2LOlALsdWVc_ekqF4CO6wHN1a9b0uJcfI3DHImxanSVTvNohgX30SoqrRO6yXqRNZuKt0kA-731Mhb9JiuTE9kLl8JXhigCZji1mH-DG43gIMMbvfKV5QfHqfdE-ZaktlUz2IgveHXYuIxKopV-lPc6itNKA0cj4f3lQ0wb8Q_V9uP48o1BRDIYUx7xmDcjggYU46VU4Q6gAfrl2UO7wQVSvTOCHrLkxwGIyOyWhgvr5xi7B2qe_SCjB6AFh4HycFFpwfqyxorr_QnYOpnS2NyN-wHhQpuHvsHzIOjzd4SE3SypKSZc3R4_kjnHMBEEMiFISx_s5nxbIim84toXcpa2DOnDhVzy15nS-l0uIPSgTArWDI12p3YhM1WdVIZhjzNwIB0LGIAreLa8xqLFj-Z5W9hXneHGSk5V7JJuSbQ-OydLT1wi5WE9XOYlD0Xwfc7Ul0QAN0KyV4ijcZ3AdBv-51hWLUWO68QMJMEXqdlI6QfVD2HE1TIqXqQHH612gAJCjLF4uYWgpPunAvvtl-hVAPrV6XO1SN4qDTMaySaSPcHOekl4OGSNHBnu0LdbnY9F41nTDj44aT8RM0v4XbTp5lnb7ZBwOur17eDlwUax0sIVihMYQgEcruom_99Gh9g; zoekendeId=2021071101; switchUserEnabled=1; zigConversationalJwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6ImFwcF82NTY4YTFjNmUwZWZhZTc3NDJjZTc2MzIifQ.eyJzY29wZSI6InVzZXIiLCJleHRlcm5hbF9pZCI6IjIwMjEwNzExMDEiLCJleHAiOjE3NTQ4NTU3MzAuNjIyOTYyfQ.cZpPCwBdcAAa23denxo-b3kXSdQ0ZYWzB36yPgoEhfM; zigConversationalExternalId=2021071101; fe_typo_user=3399f6ffd84f170ce31e7aaa6584dd85.f63cc66f0f735df98cebc76ff13c5ef947301a86aa4c82a5cd1376540285cff9; portalLocale=en_GB; __cf_bm=defhzVtkPrz.33FTBWkmfh4sacm9ZzVx534fYmrAsrA-1754848566-1.0.1.1-0zlovEkWcB5sdlrmuZRlQSR2PagOhrgebjDaYb3qS1z5mPdT.5tUdmSJbFE6tX1j_bAD.greHwgW3hjQCq7nmBjOo5utAEmLTon5jhaeBzzlmuYqRFuP6rMZWsfa8UYL; __Host-PHPSESSID=c5018e38ba33a652c845015053cbcce5; __cf_bm=spuiTy9SVYYwJK9HRJCZ2S6TCc0IkC8dDs2SAOVyemI-1754848808-1.0.1.1-RdZPr6yvhtLox_JCZywWm.2ou4eehelq7Pe6flcFTamMxWcYmykLa6F1nQ2ICx13ggFqO.9X883dJAF0gS6nMCxIrOp5TcXUwK_p0Tyft5U'
}


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
            logger.error(f"Key error: {e} in item: {item['id']}")
            continue

    return direct_offers

def build_urls(data) -> tuple:
    """Build URLs to send in the email."""
    en_base_url = "https://www.roommatch.nl/en/offerings/to-rent/details/"
    nl_base_url = "https://www.roommatch.nl/aanbod/studentenwoningen/details/"
    en_urls, nl_urls = [], []
    for item in data:
        try:
            en_url, nl_url = f"{en_base_url}{item['urlKey']}", f"{nl_base_url}{item['urlKey']}"
            en_urls.append(en_url)
            nl_urls.append(nl_url)
        except KeyError as e:
            logger.error(f"Key error: {e} in item: {item['id']}")
            continue
    return en_urls, nl_urls

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
    logger.info(f"Email sent")

async def main():
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
            eu_urls, nl_urls = build_urls(direct_offers)

            if eu_urls: 
                send_email(
                    sender_email=os.getenv('SENDER_EMAIL'),
                    recipient_email=os.getenv('RECIPIENT_EMAIL'),
                    sender_password=os.getenv('SENDER_PASSWORD'),
                    subject="AUTOMATED: ROOM.NL new direct offer",
                    body=f"New listings found: {eu_urls}"
                )
            if nl_urls:
                for nl_url in nl_urls:
                    logger.info(f"Responding to listing: {nl_url}")
                    # Call the automatic respond function
                    await automatic_respond(nl_url)
                    time.sleep(1)

        save_data(data)
    else:
        logger.error(f"Failed to retrieve data. Status code: {response.status_code}")

if __name__ == "__main__":
    uc.loop().run_until_complete(main())