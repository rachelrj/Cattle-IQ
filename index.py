from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
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
    time.sleep(300)

    options = webdriver.FirefoxOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')

    # Use locally to connect to hub
    # Use on AWS container to connect to hub
    hub_url = "http://localhost:4444/wd/hub"

    # Use within docker local container to connect to hub
    # hub_url = "http://selenium_hub:4444/wd/hub"

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
