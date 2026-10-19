"""
Buyurtma yaratilganda Telegram guruhiga xabar yuboradi.
python-telegram-bot 4.x (sync) yoki requests orqali ishlaydi.
Asinxron thread — asosiy so'rovni bloklamaydi.
"""
import html
import os
import threading


def _get_cfg():
    try:
        from django.conf import settings
        token = getattr(settings, "BOT_TOKEN", "").strip()
        chat_id = getattr(settings, "TELEGRAM_CHAT_ID", "").strip()
        site_url = getattr(settings, "SITE_URL", "http://localhost:8000").rstrip("/")
    except Exception:
        token = os.getenv("BOT_TOKEN", "").strip()
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        site_url = os.getenv("SITE_URL", "http://localhost:8000").rstrip("/")
    return token, chat_id, site_url


def _admin_url(site_url, bid):
    return f"{site_url}/admin/core/buyurtma/{bid}/change/"


def _is_local(site_url):
    """Return True if site_url points to localhost — Telegram rejects such URLs in buttons."""
    return any(x in site_url for x in ("localhost", "127.0.0.1"))


def _build_text(b):
    """Build a clean Telegram HTML message with all order details."""
    from datetime import timezone as _tz, timedelta as _td
    UZT = _tz(_td(hours=5))
    time_s = b.yaratilgan_vaqti.astimezone(UZT).strftime("%d.%m.%Y  %H:%M")
    mahsulotlar = list(b.mahsulotlar.all())
    total_qty = sum(i.soni for i in mahsulotlar)

    # Product lines with per-item car selection
    items_lines = []
    for i in mahsulotlar:
        mashina = getattr(i, "mashina_turi", "")
        car_tag = f" <i>({html.escape(mashina)})</i>" if mashina and mashina.strip() else ""
        items_lines.append(f"  — {html.escape(i.nomi)}{car_tag}")
        items_lines.append(f"    <b>{i.soni} ta</b>")
    items_text = "\n".join(items_lines)

    loc_line  = f"\n📍 <b>Manzil:</b> {html.escape(b.manzil)}" if getattr(b, "manzil", None) and b.manzil.strip() else ""
    note_line = f"\n💬 <b>Izoh:</b> {html.escape(b.izoh)}"    if getattr(b, "izoh",   None) and b.izoh.strip()   else ""

    return (
        f"🆕 <b>YANGI BUYURTMA #{b.id}</b>\n"
        f"🕐 <i>{time_s}</i>\n"
        f"\n"
        f"👤 <b>Ismi: {html.escape(b.ism)}</b>\n"
        f"📞 <b>Buyurtmachi raqami: {html.escape(b.telefon)}</b>"
        f"{loc_line}"
        f"{note_line}\n"
        f"\n"
        f"📦 <b>Buyurtma tafsilotlari:</b>\n"
        f"{items_text}\n"
        f"\n"
        f"💰 <b>Jami miqdor: {total_qty} ta</b>"
    )


def _build_keyboard(b, site_url, telegram_lib=None):
    """Return inline keyboard rows."""
    rows = []

    if not _is_local(site_url):
        url = _admin_url(site_url, b.id)
        if telegram_lib:
            rows.append([telegram_lib.InlineKeyboardButton("🖥  Panelda ochish", url=url)])
        else:
            rows.append([{"text": "🖥  Panelda ochish", "url": url}])

    if getattr(b, "latitude", None) and getattr(b, "longitude", None):
        lat, lng = b.latitude, b.longitude
        gmaps  = f"https://www.google.com/maps?q={lat},{lng}"
        yandex = f"https://yandex.uz/maps/?pt={lng},{lat}&z=17&l=map"

        if telegram_lib:
            rows.append([
                telegram_lib.InlineKeyboardButton("🗺 Google Maps", url=gmaps),
                telegram_lib.InlineKeyboardButton("🗺 Yandex Maps", url=yandex),
            ])
        else:
            rows.append([
                {"text": "🗺 Google Maps", "url": gmaps},
                {"text": "🗺 Yandex Maps", "url": yandex},
            ])

    return rows


def _do_send(buyurtma_id):
    token, chat_id, site_url = _get_cfg()
    if not token:
        print("[TelegramNotify] BOT_TOKEN topilmadi — .env ni tekshiring.")
        return
    if not chat_id:
        print("[TelegramNotify] TELEGRAM_CHAT_ID topilmadi — .env ni tekshiring.")
        return
    _do_send_requests(buyurtma_id, token, chat_id, site_url)


def _do_send_requests(buyurtma_id, token, chat_id, site_url):
    try:
        import requests
        from core.models import Buyurtma
        b = Buyurtma.objects.prefetch_related("mahsulotlar").get(pk=buyurtma_id)

        text = _build_text(b)
        rows = _build_keyboard(b, site_url, telegram_lib=None)

        api = f"https://api.telegram.org/bot{token}"
        payload = {
            "chat_id": int(chat_id),
            "text": text,
            "parse_mode": "HTML",
        }
        if rows:
            payload["reply_markup"] = {"inline_keyboard": rows}

        resp = requests.post(f"{api}/sendMessage", json=payload, timeout=10)
        if not resp.ok:
            print(f"[TelegramNotify] sendMessage failed: {resp.status_code} {resp.text}")

        if getattr(b, "latitude", None) and getattr(b, "longitude", None):
            requests.post(f"{api}/sendLocation", json={
                "chat_id": int(chat_id),
                "latitude": b.latitude, "longitude": b.longitude,
            }, timeout=10)

    except Exception as exc:
        print(f"[TelegramNotify/requests] Xato: {exc}")


def send_order_notification(buyurtma_id):
    """Non-blocking — background thread da ishlaydi."""
    threading.Thread(target=_do_send, args=(buyurtma_id,), daemon=True).start()
