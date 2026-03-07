from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from openpyxl import Workbook
from .models import (
    Avtomobil,
    MahsulotKategoriya,
    Mahsulot,
    MahsulotRasmi,
    MahsulotXususiyati,
    TasdiqlovchiSet,
    TasdiqlovchiKod,
    TelegramFoydalanuvchi,
)
import random


# 🚗 Avtomobil admin (oldingi Kategoriya)
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
        'yaratilgan_vaqti',
        'rasm_preview'
    )

    search_fields = ('nomi', 'tavsifi')
    list_filter = ('mahsulot_kategoriyasi', 'avtomobillar')

    inlines = [
        MahsulotRasmiInline,
        MahsulotXususiyatiInline
    ]

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': (
                'nomi',
                'mahsulot_kategoriyasi',
                'avtomobillar',
                'tavsifi'
            )
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


# 🏷 Etiketka set
@admin.register(TasdiqlovchiSet)
class TasdiqlovchiSetAdmin(admin.ModelAdmin):
    list_display = ("id", "soni", "yaratilgan_vaqti")
    actions = ["export_selected_to_excel"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            for _ in range(obj.soni):
                TasdiqlovchiKod.objects.create(
                    tasdiqlovchi_set=obj,
                    code=str(random.randint(100000, 999999))
                )

    def export_selected_to_excel(self, request, queryset):
        wb = Workbook()
        ws = wb.active
        ws.append(["ID", "CODE"])

        for s in queryset:
            for kod in s.kodlar.all():
                ws.append([kod.id, kod.code])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = 'attachment; filename="kodlar.xlsx"'
        wb.save(response)
        return response

    export_selected_to_excel.short_description = "Excel yuklab olish"


# 👤 Telegram foydalanuvchi
@admin.register(TelegramFoydalanuvchi)
class TelegramFoydalanuvchiAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "telegram_id",
        "telegram_username",
        "telefon_raqam",
        "yaratilgan_vaqti"
    )