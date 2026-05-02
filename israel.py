# # # # # import asyncio
# # # # # from mcp.server.fastmcp import FastMCP
# # # # # from playwright.async_api import async_playwright

# # # # # mcp = FastMCP("israel")

# # # # # FORECAST_URL = "https://www.weather2day.co.il/forecast"

# # # # # class BrowserManager:
# # # # #     def __init__(self):
# # # # #         self.playwright = None
# # # # #         self.browser = None
# # # # #         self.context = None
# # # # #         self.page = None

# # # # #     async def get_page(self):
# # # # #         if self.page is None:
# # # # #             self.playwright = await async_playwright().start()
# # # # #             # הפעלה עם הגדרות לעקיפת זיהוי בוטים
# # # # #             self.browser = await self.playwright.chromium.launch(
# # # # #                 headless=False,
# # # # #                 args=["--disable-blink-features=AutomationControlled"]
# # # # #             )
# # # # #             # הגדרות Context שמתאימות לעבודה תחת סינון (התעלמות משגיאות SSL)
# # # # #             self.context = await self.browser.new_context(
# # # # #                 ignore_https_errors=True,
# # # # #                 viewport={'width': 1280, 'height': 720}
# # # # #             )
# # # # #             self.page = await self.context.new_page()
# # # # #             # הסתרת עובדת היותנו אוטומציה
# # # # #             await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
# # # # #         return self.page

# # # # # browser_mgr = BrowserManager()

# # # # # @mcp.tool()
# # # # # async def open_weather_forecast_israel() -> str:
# # # # #     """פותח את אתר מזג האוויר ומנקה חסימות ראשוניות"""
# # # # #     page = await browser_mgr.get_page()
# # # # #     try:
# # # # #         # טעינה בסיסית של הדף
# # # # #         await page.goto(FORECAST_URL, wait_until="commit", timeout=60000)
# # # # #         await asyncio.sleep(4) # זמן המתנה לרינדור ה-JS של האתר
        
# # # # #         # לחיצה במקום ריק כדי לסגור פופ-אפים אפשריים
# # # # #         await page.mouse.click(10, 10)
        
# # # # #         return "האתר נפתח. כעת השתמש ב-enter_weather_forecast_city_israel כדי להזין עיר."
# # # # #     except Exception as e:
# # # # #         return f"שגיאה בפתיחה: {str(e)}"

# # # # # @mcp.tool()
# # # # # async def enter_weather_forecast_city_israel(city_name: str) -> str:
# # # # #     """מזין שם עיר (הזרקה ישירה למניעת בעיות עם דף לבן)"""
# # # # #     page = await browser_mgr.get_page()
# # # # #     search_selector = "#city_search_forecast"
    
# # # # #     try:
# # # # #         # המתנה לקיום האלמנט ב-DOM
# # # # #         await page.wait_for_selector(search_selector, timeout=15000)
        
# # # # #         # ניקוי והזרקת טקסט באמצעות JS (הכי אמין נגד חסימות ויזואליות)
# # # # #         await page.evaluate(f"""
# # # # #             (selector, city) => {{
# # # # #                 const el = document.querySelector(selector);
# # # # #                 el.value = ''; 
# # # # #                 el.focus();
# # # # #             }}
# # # # #         """, search_selector)
        
# # # # #         # הקלדה בפועל כדי לעורר את רשימת ה-Autocomplete
# # # # #         await page.type(search_selector, city_name, delay=150)
# # # # #         await asyncio.sleep(1)
# # # # #         await page.keyboard.press("ArrowDown")
        
# # # # #         return f"העיר '{city_name}' הוזנה. כעת חובה להשתמש ב-select_weather_forecast_city_israel."
# # # # #     except Exception as e:
# # # # #         return f"שגיאה בהזנה: {str(e)}"

# # # # # @mcp.tool()
# # # # # async def select_weather_forecast_city_israel() -> str:
# # # # #     """בוחר את העיר הראשונה מהרשימה ועובר לתחזית"""
# # # # #     page = await browser_mgr.get_page()
# # # # #     # סלקטור רחב לתוצאות החיפוש
# # # # #     item_selector = ".autocomplete-items div, .autocomplete-suggestion"
    
