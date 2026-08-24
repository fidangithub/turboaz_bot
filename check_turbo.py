#!/usr/bin/env python3
"""
Turbo.az bildiriş botu
-----------------------
Bu skript turbo.az saytında müəyyən marka üzrə elanlara baxır,
başlığında axtardığın model adı olan (məs: "Sunny") elanları tapır,
əvvəl görülməmiş olanları Telegram-a bildiriş kimi göndərir.

Konfiqurasiya aşağıdakı sabitlərdə (CONFIG) edilir və ya mühit
dəyişənləri (environment variables) ilə override edilə bilər —
bu, tokeni kodun içində açıq saxlamamaq üçündür (GitHub Secrets).
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

# ----------------------- CONFIG -----------------------
# Bunları öz məlumatınla doldur, YA DA mühit dəyişəni kimi ver
# (GitHub Actions-da Secrets istifadə et, tokeni koda yazma!)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "PUT_YOUR_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "848837342")

# Axtarış filtrləri:
MAKE_ID = "7"          # Nissan-ın turbo.az-dakı ID-si
MODEL_KEYWORD = "sunny"  # Başlıqda axtarılacaq söz (kiçik hərflərlə)

# İl aralığı (boş buraxsan hər il axtarılır)
MIN_YEAR = None   # məs: 2010
MAX_YEAR = None   # məs: 2020

# Qiymət aralığı AZN (boş buraxsan hər qiymət axtarılır)
MIN_PRICE = None  # məs: 8000
MAX_PRICE = None  # məs: 20000

SEARCH_URL = f"https://turbo.az/autos?q%5Bmake%5D%5B%5D={MAKE_ID}"
SEEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seen_ids.json")

# --------------------------------------------------------


def load_seen_ids():
    """Əvvəl görülmüş elan ID-lərini fayldan oxu."""
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_seen_ids(seen_ids):
    """Görülmüş ID-ləri fayla yaz."""
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen_ids), f)


def fetch_page(url):
    """Bir səhifəni HTML kimi çək."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_listings(html):
    """
    HTML içindən elan bloklarını çıxarır.
    Turbo.az elan linkləri bu formatdadır: /autos/12345678-nissan-sunny
    Hər linkin yanında qiymət və başlıq məlumatı olur.
    """
    listings = []
    # Elan linklərini tap: /autos/<id>-<slug>
    pattern = re.compile(r'href="(/autos/(\d+)-([a-z0-9\-]+))"')
    seen_in_page = set()
    for match in pattern.finditer(html):
        path, listing_id, slug = match.groups()
        if listing_id in seen_in_page:
            continue
        seen_in_page.add(listing_id)
        listings.append({
            "id": listing_id,
            "slug": slug,
            "url": "https://turbo.az" + path,
        })
    return listings


def filter_by_model(listings, keyword):
    """Slug içində axtarılan model sözü olan elanları saxla."""
    keyword = keyword.lower()
    return [l for l in listings if keyword in l["slug"].lower()]


def send_telegram_message(token, chat_id, text):
    """Telegram-a mesaj göndər."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status == 200
    except urllib.error.URLError as e:
        print(f"Telegram xətası: {e}", file=sys.stderr)
        return False


def main():
    if TELEGRAM_BOT_TOKEN == "PUT_YOUR_TOKEN_HERE":
        print("XƏTA: TELEGRAM_BOT_TOKEN təyin edilməyib.", file=sys.stderr)
        sys.exit(1)

    print(f"Axtarış: {SEARCH_URL}")
    seen_ids = load_seen_ids()
    first_run = len(seen_ids) == 0

    try:
        html = fetch_page(SEARCH_URL)
    except Exception as e:
        print(f"Səhifəni çəkmək mümkün olmadı: {e}", file=sys.stderr)
        sys.exit(1)

    all_listings = parse_listings(html)
    matched = filter_by_model(all_listings, MODEL_KEYWORD)

    print(f"Tapılan {MODEL_KEYWORD} elanı: {len(matched)}")

    new_listings = [l for l in matched if l["id"] not in seen_ids]

    if first_run:
        # İlk işə salınmada bütün mövcud elanları "görülmüş" say,
        # yalnız bundan sonra yeniləri bildiriş kimi göndər.
        print("İlk işə salınma — mövcud elanlar bazaya yazılır, bildiriş göndərilmir.")
        for l in matched:
            seen_ids.add(l["id"])
        save_seen_ids(seen_ids)
        return

    if not new_listings:
        print("Yeni elan yoxdur.")
        return

    for listing in new_listings:
        message = (
            f"🚗 Yeni Nissan Sunny elanı!\n\n"
            f"{listing['url']}"
        )
        ok = send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)
        if ok:
            print(f"Bildiriş göndərildi: {listing['url']}")
        else:
            print(f"Bildiriş göndərilmədi: {listing['url']}", file=sys.stderr)
        seen_ids.add(listing["id"])
        time.sleep(1)  # Telegram rate-limit üçün kiçik fasilə

    save_seen_ids(seen_ids)


if __name__ == "__main__":
    main()
