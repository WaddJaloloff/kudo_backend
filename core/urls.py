from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    MahsulotViewSet,
    AvtomobilViewSet,
    MahsulotKategoriyaViewSet,
    BuyurtmaCreateView,
)

router = DefaultRouter()
router.register(r"avtomobillar", AvtomobilViewSet, basename="avtomobil")
router.register(r"mahsulot-kategoriyalar", MahsulotKategoriyaViewSet, basename="mahsulot-kategoriya")
router.register(r"products", MahsulotViewSet, basename="mahsulot")

urlpatterns = [
    path("", include(router.urls)),
    path("buyurtmalar/", BuyurtmaCreateView.as_view(), name="buyurtmalar"),
]