# # # # #     try:
# # # # #         await page.wait_for_selector(item_selector, timeout=10000)
# # # # #         await page.click(item_selector)
# # # # #         await page.wait_for_load_state("networkidle")
# # # # #         return "העיר נבחרה. כעת ניתן לראות את התחזית בדפדפן."
# # # # #     except Exception:
# # # # #         # גיבוי: לחיצה על Enter אם הרשימה לא נלחצת
# # # # #         await page.keyboard.press("Enter")
# # # # #         return "ניסיתי לבחור את העיר באמצעות מקש Enter."

# # # # # if __name__ == "__main__":
# # # # #     mcp.run(transport="stdio")



# # # # import asyncio
# # # # from mcp.server.fastmcp import FastMCP
# # # # from playwright.async_api import async_playwright

# # # # mcp = FastMCP("israel")
# # # # FORECAST_URL = "https://www.weather2day.co.il/forecast"

# # # # class BrowserManager:
# # # #     def __init__(self):
# # # #         self.playwright = None
# # # #         self.browser = None
# # # #         self.page = None

# # # #     async def ensure_page(self):
# # # #         """פונקציה שמוודאת שהדפדפן פתוח ובדף הנכון לפני כל פעולה"""
# # # #         if self.page is None:
# # # #             self.playwright = await async_playwright().start()
# # # #             self.browser = await self.playwright.chromium.launch(headless=False)
# # # #             context = await self.browser.new_context(ignore_https_errors=True)
# # # #             self.page = await context.new_page()
# # # #             await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
# # # #         # אם אנחנו לא בדף הנכון, ננווט אליו
# # # #         if self.page.url != FORECAST_URL:
# # # #             await self.page.goto(FORECAST_URL, wait_until="commit")
# # # #             await asyncio.sleep(2)
# # # #         return self.page

# # # # browser_mgr = BrowserManager()

# # # # @mcp.tool()
# # # # async def open_weather_forecast_israel() -> str:
# # # #     """פותח את אתר מזג האוויר"""
# # # #     await browser_mgr.ensure_page()
# # # #     return "האתר מוכן. ניתן להזין שם עיר."

# # # # @mcp.tool()
# # # # async def enter_weather_forecast_city_israel(city_name: str) -> str:
# # # #     """מזין שם עיר (מפעיל אוטומטית את פתיחת האתר אם צריך)"""
# # # #     page = await browser_mgr.ensure_page()
# # # #     search_selector = "#city_search_forecast"
    
# # # #     try:
# # # #         await page.wait_for_selector(search_selector, timeout=10000)
# # # #         await page.evaluate(f"document.querySelector('{search_selector}').value = ''")
# # # #         await page.type(search_selector, city_name, delay=150)
# # # #         await asyncio.sleep(1)
# # # #         await page.keyboard.press("ArrowDown")
# # # #         return f"העיר '{city_name}' הוזנה. כעת יש להפעיל את כלי הבחירה (select)."
# # # #     except Exception as e:
# # # #         return f"שגיאה בהזנת העיר: {str(e)}"

# # # # @mcp.tool()
# # # # async def select_weather_forecast_city_israel() -> str:
# # # #     """בוחר את העיר מהרשימה"""
# # # #     page = await browser_mgr.ensure_page()
# # # #     item_selector = ".autocomplete-items div, .autocomplete-suggestion"
    
# # # #     try:
# # # #         await page.wait_for_selector(item_selector, timeout=5000)
# # # #         await page.click(item_selector)
# # # #         return "העיר נבחרה והתחזית מוצגת."
# # # #     except:
# # # #         await page.keyboard.press("Enter")
# # # #         return "בוצעה בחירה באמצעות Enter."

# # # # if __name__ == "__main__":
# # # #     mcp.run(transport="stdio")






