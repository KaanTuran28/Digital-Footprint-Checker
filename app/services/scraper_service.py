import os
import time
import random
import asyncio
from playwright.async_api import async_playwright

# --- 1. AYARLAR VE SABİTLER ---

LOGIN_CREDENTIALS = {
    "instagram": {
        "username": os.getenv("INSTAGRAM_USERNAME"), 
        "password": os.getenv("INSTAGRAM_PASSWORD")
    },
    "x": {
        "username": os.getenv("X_USERNAME"), 
        "password": os.getenv("X_PASSWORD")
    },
    "linkedin": {
        "username": os.getenv("LINKEDIN_USERNAME"), 
        "password": os.getenv("LINKEDIN_PASSWORD")
    }
}

PLATFORM_CONFIG = {
    "instagram": {
        "login_url": "https://www.instagram.com/accounts/login/",
        "profile_url": "https://www.instagram.com/{}",
        "username_selector": "input[name='username']",
        "password_selector": "input[name='password']",
        "submit_selector": "button[type='submit']"
    },
    "x": {
        "login_url": "https://twitter.com/i/flow/login", # Daha doğrudan login linki
        "profile_url": "https://twitter.com/{}",
        # X girişinde sırayla: 1. Kullanıcı Adı -> 2. (Bazen) Email/Tel -> 3. Şifre
        "username_selector": "input[autocomplete='username']",
        "verification_selector": "input[data-testid='ocfEnterTextTextInput']", # Doğrulama kutusu
        "password_selector": "input[name='password']"
    },
    "linkedin": {
        "login_url": "https://www.linkedin.com/login",
        "profile_url": "https://www.linkedin.com/in/{}",
        "username_selector": "#username",
        "password_selector": "#password",
        "submit_selector": "button[type='submit']"
    }
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Yardımcı Fonksiyon: İnsan gibi bekleme
async def human_delay(page, min_s=1.0, max_s=3.0):
    await page.wait_for_timeout(random.uniform(min_s, max_s) * 1000)

# --- 2. INSTAGRAM MODÜLÜ ---
async def scrape_instagram(context, username, deep_scan):
    print(f"📷 Instagram taranıyor: {username}")
    page = await context.new_page()
    scraped_texts = []
    config = PLATFORM_CONFIG["instagram"]
    creds = LOGIN_CREDENTIALS["instagram"]
    target_url = config["profile_url"].format(username)

    try:
        # Profile Git
        await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        await human_delay(page, 2, 4)

        # Giriş Gerekli mi?
        if "login" in page.url or await page.locator("input[name='username']").count() > 0:
            print("📷 Instagram: Giriş yapılıyor...")
            if "login" not in page.url: await page.goto(config["login_url"])
            try:
                await page.locator(config["username_selector"]).fill(creds['username'])
                await human_delay(page, 0.5, 1.5)
                await page.locator(config["password_selector"]).fill(creds['password'])
                await human_delay(page, 0.5, 1.5)
                await page.locator(config["submit_selector"]).click()
                await page.wait_for_load_state("networkidle", timeout=30000)
                
                # Pop-up geçme
                try: await page.get_by_role("button", name="Not Now").click()
                except: pass
                try: await page.get_by_role("button", name="Şimdi Değil").click()
                except: pass
                
                await page.goto(target_url, wait_until="domcontentloaded")
                await human_delay(page, 3, 5)
            except Exception as e:
                print(f"📷 Instagram giriş hatası: {e}")

        # Veri Topla (Biyografi)
        try:
            meta_desc = await page.get_attribute('meta[name="description"]', 'content')
            if meta_desc: scraped_texts.append(f"İSTATİSTİK: {meta_desc}")
            header_text = await page.locator('header').inner_text()
            clean_header = " | ".join([line.strip() for line in header_text.split('\n') if len(line.strip()) > 1])
            scraped_texts.append(f"BİYOGRAFİ: {clean_header}")
        except: pass

        # Veri Topla (Derin Tarama - Gönderi Tıklama)
        if deep_scan:
            print("📷 Instagram: Gönderi detaylarına bakılıyor...")
            try:
                posts = await page.locator('article a[href^="/p/"]').all()
                for i, post in enumerate(posts[:3]): # İlk 3 gönderi
                    try:
                        await post.click()
                        await page.wait_for_selector('div[role="dialog"]', timeout=6000)
                        await human_delay(page, 1, 2)
                        
                        dialog_box = page.locator('div[role="dialog"]')
                        
                        # Konum
                        try:
                            location = await dialog_box.locator('a[href*="/explore/locations/"]').inner_text()
                            scraped_texts.append(f"KONUM: {location}")
                        except: pass

                        # İçerik
                        full_text = await dialog_box.inner_text()
                        clean_text = " ".join([l.strip() for l in full_text.split('\n') if len(l.strip()) > 2]).replace(username, "")
                        scraped_texts.append(f"GÖNDERİ {i+1}: {clean_text[:1000]}")
                        
                        await page.keyboard.press("Escape")
                        await human_delay(page, 1, 2)
                    except: await page.keyboard.press("Escape")
            except Exception as e: print(f"📷 Instagram gönderi hatası: {e}")

        final_text = "\n\n".join(scraped_texts)
        if len(final_text) < 10:
             # Fallback
            try: return {"platform": "instagram", "username": username, "data": (await page.locator('body').inner_text())[:3000], "error": None}
            except: return {"platform": "instagram", "error": "Veri çekilemedi."}

        return {"platform": "instagram", "username": username, "data": final_text, "error": None}

    except Exception as e:
        return {"platform": "instagram", "error": str(e)}
    finally:
        await page.close()

# --- 3. X (TWITTER) MODÜLÜ ---
async def scrape_x(context, username, deep_scan):
    print(f"🐦 X taranıyor: {username}")
    
    # Debug için headless=False yapabilirsiniz, canlı izlemek hatayı bulmayı kolaylaştırır
    # page = await context.new_page() 
    
    # X için özel bir sayfa açıyoruz
    page = await context.new_page()
    
    scraped_texts = []
    config = PLATFORM_CONFIG["x"]
    creds = LOGIN_CREDENTIALS["x"]
    target_url = config["profile_url"].format(username)

    try:
        # Önce Login Olmayı Dene
        print("🐦 X: Giriş sayfasına gidiliyor...")
        await page.goto(config["login_url"], wait_until="domcontentloaded", timeout=60000)
        await human_delay(page, 3, 5)

        # Giriş kutusu var mı?
        if await page.locator(config["username_selector"]).count() > 0:
            print("🐦 X: Giriş yapılıyor...")
            
            # 1. ADIM: Kullanıcı Adını Gir
            await page.locator(config["username_selector"]).fill(creds['username'])
            await page.locator("text=Next").first.click() # Veya "İleri"
            await human_delay(page, 2, 3)

            # 2. ADIM: Doğrulama Kontrolü (KRİTİK KISIM)
            # Bazen "Olağandışı etkinlik" diyip telefon veya e-posta sorar
            # Genellikle data-testid="ocfEnterTextTextInput" olan bir input çıkar
            verification_input = page.locator("input[data-testid='ocfEnterTextTextInput']")
            
            if await verification_input.count() > 0 and await verification_input.is_visible():
                print("🐦 X: Doğrulama istendi, e-posta/telefon giriliyor...")
                # Genelde e-posta veya kullanıcı adı ister. 
                # Buraya .env dosyanızdaki e-postayı veya kullanıcı adını tekrar girmeyi deneyebilirsiniz.
                # Şimdilik kullanıcı adını tekrar deniyoruz, gerekirse .env'ye EMAIL ekleyip onu kullanın.
                await verification_input.fill(creds['username']) 
                await page.locator("text=Next").first.click()
                await human_delay(page, 2, 3)

            # 3. ADIM: Şifre Gir
            if await page.locator(config["password_selector"]).count() > 0:
                await page.locator(config["password_selector"]).fill(creds['password'])
                await page.locator("[data-testid='LoginForm_Login_Button']").click()
                await page.wait_for_load_state("networkidle", timeout=30000)
                print("🐦 X: Giriş başarılı (veya denendi).")
            else:
                print("🐦 X: Şifre ekranı gelmedi, bir sorun olabilir.")

        # Şimdi Hedef Profile Git
        print(f"🐦 X: Hedef profile gidiliyor -> {target_url}")
        await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        await human_delay(page, 4, 6)

        # Hata Kontrolü (Hesap yoksa veya gizliyse)
        if await page.locator("text=This account doesn’t exist").count() > 0:
             return {"platform": "x", "username": username, "data": None, "error": "Hesap bulunamadı."}

        # Biyografi Topla
        try:
            # X bazen data-testid'leri değiştirir, en garantisi UserDescription
            bio_el = page.locator('[data-testid="UserDescription"]')
            if await bio_el.count() > 0:
                bio = await bio_el.inner_text()
                scraped_texts.append(f"BİYOGRAFİ: {bio}")
            
            loc_el = page.locator('[data-testid="UserLocation"]')
            if await loc_el.count() > 0:
                loc = await loc_el.inner_text()
                scraped_texts.append(f"KONUM: {loc}")
                
            # Doğum Tarihi (Varsa)
            birth_el = page.locator('[data-testid="UserBirthdate"]')
            if await birth_el.count() > 0:
                birth = await birth_el.inner_text()
                scraped_texts.append(f"DOĞUM TARİHİ: {birth}")
                
        except Exception as e: 
            print(f"🐦 X Biyografi Hatası: {e}")

        # Tweetler (Deep Scan)
        if deep_scan:
            print("🐦 X: Tweetler taranıyor...")
            try:
                # Sayfayı kaydır
                for _ in range(3):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await human_delay(page, 2, 3)
                
                # Tweet metinlerini topla
                tweets = await page.locator('[data-testid="tweetText"]').all()
                print(f"🐦 X: {len(tweets)} adet tweet bulundu.")
                
                for i, tweet in enumerate(tweets[:7]): # İlk 7 tweet
                    text = await tweet.inner_text()
                    # Reklamları veya boş tweetleri ele
                    if len(text) > 5:
                        scraped_texts.append(f"TWEET {i+1}: {text}")
            except Exception as e: 
                print(f"🐦 X Tweet Hatası: {e}")

        final_text = "\n\n".join(scraped_texts)
        
        # Fallback (Veri yoksa sayfadaki tüm metni al)
        if len(final_text) < 5: 
            try:
                body_text = await page.locator('body').inner_text()
                return {"platform": "x", "username": username, "data": body_text[:3000], "error": None}
            except:
                return {"platform": "x", "username": username, "data": None, "error": "Veri çekilemedi, giriş sorunu olabilir."}
            
        return {"platform": "x", "username": username, "data": final_text, "error": None}

    except Exception as e:
        return {"platform": "x", "error": f"Genel Hata: {str(e)}"}
    finally:
        await page.close()

# --- 4. LINKEDIN MODÜLÜ ---
async def scrape_linkedin(context, username, deep_scan):
    print(f"👔 LinkedIn taranıyor: {username}")
    page = await context.new_page()
    scraped_texts = []
    config = PLATFORM_CONFIG["linkedin"]
    creds = LOGIN_CREDENTIALS["linkedin"]
    target_url = config["profile_url"].format(username)

    try:
        await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        await human_delay(page, 2, 4)

        if "login" in page.url or "authwall" in page.url:
            print("👔 LinkedIn: Giriş yapılıyor...")
            await page.goto(config["login_url"])
            try:
                await page.locator(config["username_selector"]).fill(creds['username'])
                await page.locator(config["password_selector"]).fill(creds['password'])
                await page.locator(config["submit_selector"]).click()
                await page.wait_for_load_state("networkidle", timeout=30000)
                await page.goto(target_url)
                await human_delay(page, 3, 5)
            except Exception as e: print(f"👔 LinkedIn giriş hatası: {e}")

        # Profil Bilgileri
        try:
            top_card = await page.locator('.pv-top-card').first.inner_text()
            scraped_texts.append(f"KİMLİK KARTI: {top_card}")
            about = await page.locator('#about').locator('..').inner_text()
            scraped_texts.append(f"HAKKINDA: {about}")
        except: pass

        # Gönderiler
        if deep_scan:
            try:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await human_delay(page, 2, 3)
                posts = await page.locator('.feed-shared-update-v2').all()
                for i, post in enumerate(posts[:3]):
                    text = await post.inner_text()
                    scraped_texts.append(f"PAYLAŞIM {i+1}: {text[:500]}")
            except: pass

        final_text = "\n\n".join(scraped_texts)
        if len(final_text) < 5: return {"platform": "linkedin", "username": username, "data": None, "error": "Veri yok"}
        return {"platform": "linkedin", "username": username, "data": final_text, "error": None}

    except Exception as e:
        return {"platform": "linkedin", "error": str(e)}
    finally:
        await page.close()

# --- 5. ANA YÖNETİCİ (DISPATCHER) ---
async def run_concurrent_scraping(usernames_dict, deep_scan=True):
    async with async_playwright() as p:
        # Tarayıcıyı bir kez başlat (Headless=True: Arka planda, False: Görünür)
        browser = await p.chromium.launch(
            headless=True, 
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        # Ortak Cookie (Oturum) dosyalarını yönetmek için context ayarları
        # Not: Her platform kendi context'ini fonksiyon içinde yönetiyor ama 
        # browser instance'ı ortak kullanılıyor.
        
        tasks = []

        # Instagram
        if usernames_dict.get('instagram'):
            auth_file = "instagram_auth_state.json"
            context = await browser.new_context(
                storage_state=auth_file if os.path.exists(auth_file) else None,
                user_agent=USER_AGENT, viewport={'width': 1366, 'height': 768}
            )
            tasks.append(scrape_instagram(context, usernames_dict['instagram'], deep_scan))

        # X (Twitter)
        if usernames_dict.get('x'):
            auth_file = "x_auth_state.json"
            context = await browser.new_context(
                storage_state=auth_file if os.path.exists(auth_file) else None,
                user_agent=USER_AGENT, viewport={'width': 1366, 'height': 768}
            )
            tasks.append(scrape_x(context, usernames_dict['x'], deep_scan))

        # LinkedIn
        if usernames_dict.get('linkedin'):
            auth_file = "linkedin_auth_state.json"
            context = await browser.new_context(
                storage_state=auth_file if os.path.exists(auth_file) else None,
                user_agent=USER_AGENT, viewport={'width': 1366, 'height': 768}
            )
            tasks.append(scrape_linkedin(context, usernames_dict['linkedin'], deep_scan))

        # Hepsini aynı anda başlat
        if not tasks: return []
        
        print(f"--- Toplam {len(tasks)} görev başlatılıyor... ---")
        results = await asyncio.gather(*tasks)
        
        await browser.close()
        return results