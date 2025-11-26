import os
import time
import random
from playwright.async_api import async_playwright
import asyncio

LOGIN_CREDENTIALS = {
    "x": {"username": os.getenv("X_USERNAME"), "password": os.getenv("X_PASSWORD")},
    "instagram": {"username": os.getenv("INSTAGRAM_USERNAME"), "password": os.getenv("INSTAGRAM_PASSWORD")}
}

PLATFORM_CONFIG = {
    "x": {
        "login_url": "https://twitter.com/login",
        "profile_url": "https://twitter.com/{}",
        "post_selector": "[data-testid='tweet']"
    },
    "instagram": {
        "login_url": "https://www.instagram.com/accounts/login/",
        "profile_url": "https://www.instagram.com/{}",
        "post_selector": "article"
    },
    "linkedin": {
        "login_url": "https://www.linkedin.com/login",
        "profile_url": "https://www.linkedin.com/in/{}",
        "post_selector": ".feed-shared-update-v2"
    }
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"

async def scrape_profile(platform, username, deep_scan=True):
    config = PLATFORM_CONFIG.get(platform)
    credentials = LOGIN_CREDENTIALS.get(platform, {})
    
    if not username or not config:
        return {"error": f"{platform.capitalize()} için tarama yapılandırması eksik."}

    auth_file = f"{platform}_auth_state.json"
    target_url = config["profile_url"].format(username)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = None

        if os.path.exists(auth_file):
            print(f"Kayıtlı oturum ({platform}) bulundu, kullanılıyor...")
            context = await browser.new_context(storage_state=auth_file, user_agent=USER_AGENT, viewport={'width': 1920, 'height': 1080})
        else:
            print("Kayıtlı oturum bulunamadı, yeni giriş yapılacak...")
            context = await browser.new_context(user_agent=USER_AGENT, viewport={'width': 1920, 'height': 1080})

        page = await context.new_page()

        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(random.uniform(2000, 4000))
            
            is_login_needed = "login" in page.url or await page.locator("a[href*='login']").is_visible()

            if is_login_needed and not os.path.exists(auth_file):
                if not credentials.get('username'):
                     return {"error": f"{platform.capitalize()} için giriş gerekli ancak .env bilgileri eksik."}

                print(f"{platform.capitalize()} için giriş yapılıyor...")
                await page.goto(config["login_url"])
                
                if platform == "instagram":
                    await page.locator("[name='username']").fill(credentials['username'])
                    await page.locator("[name='password']").fill(credentials['password'])
                    await page.locator("button[type='submit']").click()
                elif platform == "x":
                    await page.locator("[name='text']").fill(credentials['username'])
                    await page.locator("text=Next").click()
                    await page.locator("[name='password']").fill(credentials['password'])
                    await page.locator("[data-testid='LoginForm_Login_Button']").click()
                
                await page.wait_for_timeout(5000) 
                print("Giriş işlemi tamamlandı, oturum kaydediliyor...")
                await context.storage_state(path=auth_file)
                await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(random.uniform(2000, 4000))
            
            print(f"Profil içeriği taranıyor ({platform})...")
            
            # HTML Elementlerinden Veri Çekme (Hibrid Yapı)
            scraped_texts = []
            
            # 1. Biyografi vb.
            body_text = await page.locator('body').inner_text()
            scraped_texts.append(body_text[:1000]) # İlk 1000 karakter genel bilgi

            # 2. Gönderiler (Deep Scan veya Default)
            scroll_count = 3 if deep_scan else 1
            for i in range(scroll_count):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(random.uniform(2000, 3500))

            if config.get("post_selector"):
                posts = await page.locator(config["post_selector"]).all()
                for post in posts:
                    scraped_texts.append(await post.inner_text())

            final_text = "\n\n".join(scraped_texts)
            
            if not final_text:
                return {"data": None, "error": "Profilde veri bulunamadı veya gizli."}
            
            return {"platform": platform, "username": username, "data": final_text, "error": None}

        except Exception as e:
            return {"error": f"Tarama sırasında hata: {str(e)}"}
        finally:
            await browser.close()

async def run_concurrent_scraping(usernames_dict, deep_scan=True):
    tasks = []
    for platform, username in usernames_dict.items():
        if username:
            tasks.append(scrape_profile(platform, username, deep_scan))
    results = await asyncio.gather(*tasks)
    return results