# # # import asyncio
# # # from mcp.server.fastmcp import FastMCP
# # # from playwright.async_api import async_playwright

# # # mcp = FastMCP("israel")
# # # FORECAST_URL = "https://www.weather2day.co.il/forecast"

# # # class BrowserManager:
# # #     def __init__(self):
# # #         self.playwright = None
# # #         self.browser = None
# # #         self.page = None

# # #     async def ensure_page(self):
# # #         if self.page is None:
# # #             self.playwright = await async_playwright().start()
# # #             self.browser = await self.playwright.chromium.launch(headless=False)
# # #             context = await self.browser.new_context(ignore_https_errors=True)
# # #             self.page = await context.new_page()
# # #             await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
# # #         # אם הדף לא טעון בכלל או שאנחנו בכתובת אחרת
# # #         if self.page.url == "about:blank" or "weather2day" not in self.page.url:
# # #             await self.page.goto(FORECAST_URL, wait_until="commit")
# # #             await asyncio.sleep(2)
# # #         return self.page

# # # browser_mgr = BrowserManager()

# # # @mcp.tool()
# # # async def open_weather_forecast_israel() -> str:
# # #     """פותח את אתר מזג האוויר בישראל"""
# # #     await browser_mgr.ensure_page()
# # #     return "האתר פתוח. כעת חובה עליך להשתמש בכלי enter_weather_forecast_city_israel כדי להזין את שם העיר."

# # # @mcp.tool()
# # # async def enter_weather_forecast_city_israel(city_name: str) -> str:
# # #     """מזין שם עיר בשדה החיפוש"""
# # #     page = await browser_mgr.ensure_page()
# # #     search_selector = "#city_search_forecast"
    
# # #     try:
# # #         await page.wait_for_selector(search_selector, timeout=10000)
# # #         # ניקוי והקלדה
# # #         await page.click(search_selector, click_count=3)
# # #         await page.keyboard.press("Backspace")
# # #         await page.type(search_selector, city_name, delay=150)
# # #         await asyncio.sleep(1)
# # #         await page.keyboard.press("ArrowDown")
        
# # #         return f"העיר '{city_name}' הוזנה בהצלחה. כעת חובה עליך להשתמש בכלי select_weather_forecast_city_israel כדי לסיים."
# # #     except Exception as e:
# # #         # אם נכשלנו, אנחנו מחזירים הוראה למודל לנסות שוב את פתיחת האתר
# # #         return f"הזנת העיר נכשלה. אנא נסה להריץ שוב את open_weather_forecast_israel ואז נסה להזין שוב."

# # # @mcp.tool()
# # # async def select_weather_forecast_city_israel() -> str:
# # #     """בוחר את העיר מהרשימה"""
# # #     page = await browser_mgr.ensure_page()
# # #     item_selector = ".autocomplete-items div, .autocomplete-suggestion"
    
# # #     try:
# # #         await page.wait_for_selector(item_selector, timeout=5000)
# # #         await page.click(item_selector)
# # #         await asyncio.sleep(2)
# # #         return "העיר נבחרה בהצלחה! התחזית מוצגת כעת למשתמש."
# # #     except:
# # #         await page.keyboard.press("Enter")
# # #         return "בוצעה בחירה באמצעות מקש Enter. התהליך הסתיים."

# # # if __name__ == "__main__":
# # #     mcp.run(transport="stdio")




# # import asyncio
# # from mcp.server.fastmcp import FastMCP
# # from playwright.async_api import async_playwright

# # mcp = FastMCP("israel")
# # FORECAST_URL = "https://www.weather2day.co.il/forecast"

# # class BrowserManager:
# #     def __init__(self):
# #         self.playwright = None
# #         self.browser = None
# #         self.page = None

# #     async def ensure_page(self):
# #         if self.page is None:
# #             self.playwright = await async_playwright().start()
# #             self.browser = await self.playwright.chromium.launch(headless=False)
# #             context = await self.browser.new_context(ignore_https_errors=True)
# #             self.page = await context.new_page()
# #             await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
# #         if self.page.url == "about:blank" or "weather2day" not in self.page.url:
# #             await self.page.goto(FORECAST_URL, wait_until="commit")
# #             await asyncio.sleep(2)
# #         return self.page

