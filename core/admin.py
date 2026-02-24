from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from openpyxl import Workbook
from .models import *
import random


# Kategoriya admin
@admin.register(Kategoriya)
class KategoriyaAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'slug')
    prepopulated_fields = {'slug': ('nomi',)}
    search_fields = ('nomi',)


# MahsulotXususiyati inline
class MahsulotXususiyatiInline(admin.TabularInline):
    model = MahsulotXususiyati
    extra = 1
    verbose_name = "Xususiyat"
    verbose_name_plural = "Xususiyatlar"



class MahsulotRasmiInline(admin.TabularInline):
    model = MahsulotRasmi
    extra = 1
    verbose_name = "Rasm"
    verbose_name_plural = "Rasm"


# Mahsulot admin
@admin.register(Mahsulot)
class MahsulotAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'get_kategoriyalar', 'yaratilgan_vaqti', 'rasm_preview')
    search_fields = ('nomi', 'tavsifi')
    list_filter = ('kategoriyalar',)

    inlines = [
        MahsulotRasmiInline,      # 1️⃣ Avval Rasm
        MahsulotXususiyatiInline  # 3️⃣ Keyin Xususiyatlar
    ]

    fieldsets = (
        ("Umumiy ma'lumotlar", {
            'fields': ('nomi', 'kategoriyalar', 'tavsifi')
        }),
    )

    def get_kategoriyalar(self, obj):
        return ", ".join([k.nomi for k in obj.kategoriyalar.all()])
    get_kategoriyalar.short_description = "Kategoriyalar"

    def rasm_preview(self, obj):
        asosiy_rasm = obj.rasmlar.filter(asosiy=True).first() or obj.rasmlar.first()

        if asosiy_rasm:
            return format_html(
                '<img src="{}" width="80" style="border-radius:6px;" />',
                asosiy_rasm.rasm.url
            )
        return "Rasm yo‘q"

    rasm_preview.short_description = "Rasm"




@admin.register(TasdiqlovchiSet)
class TasdiqlovchiSetAdmin(admin.ModelAdmin):
    list_display = ("id", "mahsulot", "soni", "yaratilgan_vaqti")
    actions = ["export_selected_to_excel"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            for i in range(obj.soni):
                code = str(random.randint(100000, 999999))

                TasdiqlovchiKod.objects.create(
                    tasdiqlovchi_set=obj,
                    code=code
                )


    def export_selected_to_excel(self, request, queryset):
        wb = Workbook()
        ws = wb.active
        ws.append(["Unikal ID", "CODE"])

        for tasdiqlovchi_set in queryset.order_by("id"):
            for kod in tasdiqlovchi_set.kodlar.all().order_by("id"):
                ws.append([
                    kod.id,
                    kod.code
                ])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = 'attachment; filename="tasdiqlovchi_kodlar.xlsx"'
        wb.save(response)

        return response

    export_selected_to_excel.short_description = "Excel'ni yuklab olish"

@admin.register(TelegramFoydalanuvchi)
class TelegramFoydalanuvchiAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "telegram_id",
        "telegram_username",
        "telefon_raqam",
        "yaratilgan_vaqti"
    )
