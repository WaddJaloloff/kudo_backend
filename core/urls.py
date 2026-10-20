from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    MahsulotViewSet,
    AvtomobilViewSet,
    MahsulotKategoriyaViewSet,
    BuyurtmaViewSet,
)

router = DefaultRouter()
router.register(r'avtomobillar', AvtomobilViewSet, basename='avtomobil')
router.register(r'mahsulot-kategoriyalar', MahsulotKategoriyaViewSet, basename='mahsulot-kategoriya')
router.register(r'products', MahsulotViewSet, basename='mahsulot')
router.register(r'buyurtmalar', BuyurtmaViewSet, basename='buyurtma')

urlpatterns = [
    path('', include(router.urls)),
]
