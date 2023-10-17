const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");

// Consts ...
const SCREENSHOTS_PATH = path.join(__dirname, "screenshots");

async function getSameDomainUrls(hostname, pageUrls) {
  return new Set(pageUrls.filter((pageUrl) => (new URL(pageUrl)).hostname.replace('www.', '') == hostname));
}

async function takeScreenshot(page, uuid, i) {
  const screenshotPath = path.join(SCREENSHOTS_PATH, uuid, `${i}.jpg`);
  await page.screenshot({ path: screenshotPath, type: "jpeg" });
  console.log(`New Screenshot: ${i}.jpg`);
}

async function takeScreenshots(page, startUrl, uuid, countTodoScreenshots) {
  const hostname = (new URL(startUrl)).hostname.replace('www.', '');
  
  let i = 0;
  let urls = [startUrl];
  let visitedPages = new Set();
  while(true) {
    // We reached the end / or we ran out of same-domain pages
    if((i >= countTodoScreenshots) || (urls[i] == null))
      break
    
    // Get page url and confirm it wasn't visited before
    let url = urls[i];
    if(visitedPages.has(url))
      continue

    // Goto new page -> Snap new screenshot ...
    console.log(`\nGo & Snap ${i}: ${url}`);
    // Timeout = 0 is a bit risky / in the real world this part will be more advanced !
    await page.goto(url, {waitUntil: 'networkidle0', timeout: 0});
    await takeScreenshot(page, uuid, i);
    visitedPages.add(url);
    i++;
    
    // Reuse already fetched page to collect more urls /if needed/
    let pageUrls = await page.$$eval('a', as => as.map(a => a.href.split("#")[0]));
    console.log(pageUrls);
    urls = [...new Set([...urls, ...await getSameDomainUrls(hostname, pageUrls)])];
  }
}

// Main ...
async function main() {
  try {
    fs.mkdirSync(SCREENSHOTS_PATH);
  } catch(err) {
    if(err.code != 'EEXIST')
      console.error("Cannot create 'screenshots' folder: ", err);
  }

  // Production:
  const uuid = process.argv[2];
  const startUrl = process.argv[3];
  const numberOfLinks = process.argv[4];

  // Development:
  // const getRandomInt = (max) => Math.floor(Math.random() * max);
  // const uuid = 'fake_uuid_' + getRandomInt(100000);
  // const startUrl = "https://www.edited.com/";
  // const numberOfLinks = 3;
  // console.log('UUID: ', uuid);

  // Create subfolder for each uuid process
  await fs.mkdir(path.join(SCREENSHOTS_PATH, uuid), (err) => {
    if(err)
      console.error(`Cannot create UUID folder for ${uuid}: `, err);
  });

  // Init Browser and Page
  const browser = await puppeteer.launch({
    headless: "new",
    args: ['--no-sandbox', "--disable-setuid-sandbox"],
    'ignoreHTTPSErrors': true
  });
  const page = await browser.newPage();

  await takeScreenshots(page, startUrl, uuid, numberOfLinks)
    .then(() => console.log("\nScreenshots taken successfully"))
    .catch((err) => console.error("\nError taking screenshots: ", err));

  await page.close();
  await browser.close();
}
main();