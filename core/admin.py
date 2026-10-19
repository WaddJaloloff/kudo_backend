from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
try:
    from openpyxl import Workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

from .models import (
    Avtomobil,
    MahsulotKategoriya,
    Mahsulot,
    MahsulotRasmi,
    MahsulotXususiyati,
    Buyurtma,
    BuyurtmaMahsuloti,
)


# 🚗 Avtomobil admin
@admin.register(Avtomobil)
class AvtomobilAdmin(admin.ModelAdmin):
    list_display = ('id', 'nomi', 'slug')
    prepopulated_fields = {'slug': ('nomi',)}
    search_fields = ('nomi',)


# 🧩 Mahsulot kategoriyasi admin
@admin.register(MahsulotKategoriya)
class MahsulotKategoriyaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nomi', 'slug')
    prepopulated_fields = {'slug': ('nomi',)}
    search_fields = ('nomi',)


# 🔧 Xususiyat inline
class MahsulotXususiyatiInline(admin.TabularInline):
    model = MahsulotXususiyati
    extra = 1


# 🖼 Rasm inline
class MahsulotRasmiInline(admin.TabularInline):
    model = MahsulotRasmi
    extra = 1


# 📦 Mahsulot admin
@admin.register(Mahsulot)
class MahsulotAdmin(admin.ModelAdmin):
    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = "Yangi mahsulot"
        return super().add_view(request, form_url, extra_context)

    list_display = (
        'id',
        'nomi',
        'mahsulot_kategoriyasi',
        'get_avtomobillar',
        'rasm_preview',
    )
    search_fields = ('nomi', 'tavsifi')
    list_filter = ('mahsulot_kategoriyasi', 'avtomobillar')
    inlines = [MahsulotRasmiInline, MahsulotXususiyatiInline]
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('nomi', 'mahsulot_kategoriyasi', 'avtomobillar', 'tavsifi')
        }),
    )

    def get_avtomobillar(self, obj):
        return ", ".join(a.nomi for a in obj.avtomobillar.all())
    get_avtomobillar.short_description = "Avtomobillar"

    def rasm_preview(self, obj):
        rasm = obj.rasmlar.filter(asosiy=True).first() or obj.rasmlar.first()
        if rasm:
            return format_html(
                '<img src="{}" width="70" style="border-radius:6px;" />',
                rasm.rasm.url
            )
        return "—"
    rasm_preview.short_description = "Rasm"


# 📋 Buyurtma mahsulotlari inline
class BuyurtmaMahsulotiInline(admin.TabularInline):
    model = BuyurtmaMahsuloti
    extra = 0
    readonly_fields = ['mahsulot_id', 'nomi', 'soni', 'mashina_turi']


# 🛒 Buyurtma admin
@admin.register(Buyurtma)
class BuyurtmaAdmin(admin.ModelAdmin):
    list_display = ['id', 'ism', 'telefon', 'harita_link', 'yaratilgan_vaqti']
    list_filter = []
    search_fields = ['ism', 'telefon']
    inlines = [BuyurtmaMahsulotiInline]
    readonly_fields = ['yaratilgan_vaqti', 'latitude', 'longitude', 'harita_link']
    list_per_page = 25

    def harita_link(self, obj):
        if obj.latitude and obj.longitude:
            lat, lng = obj.latitude, obj.longitude
            google  = f"https://www.google.com/maps?q={lat},{lng}"
            yandex  = f"https://yandex.uz/maps/?pt={lng},{lat}&z=17&l=map"
            two_gis = f"https://2gis.uz/geo/{lng},{lat}"
            copy_js = (
                f"navigator.clipboard.writeText('{yandex}').then(function(){{"
                f"this.textContent='✅ Nusxa olindi!';setTimeout(()=>this.textContent='📋 Yandex link',2000)"
                f"}}.bind(this),function(){{prompt('Nusxa oling:','{yandex}')}});"
            )
            return format_html(
                '<div style="display:flex;flex-wrap:wrap;gap:4px;align-items:center;">'
                '<a href="{}" target="_blank" '
                'style="display:inline-block;padding:4px 10px;border-radius:5px;'
                'background:#4285F4;color:#fff;font-size:12px;font-weight:500;text-decoration:none;">'
                '🗺 Google Maps</a>'
                '<a href="{}" target="_blank" '
                'style="display:inline-block;padding:4px 10px;border-radius:5px;'
                'background:#FF3333;color:#fff;font-size:12px;font-weight:500;text-decoration:none;">'
                '🗺 Yandex Maps</a>'
                '<a href="{}" target="_blank" '
                'style="display:inline-block;padding:4px 10px;border-radius:5px;'
                'background:#00C347;color:#fff;font-size:12px;font-weight:500;text-decoration:none;">'
                '🗺 2GIS</a>'
                '<button onclick="{}" '
                'style="display:inline-block;padding:4px 10px;border-radius:5px;'
                'background:#8B5CF6;color:#fff;font-size:12px;font-weight:500;border:none;cursor:pointer;">'
                '📋 Yandex link</button>'
                '</div>',
                google, yandex, two_gis, copy_js,
            )
        return "—"
    harita_link.short_description = "Xarita"
    harita_link.allow_tags = True
