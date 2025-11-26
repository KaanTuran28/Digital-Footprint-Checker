import os
import time
import random
from playwright.async_api import async_playwright
import asyncio

# 1. GÜNCELLEME: LinkedIn bilgileri eklendi ve .env kontrolü yapıldı
LOGIN_CREDENTIALS = {
    "x": {
        "username": os.getenv("X_USERNAME"), 
        "password": os.getenv("X_PASSWORD")
    },
    "instagram": {
        "username": os.getenv("INSTAGRAM_USERNAME"), 
        "password": os.getenv("INSTAGRAM_PASSWORD")
    },
    "linkedin": {
        "username": os.getenv("LINKEDIN_USERNAME"), # .env'ye bunu eklemeyi unutmayın
        "password": os.getenv("LINKEDIN_PASSWORD")
    }
}

PLATFORM_CONFIG = {
    "x": {
        "login_url": "https://twitter.com/login",
        "profile_url": "https://twitter.com/{}",
        "post_selector": "[data-testid='tweet']",
        # X girişinde bazen kullanıcı adı bazen e-posta ister
        "username_selector": "input[autocomplete='username']",
        "password_selector": "input[name='password']"
    },
    "instagram": {
        "login_url": "https://www.instagram.com/accounts/login/",
        "profile_url": "https://www.instagram.com/{}",
        "post_selector": "article",
        "username_selector": "input[name='username']",
        "password_selector": "input[name='password']"
    },
    "linkedin": {
        "login_url": "https://www.linkedin.com/login",
        "profile_url": "https://www.linkedin.com/in/{}",
        "post_selector": ".feed-shared-update-v2",
        "username_selector": "#username",
        "password_selector": "#password"
    }
}

# Daha gerçekçi bir User-Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

