
import asyncio
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

mcp = FastMCP("israel")
FORECAST_URL = "https://www.weather2day.co.il/forecast"

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    async def ensure_page(self):
        if self.page is None or self.browser is None:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=False)
            context = await self.browser.new_context(ignore_https_errors=True)
            self.page = await context.new_page()
            await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # אם אנחנו לא בדף הבית וגם לא בדף תחזית ספציפי, נחזור לדף הבית
        if self.page.url == "about:blank":
            await self.page.goto(FORECAST_URL, wait_until="domcontentloaded")
            await asyncio.sleep(2)
        return self.page

browser_mgr = BrowserManager()

@mcp.tool()
async def open_weather_forecast_israel() -> str:
    """פותח את אתר מזג האוויר"""
    await browser_mgr.ensure_page()
    return "SUCCESS: האתר פתוח. כעת המשך ל-enter_weather_forecast_city_israel."

@mcp.tool()
async def enter_weather_forecast_city_israel(city_name: str) -> str:
    """מזין שם עיר ומנקה חיפושים קודמים"""
    page = await browser_mgr.ensure_page()
    search_selector = "#city_search_forecast"
    
    try:
        # ודוא שהגענו לדף החיפוש לפני ההקלדה
        if "forecast" not in page.url:
            await page.goto(FORECAST_URL)

        await page.wait_for_selector(search_selector, timeout=10000)
        await page.click(search_selector, click_count=3)
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Backspace")
        
        await page.type(search_selector, city_name, delay=150)
        await asyncio.sleep(2) # זמן לרשימה להיפתח
        return f"SUCCESS: העיר '{city_name}' הוזנה. כעת חובה להשתמש ב-select_weather_forecast_city_israel."
    except Exception as e:
        return f"ERROR: הזנת העיר נכשלה: {str(e)}"

@mcp.tool()
async def select_weather_forecast_city_israel() -> str:
    """בוחר את העיר וממתין לטעינת הדף החדש"""
    page = await browser_mgr.ensure_page()
    item_selector = ".autocomplete-items div, .autocomplete-suggestion"
    
    try:
        # המתנה שהרשימה תהיה גלויה
        await page.wait_for_selector(item_selector, timeout=7000)
        
        # לחיצה והמתנה לניווט לדף החדש
        async with page.expect_navigation(wait_until="networkidle", timeout=15000):
            await page.click(item_selector)
            
        return "SUCCESS: העיר נבחרה והדף החדש נטען בהצלחה."
    except:
        # גיבוי במקרה שהניווט לא זוהה או שהרשימה לא הגיבה
        await page.keyboard.press("Enter")
        await asyncio.sleep(3)
        return "SUCCESS: בוצע ניסיון בחירה (Enter). בדוק אם הדף השתנה."




@mcp.tool()
async def get_weather_page_content() -> str:
    """שלב 4: מחלץ את נתוני התחזית מהדף עבור המודל"""
    page = await browser_mgr.ensure_page()
    try:
        # המתנה שהאלמנט המרכזי של התחזית יופיע
        await page.wait_for_selector("body", timeout=10000)
        
        # חילוץ טקסט נקי
        raw_text = await page.inner_text("body")
        clean_text = "\n".join([l.strip() for l in raw_text.split('\n') if l.strip()])
        
        # מחזירים רק את ה-4000 תווים הראשונים (מספיק לתחזית)
        return f"--- תכולת דף התחזית ---\n{clean_text[:4000]}\n--- סוף תכולה ---"
    except Exception as e:
        return f"ERROR: לא הצלחתי לקרוא את התוכן: {str(e)}"





if __name__ == "__main__":
    mcp.run(transport="stdio")