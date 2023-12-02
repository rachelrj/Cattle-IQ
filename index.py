from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import os
import importlib
import time

def run_scrapes():

    # Even though the container with this script waits for selenium_hub
    # and firefox node to be created, it still was erroring out.
    # After I added this time.sleep(300), it started working. 
    # Comment out if testing.
    # TODO: Fix this. Avoid the need to sleep.
    time.sleep(1)

    # Use locally to connect to hub
    # Use on AWS container to connect to hub
    hub_url = "http://localhost:4444/wd/hub"

    # Use within docker local container to connect to hub
    # hub_url = "http://selenium_hub:4444/wd/hub"

    options = webdriver.FirefoxOptions()

    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')

    # Set preferences for file download
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("browser.download.folderList", 2)
    firefox_profile.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_profile.set_preference("browser.download.dir", "/lib")
    firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")

    # Convert Firefox profile to a base64 string and set it in options
    options.set_preference("firefox_profile", firefox_profile.encoded)

    # Initialize and return the Remote WebDriver
    driver = webdriver.Remote(
        command_executor=hub_url,
        options=options
    )

    # Initialize Firefox options
    # options = webdriver.FirefoxOptions()

    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--disable-extensions')


    # firefox_capabilities = DesiredCapabilities.FIREFOX.copy()

    # # Set preferences for file download
    # firefox_profile = webdriver.FirefoxProfile()
    # firefox_profile.set_preference("browser.download.folderList", 2)
    # firefox_profile.set_preference("browser.download.manager.showWhenStarting", False)
    # firefox_profile.set_preference("browser.download.dir", "/lib")
    # firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")

    # # Convert Firefox profile to a base64 string
    # encoded_profile = firefox_profile.encoded
    
    # # Set the encoded Firefox profile in capabilities
    # firefox_capabilities['firefox_profile'] = encoded_profile
    # firefox_capabilities.update(options.to_capabilities())

    # # Initialize and return the Remote WebDriver
    # driver = webdriver.Remote(
    #     command_executor=hub_url,
    #     desired_capabilities=firefox_capabilities
    # )

    # options.set_preference("browser.download.folderList", 2)
    # options.set_preference("browser.download.manager.showWhenStarting", False)
    # options.set_preference("browser.download.dir", download_dir)
    # options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
    # options.set_preference("pdfjs.disabled", True)
    # options.set_preference("dom.disable_beforeunload", True)
    # options.set_preference("browser.helperApps.alwaysAsk.force", False)


    scripts_directory = "scripts"

    script_files = [f for f in os.listdir(scripts_directory) if f.endswith(".py")]

    for script_file in script_files:
        try:
            module_name = script_file[:-3]
            module = importlib.import_module(f"{scripts_directory}.{module_name}")    
            if hasattr(module, "run_scrape"):
                module.run_scrape(driver)
                print("\n\n\n")
        except Exception as error:
            print(str(error))

    driver.quit()

if __name__ == "__main__":
    run_scrapes()