async def scrape_profile(platform, username, deep_scan=True):
    print(f"--- {platform.upper()} Taraması Başlatılıyor: {username} ---")
    
    config = PLATFORM_CONFIG.get(platform)
    credentials = LOGIN_CREDENTIALS.get(platform, {})
    
    if not username or not config:
        return {"error": f"{platform.capitalize()} için yapılandırma hatası."}

    auth_file = f"{platform}_auth_state.json"
    target_url = config["profile_url"].format(username)

    async with async_playwright() as p:
        # 2. GÜNCELLEME: args parametresi ile bot tespitini zorlaştırıyoruz
        browser = await p.chromium.launch(
            headless=True, # Hata ayıklamak isterseniz bunu False yapın
            args=["--disable-blink-features=AutomationControlled"] 
        )
        
        context = None

        # Kayıtlı oturum kontrolü
        if os.path.exists(auth_file):
            print(f"{platform}: Kayıtlı oturum bulundu.")
            context = await browser.new_context(storage_state=auth_file, user_agent=USER_AGENT, viewport={'width': 1920, 'height': 1080})
        else:
            print(f"{platform}: Yeni oturum açılıyor.")
            context = await browser.new_context(user_agent=USER_AGENT, viewport={'width': 1920, 'height': 1080})

        page = await context.new_page()

        try:
            # Hedef sayfaya git
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(random.uniform(2000, 4000))
            
            # Giriş gerekli mi kontrolü (Login URL'sine yönlendirdi mi veya login butonu var mı?)
            is_login_needed = "login" in page.url or await page.locator("a[href*='login']").is_visible() or await page.locator("input[name='password']").is_visible()

            # Oturum dosyası yoksa veya giriş sayfasına attıysa giriş yap
            if is_login_needed:
                if not credentials.get('username') or not credentials.get('password'):
                     return {"error": f"{platform.capitalize()} için giriş gerekli ancak .env bilgileri eksik."}

                print(f"{platform}: Giriş yapılıyor...")
                
                # Eğer şu an giriş sayfasında değilsek giriş sayfasına git
                if "login" not in page.url:
                    await page.goto(config["login_url"], wait_until="domcontentloaded")
                    await page.wait_for_timeout(3000)

                # PLATFORMA ÖZEL GİRİŞ İŞLEMLERİ
                if platform == "instagram":
                    try:
                        await page.locator(config["username_selector"]).fill(credentials['username'])
                        await page.wait_for_timeout(1000)
                        await page.locator(config["password_selector"]).fill(credentials['password'])
                        await page.wait_for_timeout(1000)
                        await page.locator("button[type='submit']").click()
                    except Exception as e:
                        print(f"Instagram giriş form hatası: {e}")

                elif platform == "x":
                    try:
                        await page.locator(config["username_selector"]).fill(credentials['username'])
                        await page.locator("text=Next").click() # Veya "İleri"
                        await page.wait_for_timeout(2000)
                        
                        # Bazen "Olağandışı etkinlik" deyip kullanıcı adı veya telefon sorabilir, burası takılabilir.
                        # Şifre alanını bekle
                        await page.locator(config["password_selector"]).fill(credentials['password'])
                        await page.locator("[data-testid='LoginForm_Login_Button']").click()
                    except Exception as e:
                        print(f"X giriş form hatası: {e}")

                elif platform == "linkedin":
                    try:
                        await page.locator(config["username_selector"]).fill(credentials['username'])
                        await page.locator(config["password_selector"]).fill(credentials['password'])
                        await page.locator("button[type='submit']").click()
                    except Exception as e:
                        print(f"LinkedIn giriş form hatası: {e}")
                
                # Giriş işleminin tamamlanmasını bekle (ağ trafiği durana kadar)
                await page.wait_for_load_state("networkidle", timeout=30000)
                
                # Başarılı giriş sonrası oturumu kaydet
                print(f"{platform}: Giriş denemesi tamamlandı, oturum kaydediliyor...")
                await context.storage_state(path=auth_file)
                
                # Hedef profile tekrar git
                print(f"{platform}: Hedef profile yönlendiriliyor -> {target_url}")
                await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(random.uniform(3000, 5000))
            
            # VERİ TOPLAMA AŞAMASI
            print(f"{platform}: İçerik taranıyor...")
            
            scraped_texts = []
            
            # 1. Sayfa metnini al (Biyografi vb.)
            try:
                body_text = await page.locator('body').inner_text()
                scraped_texts.append(body_text[:2000]) # Çok uzun olmaması için kısıtla
            except:
                pass

            # 2. Gönderileri Tara (Scroll işlemi)
            scroll_count = 3 if deep_scan else 1
            for i in range(scroll_count):
                print(f"{platform}: Sayfa kaydırılıyor ({i+1}/{scroll_count})...")
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(random.uniform(2000, 4000))

            # Gönderi seçicisi varsa gönderileri topla
            if config.get("post_selector"):
                posts = await page.locator(config["post_selector"]).all()
                print(f"{platform}: {len(posts)} adet gönderi bulundu.")
                for post in posts:
                    try:
                        text = await post.inner_text()
                        if text:
                            scraped_texts.append(text)
                    except:
                        continue

            final_text = "\n\n".join(scraped_texts)
            
            # Eğer veri çok kısaysa (muhtemelen giriş başarısız oldu veya gizli profil)
            if len(final_text) < 50:
                return {"data": None, "error": "Profilde veri bulunamadı. Profil gizli olabilir veya giriş başarısız oldu."}
            
            print(f"{platform}: Tarama başarılı.")
            return {"platform": platform, "username": username, "data": final_text, "error": None}

        except Exception as e:
            print(f"{platform} Genel Hata: {str(e)}")
            return {"error": f"Tarama sırasında hata: {str(e)}"}
        finally:
            await browser.close()

async def run_concurrent_scraping(usernames_dict, deep_scan=True):
    tasks = []
    for platform, username in usernames_dict.items():
        if username:
            tasks.append(scrape_profile(platform, username, deep_scan))
    
    # Tüm görevleri eşzamanlı çalıştır
    if not tasks:
        return []
        
    results = await asyncio.gather(*tasks)
    return results