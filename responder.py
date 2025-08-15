import nodriver as uc
import os
from dotenv import load_dotenv
import time
from logger import logger

load_dotenv()

async def automatic_respond(url: str | None):
    browser = await uc.start(headless=True)
    page = await browser.get('https://www.roommatch.nl/portal/sso/frontend/start')
    email = await page.find("input[name=loginName]")
    if not email:
        logger.error("Email input field not found")
        return

    logger.info('filling in the "email" input field')
    await email.send_keys(os.getenv("LOGIN_EMAIL")) # type: ignore
    next_button = await page.find("Next")
    if not next_button:
        logger.error("Next button not found")
        return
    
    logger.info('clicking the "Next" button')
    await next_button.click()

    logger.info("finding the password field")
    password = await page.find("input[id=password]")
    if not password:
        logger.error("Password input field not found")
        return

    logger.info('filling in the "password" input field')
    await password.send_keys(os.getenv("LOGIN_PASSWORD")) # type: ignore
    
    next_button = await page.find("Next")
    if not next_button:
        logger.error("Next button not found")
        return
    
    logger.info('clicking the "Next" button')
    await next_button.click()
    await page
    time.sleep(3)
    logger.info("Going to the listings page")

    #listing_link = await page.find("a[ng-href=/aanbod/studentenwoningen/details/119627-omegaplantsoen-800-k1-leiden]")
    #await listing_link.click() # type: ignore
    if url:
        await page.get(url)
    else:
        await page.get('https://www.roommatch.nl/aanbod/studentenwoningen/details/113848-rijswijkseweg-340-22-denhaag')

    logger.info("responding to the listing")
    respond_button = await page.find("input[value=Reageer]")
    if not respond_button:
        logger.error("Respond button not found")
        return

    logger.info('clicking the "Respond" button')
    await respond_button.click()
    time.sleep(2)  # Wait for the response to be sent

    browser.stop()
     

if __name__ == '__main__':
    uc.loop().run_until_complete(automatic_respond(None))