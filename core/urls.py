from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import export_excel
from .views import KategoriyaViewSet, MahsulotViewSet

router = DefaultRouter()
router.register(r'categories', KategoriyaViewSet)
router.register(r'products', MahsulotViewSet)

urlpatterns = [
    path('export_excel/<int:set_id>/', export_excel, name='export_excel'),
    path('', include(router.urls)),
]