import { chromium } from "playwright";
import * as fs from "node:fs";
import * as path from "node:path";
import { humanClick, humanType, humanPause, humanScroll, randomDelay } from "./humanmode.js";

const __dirname = path.dirname(new URL(import.meta.url).pathname);
const COOKIE_PATHS = [
  path.join(__dirname, "..", "data", "cookies.json"),
  "/root/.openclaw/workspace/secrets/facebook/cookies.json",
  "/root/.openclaw/workspace/facebook-data/cookies.json",
];
const LOG_DIR = path.join(__dirname, "..", "data", "logs");
if (!fs.existsSync(LOG_DIR)) fs.mkdirSync(LOG_DIR, { recursive: true });

const caption = process.argv[2] || "";
const imagePath = process.argv[3] || "";
if (!caption.trim()) throw new Error("Missing post text");
if (!imagePath || !fs.existsSync(imagePath)) throw new Error(`Image not found: ${imagePath}`);

function cookiePath(): string {
  const p = COOKIE_PATHS.find(x => fs.existsSync(x));
  if (!p) throw new Error("No Facebook cookies found");
  return p;
}
async function shot(page: any, name: string) {
  const out = path.join(LOG_DIR, name);
  await page.screenshot({ path: out, fullPage: false });
  console.log(`SCREENSHOT=${out}`);
}
async function clickFirst(page: any, selectors: string[], label: string): Promise<string> {
  for (const sel of selectors) {
    try {
      const el = await page.$(sel);
      if (el) { await humanClick(page, sel); return sel; }
    } catch {}
  }
  throw new Error(`Could not click ${label}`);
}

async function main() {
  console.log("HUMANMODE_POST_START");
  const browser = await chromium.launch({ headless: true, args: ["--no-sandbox", "--disable-blink-features=AutomationControlled"] });
  const context = await browser.newContext({
    viewport: { width: 1366, height: 820 },
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    locale: "vi-VN", timezoneId: "Asia/Ho_Chi_Minh",
  });
  await context.addInitScript(() => { Object.defineProperty(navigator, "webdriver", { get: () => undefined }); });
  const cookies = JSON.parse(fs.readFileSync(cookiePath(), "utf-8"));
  await context.addCookies(cookies);
  const page = await context.newPage();
  try {
    await page.goto("https://www.facebook.com/", { waitUntil: "domcontentloaded", timeout: 45000 });
    await randomDelay(3500, 5500);
    if (page.url().includes("login")) throw new Error("Cookie session not logged in");
    await humanPause("read");
    await humanScroll(page, { steps: 2, minPx: 180, maxPx: 420, direction: "down" });
    await humanScroll(page, { steps: 1, minPx: 160, maxPx: 260, direction: "up" });
    await page.evaluate(() => window.scrollTo(0, 0));
    await randomDelay(1200, 2200);

    await clickFirst(page, [
      'div[aria-label*="on your mind"]',
      'div[aria-label*="Bạn đang nghĩ"]',
      'span:has-text("What\'s on your mind")',
      'span:has-text("Bạn đang nghĩ gì")',
      'div[role="button"]:has-text("What\'s on your mind")',
    ], "composer");
    await randomDelay(1800, 2800);

    const textbox = 'div[role="textbox"][contenteditable="true"]';
    await humanType(page, textbox, caption);
    await randomDelay(1200, 2200);

    const fileInput = await page.$('input[type="file"]');
    if (!fileInput) {
      await clickFirst(page, [
        'div[aria-label*="Photo"]', 'div[aria-label*="Ảnh"]', 'span:has-text("Photo/video")', 'span:has-text("Ảnh/video")'
      ], "photo button");
      await randomDelay(1000, 2000);
    }
    const input = await page.$('input[type="file"]');
    if (!input) throw new Error("File input not found");
    await input.setInputFiles(imagePath);
    await randomDelay(6000, 9000);
    await shot(page, `before-blacknacha-post-${Date.now()}.png`);

    await clickFirst(page, [
      'div[aria-label="Post"]', 'div[aria-label="Đăng"]', 'span:has-text("Post")', 'span:has-text("Đăng")'
    ], "post button");
    await randomDelay(8000, 12000);
    await shot(page, `after-blacknacha-post-${Date.now()}.png`);
    console.log("HUMANMODE_POST_DONE");
  } finally {
    await browser.close();
  }
}
main().catch(e => { console.error("HUMANMODE_POST_ERROR", e); process.exit(1); });