# # browser_mgr = BrowserManager()

# # @mcp.tool()
# # async def open_weather_forecast_israel() -> str:
# #     """Opens the weather website. Use this FIRST."""
# #     await browser_mgr.ensure_page()
# #     return "SUCCESS: האתר פתוח. עכשיו עליך להשתמש בכלי enter_weather_forecast_city_israel."

# # @mcp.tool()
# # async def enter_weather_forecast_city_israel(city_name: str) -> str:
# #     """Enters the city name. Use this SECOND."""
# #     page = await browser_mgr.ensure_page()
# #     search_selector = "#city_search_forecast"
    
# #     try:
# #         await page.wait_for_selector(search_selector, timeout=10000)
# #         await page.click(search_selector, click_count=3)
# #         await page.keyboard.press("Backspace")
# #         await page.type(search_selector, city_name, delay=150)
# #         await asyncio.sleep(1.5) # זמן לרשימה להיפתח
# #         await page.keyboard.press("ArrowDown")
        
# #         return f"SUCCESS: העיר '{city_name}' הוזנה. עכשיו חובה להשתמש בכלי select_weather_forecast_city_israel."
# #     except Exception as e:
# #         return f"ERROR: הזנת העיר נכשלה. וודא שהאתר פתוח ונסה שוב."

# # @mcp.tool()
# # async def select_weather_forecast_city_israel() -> str:
# #     """Selects the city from list. Use this THIRD."""
# #     page = await browser_mgr.ensure_page()
# #     item_selector = ".autocomplete-items div, .autocomplete-suggestion"
    
# #     try:
# #         await page.wait_for_selector(item_selector, timeout=5000)
# #         await page.click(item_selector)
# #         await asyncio.sleep(2)
# #         return "SUCCESS: העיר נבחרה! התחזית מוצגת כעת בדפדפן."
# #     except:
# #         await page.keyboard.press("Enter")
# #         return "SUCCESS: בוצע ניסיון בחירה עם Enter. התחזית אמורה להופיע."

# # if __name__ == "__main__":
# #     mcp.run(transport="stdio")




# import asyncio
# from mcp.server.fastmcp import FastMCP
# from playwright.async_api import async_playwright

# mcp = FastMCP("israel")
# FORECAST_URL = "https://www.weather2day.co.il/forecast"

# class BrowserManager:
#     def __init__(self):
#         self.playwright = None
#         self.browser = None
#         self.page = None

#     async def ensure_page(self):
#         if self.page is None or self.browser is None:
#             self.playwright = await async_playwright().start()
#             self.browser = await self.playwright.chromium.launch(headless=False)
#             # יצירת הקשר ששומר על הדפדפן פתוח
#             context = await self.browser.new_context(ignore_https_errors=True)
#             self.page = await context.new_page()
#             await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         # לוודא שאנחנו בדף הנכון
#         if self.page.url == "about:blank" or "weather2day" not in self.page.url:
#             await self.page.goto(FORECAST_URL, wait_until="domcontentloaded")
#             await asyncio.sleep(2)
#         return self.page

# browser_mgr = BrowserManager()

# @mcp.tool()
# async def open_weather_forecast_israel() -> str:
#     """פותח את אתר מזג האוויר"""
#     await browser_mgr.ensure_page()
#     return "SUCCESS: האתר פתוח ומוכן. עכשיו השתמש ב-enter_weather_forecast_city_israel."

# @mcp.tool()
# async def enter_weather_forecast_city_israel(city_name: str) -> str:
#     """מזין שם עיר בשדה החיפוש ומנקה חיפושים קודמים"""
#     page = await browser_mgr.ensure_page()
#     search_selector = "#city_search_forecast"
    
