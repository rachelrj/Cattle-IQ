const express = require('express');
const { Builder, By } = require('selenium-webdriver');

const app = express();
const port = 3000;
app.get('/montanalivestockauction', async (request, response) => {
try {
    const data = await WebScrapingTest();
    response.status(200).json(data);
    } catch (error) {
    response.status(500).json({
        message: 'Server error occurred',
    });
    }
});
app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
});

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

async function WebScrapingTest() {
    let sales = [];

    try {
      driver = await new Builder().forBrowser('chrome').build();
      await driver.get('https://www.montanalivestockauction.com/market-reports');
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
    } finally {
      await driver.quit();
    }
}