import { chromium, Locator, Page } from "playwright";
import * as fs from "node:fs";
import * as path from "node:path";
import { humanType, humanPause, humanScroll, randomDelay } from "./humanmode.js";
const __dirname = path.dirname(new URL(import.meta.url).pathname);
const COOKIE_PATH = path.join(__dirname, "..", "data", "cookies.json");
const LOG_DIR = path.join(__dirname, "..", "data", "logs");
const caption = "Ta đi tìm Phật. Cái ta gặp lại là Bản Ngã.";
const imagePath = "/root/.openclaw/workspace/facebook-automato-humanmode/assets/post-images/blacknacha-art-1.jpg";
async function shot(page: Page, name: string){ const out=path.join(LOG_DIR, `${name}-${Date.now()}.png`); await page.screenshot({path:out,fullPage:false}); console.log(`SCREENSHOT=${out}`); return out; }
async function humanClickLocator(page: Page, loc: Locator, label: string){
  await loc.scrollIntoViewIfNeeded({timeout:10000}).catch(()=>{});
  const box = await loc.boundingBox({timeout:10000});
  if (!box) throw new Error(`No box for ${label}`);
  const x = box.x + box.width*(0.35+Math.random()*0.3), y = box.y + box.height*(0.35+Math.random()*0.3);
  await page.mouse.move(x-80+Math.random()*30, y-40+Math.random()*20, {steps: 12});
  await randomDelay(180,420);
  await page.mouse.move(x,y,{steps:8}); await randomDelay(120,280); await page.mouse.click(x,y);
  console.log(`HUMAN_CLICK=${label}`);
}
async function main(){
 const browser=await chromium.launch({headless:true,args:["--no-sandbox","--disable-blink-features=AutomationControlled"]});
 const context=await browser.newContext({viewport:{width:1366,height:900},locale:"vi-VN",timezoneId:"Asia/Ho_Chi_Minh",userAgent:"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"});
 await context.addInitScript(() => { Object.defineProperty(navigator, "webdriver", { get: () => undefined }); });
 await context.addCookies(JSON.parse(fs.readFileSync(COOKIE_PATH,"utf-8")));
 const page=await context.newPage();
 try{
  await page.goto("https://www.facebook.com/",{waitUntil:"domcontentloaded",timeout:45000}); await randomDelay(5000,7000);
  if (page.url().includes('login')) throw new Error('not logged in');
  await page.keyboard.press('Escape').catch(()=>{});
  await humanPause('read'); await humanScroll(page,{steps:1,minPx:150,maxPx:280,direction:'down'}); await humanScroll(page,{steps:1,minPx:120,maxPx:220,direction:'up'});
  await page.evaluate(()=>window.scrollTo(0,0)); await randomDelay(1000,2000);
  const composer = page.getByRole('button', { name: /What\'s on your mind, Blackk\?/ }).first();
  await humanClickLocator(page, composer, 'composer'); await randomDelay(2500,3500);
  await shot(page,'composer-open');
  const textbox = page.locator('div[role="dialog"] div[role="textbox"][contenteditable="true"]').first();
  await textbox.waitFor({state:'visible',timeout:15000});
  await humanType(page, 'div[role="dialog"] div[role="textbox"][contenteditable="true"]', caption);
  await randomDelay(1000,1800);
  let input = page.locator('div[role="dialog"] input[type="file"]').first();
  if (await input.count() === 0) {
    const photo = page.locator('div[role="dialog"] [aria-label*="Photo"], div[role="dialog"] [aria-label*="Ảnh"], div[role="dialog"] span:has-text("Photo/video"), div[role="dialog"] span:has-text("Ảnh/video")').first();
    await humanClickLocator(page, photo, 'photo'); await randomDelay(1200,2000);
    input = page.locator('div[role="dialog"] input[type="file"]').first();
  }
  await input.setInputFiles(imagePath); console.log('IMAGE_SET');
  await page.waitForTimeout(12000);
  await shot(page,'before-final-click');
  // pick visible enabled Post button in dialog, prefer last text Post if multiple
  const buttons = page.locator('div[role="dialog"] div[role="button"]:has-text("Post"), div[role="dialog"] [aria-label="Post"], div[role="dialog"] div[role="button"]:has-text("Đăng"), div[role="dialog"] [aria-label="Đăng"]');
  const n = await buttons.count(); console.log('POST_BUTTONS='+n);
  let clicked=false;
  for (let i=n-1;i>=0;i--){
    const b=buttons.nth(i); if (!(await b.isVisible().catch(()=>false))) continue;
    const ariaDisabled = await b.getAttribute('aria-disabled').catch(()=>null);
    const disabled = await b.getAttribute('disabled').catch(()=>null);
    console.log(`BTN ${i} ariaDisabled=${ariaDisabled} disabled=${disabled}`);
    if (ariaDisabled==='true' || disabled!==null) continue;
    await humanClickLocator(page,b,`post-${i}`); clicked=true; break;
  }
  if(!clicked) throw new Error('No enabled Post button clicked');
  await page.waitForTimeout(18000);
  const after = await shot(page,'after-final-click');
  const body = await page.locator('body').innerText().catch(()=>"");
  console.log(JSON.stringify({done:true, after, hasCaptionOnPage: body.includes(caption), url: page.url()},null,2));
 } finally { await browser.close(); }
}
main().catch(e=>{console.error('POST_VERIFY_ERROR',e);process.exit(1)});