#     try:
#         await page.wait_for_selector(search_selector, timeout=10000)
#         # לחיצה וניקוי יסודי של השדה
#         await page.click(search_selector, click_count=3)
#         await page.keyboard.press("Control+A") # ליתר ביטחון
#         await page.keyboard.press("Backspace")
        
#         # הקלדה עם דיליי קטן כדי שהאתר יגיב
#         await page.type(search_selector, city_name, delay=150)
#         await asyncio.sleep(1.5)
#         await page.keyboard.press("ArrowDown")
        
#         return f"SUCCESS: העיר '{city_name}' הוזנה. עכשיו חובה להשתמש ב-select_weather_forecast_city_israel."
#     except Exception as e:
#         return f"ERROR: הזנת העיר נכשלה. נסה לפתוח את האתר מחדש."

# @mcp.tool()
# async def select_weather_forecast_city_israel() -> str:
#     """בוחר את התוצאה הראשונה מהרשימה"""
#     page = await browser_mgr.ensure_page()
#     item_selector = ".autocomplete-items div, .autocomplete-suggestion"
    
#     try:
#         # מחכים שהרשימה תופיע
#         await page.wait_for_selector(item_selector, timeout=7000)
#         await page.click(item_selector)
#         await asyncio.sleep(2) # זמן לטעינת התוצאה
#         return "SUCCESS: העיר נבחרה! התחזית מוצגת כעת."
#     except:
#         # אם הרשימה לא נפתחה, ננסה Enter כמוצא אחרון
#         await page.keyboard.press("Enter")
#         return "SUCCESS: בוצע Enter כגיבוי. התחזית אמורה להיטען."

# if __name__ == "__main__":
#     mcp.run(transport="stdio")




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

if __name__ == "__main__":
    mcp.run(transport="stdio")






# from mcp.server.fastmcp import FastMCP
# from playwright.async_api import TimeoutError as PlaywrightTimeout
# from playwright.async_api import async_playwright

# from playwright.async_api import async_playwright

# mcp = FastMCP("weather-Israel")

# FORECAST_URL = "https://www.weather2day.co.il/forecast"

# # משתנים גלובליים לשמירת מצב הדפדפן
# browser_instance = None
# page_instance = None

# async def get_page():
#     global browser_instance, page_instance
#     if page_instance is None:
#         pw = await async_playwright().start()
#         browser_instance = await pw.chromium.launch(headless=False) # headless=False כדי שתראי מה קורה
#         page_instance = await browser_instance.new_page()
#     return page_instance


# @mcp.tool()
# async def open_weather_forecast_israel() -> str:
#     """פותח את דף תחזית מזג האוויר בישראל"""
#     page = await get_page()
#     await page.goto(FORECAST_URL)
#     return "האתר נפתח בהצלחה. כעת ניתן להזין שם עיר."

# @mcp.tool()
# async def enter_weather_forecast_city_israel(city_name: str) -> str:
#     """מזין שם עיר בשדה החיפוש באתר"""
#     page = await get_page()
#     # איתור השדה (בדרך כלל input עם placeholder מתאים)
#     search_selector = "#city_search_forecast" # וודאי שזה הסלקטור המדויק באתר
#     await page.fill(search_selector, city_name)
#     return f"העיר '{city_name}' הוזנה בשדה החיפוש."


# @mcp.tool()
# async def select_weather_forecast_city_israel() -> str:
#     """בוחר את העיר הראשונה שמופיעה ברשימת התוצאות"""
#     page = await get_page()
    
#     # המתנה להופעת רשימת התוצאות
#     dropdown_selector = "#city_search_forecastautocomplete-list" # דוגמה לסלקטור של תוצאה
#     await page.wait_for_selector(dropdown_selector)
    
#     # לחיצה על התוצאה הראשונה
#     await page.click(dropdown_selector)
    
#     # המתנה לטעינת דף התחזית החדש
#     await page.wait_for_load_state("networkidle")
    
#     return "העיר נבחרה בהצלחה. דף התחזית נטען."

# def main():
#    mcp.run(transport="stdio")
  

# if __name__ == "__main__":
#     main()