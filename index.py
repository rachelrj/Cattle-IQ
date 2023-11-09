from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import os
import importlib

def run_scrapes():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')

    # Use locally to connect to hub
    hub_url = "http://localhost:4444/wd/hub"

    # Use within container to connect to hub
    # hub_url = "http://selenium_hub:4444/wd/hub"

    # Use Remote WebDriver with options
    driver = webdriver.Remote(command_executor=hub_url, options=options)

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
