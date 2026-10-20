import os
import logging
import requests as http_requests

from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Mahsulot, Avtomobil, MahsulotKategoriya, Buyurtma
from .serializers import (
    MahsulotSerializer,
    AvtomobilSerializer,
    MahsulotKategoriyaSerializer,
    BuyurtmaSerializer,
)

logger = logging.getLogger(__name__)


def send_order_notification(buyurtma: Buyurtma):
    """Yangi buyurtma haqida Telegram botga xabar yuboradi."""
    token = os.getenv("ORDER_BOT_TOKEN") or os.getenv("BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.warning("Telegram bot token yoki chat_id topilmadi, xabar yuborilmadi.")
        return

    mahsulotlar_text = ""
    for i, m in enumerate(buyurtma.mahsulotlar, 1):
        nomi = m.get("nomi", "—")
        soni = m.get("soni", 1)
        mashina = m.get("mashina_turi", "")
        mashina_text = f" ({mashina})" if mashina else ""
        mahsulotlar_text += f"  {i}. {nomi}{mashina_text} × {soni}\n"

    maps_link = ""
    if buyurtma.latitude and buyurtma.longitude:
        maps_link = f"\n🗺 <a href='https://yandex.uz/maps/?pt={buyurtma.longitude},{buyurtma.latitude}&z=17&l=map'>Xaritada ko'rish</a>"

    text = (
        f"🛒 <b>Yangi buyurtma #{buyurtma.id}</b>\n\n"
        f"👤 <b>Ism:</b> {buyurtma.ism}\n"
        f"📞 <b>Telefon:</b> {buyurtma.telefon}\n"
        f"📍 <b>Manzil:</b> {buyurtma.manzil or '—'}{maps_link}\n"
        f"💬 <b>Izoh:</b> {buyurtma.izoh or '—'}\n\n"
        f"📦 <b>Mahsulotlar:</b>\n{mahsulotlar_text}"
    )

    try:
        http_requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception as e:
        logger.error(f"Telegram xabar yuborishda xato: {e}")


class AvtomobilViewSet(viewsets.ModelViewSet):
    queryset = Avtomobil.objects.all()
    serializer_class = AvtomobilSerializer


class MahsulotKategoriyaViewSet(viewsets.ModelViewSet):
    queryset = MahsulotKategoriya.objects.all()
    serializer_class = MahsulotKategoriyaSerializer


class BuyurtmaViewSet(viewsets.ModelViewSet):
    queryset = Buyurtma.objects.all()
    serializer_class = BuyurtmaSerializer
    http_method_names = ["get", "post", "head", "options"]  # PUT/DELETE yoq

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        buyurtma = serializer.save()
        send_order_notification(buyurtma)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MahsulotViewSet(viewsets.ModelViewSet):
    serializer_class = MahsulotSerializer

    def get_queryset(self):
        qs = Mahsulot.objects.all().prefetch_related(
            "rasmlar",
            "xususiyatlar",
            "avtomobillar"
        ).select_related("mahsulot_kategoriyasi")

        avtomobil = self.request.query_params.get("avtomobil")
        kategoriya = self.request.query_params.get("kategoriya")

        if avtomobil:
            qs = qs.filter(avtomobillar__slug=avtomobil)

        if kategoriya:
            qs = qs.filter(mahsulot_kategoriyasi__slug=kategoriya)

        return qs.distinct()
