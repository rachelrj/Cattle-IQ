const { Builder, By, Options, Browser } = require('selenium-webdriver');
const firefox = require('selenium-webdriver/firefox');
const options = new firefox.Options();

async function runScrape() {
    options.addArguments('--no-sandbox')
    options.addArguments('--disable-dev-shm-usage')
    options.addArguments("--disable-extensions")
    let driver = new Builder()
    .setFirefoxOptions(options)
    .forBrowser(Browser.FIREFOX)
    .usingServer('http://localhost:4444/wd/hub')
    .build(); 

    try {
        await driver.get('https://www.montanalivestockauction.com/market-reports');
        const data = await WebScrapingTest(driver);
        console.log(data);
        return data;
    } catch (error) {
            return error;
    } finally {
            await driver.quit();
    }
}

async function getDate(driver) {
    const section = await driver.findElement(By.id("section-content"))
    const text = await section.getText()
    let date = text.match('(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)(.+?)([0-9]{4})')
    if (date && date.length) {
        date = date[0];
    }
    const newDate = new Date(date).toISOString().split('T')[0]
    return newDate;    
}

async function addRows(sales, tbody, calfOrYearling, date) {
    const rows = await tbody.findElements(By.tagName('tr'));
    for (const row of rows) {
        const tds = await row.findElements(By.tagName('td'));
        const seller = await tds[0].getText();
        const head = await tds[1].getText();
        const kind = await tds[2].getText();
        const weight = await tds[3].getText();
        const price = await tds[4].getText();
        const ch = await tds[5].getText();
        const info = {
            "seller": seller,
            "head": head,
            "kind": kind,
            "weight": weight,
            "price": price,
            "unit": ch,
            "calf/yearling": calfOrYearling,
            "date": date
        }
        sales.push(info);
      }
}

async function WebScrapingTest(driver) {
    let sales = [];

    try {
      const date = await getDate(driver);

      const yearlingButton = driver.findElement(By.xpath("//*[text()='YEARLING']"));
      await driver.executeScript("arguments[0].click();", yearlingButton);
      const yearlingTabPanel = await driver.findElement(By.id("yearling"));
      const yearlingtbody = await yearlingTabPanel.findElement(By.tagName('tbody'));
      await addRows(sales, yearlingtbody, "yearling", date);

      const calfButton = driver.findElement(By.xpath("//*[text()='CALF']"));
      await driver.executeScript("arguments[0].click();", calfButton);
      const calfTabPanel = await driver.findElement(By.id("calf"));
      const calftbody = await calfTabPanel.findElement(By.tagName('tbody'));
      await addRows(sales, calftbody, "calf", date);

      return sales;
    } catch (error) {
      console.log(error);
    }
}

runScrape();

