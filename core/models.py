
import random
from django.db import models
from django.utils.crypto import get_random_string
from django.db import models



class Avtomobil(models.Model):
    nomi = models.CharField("Avtomobil nomi", max_length=150)
    slug = models.SlugField("URL nomi", unique=True)

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name = "Avtomobil"
        verbose_name_plural = "Avtomobillar"

class MahsulotKategoriya(models.Model):
    nomi = models.CharField("Kategoriya nomi", max_length=150)
    slug = models.SlugField("URL nomi", unique=True)

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name = "Kategoriyasi "
        verbose_name_plural = "Kategoriyalari "
        

class Mahsulot(models.Model):

    # ❗ MAJBURIY: mahsulot turi (amortizator, moy...)
    mahsulot_kategoriyasi = models.ForeignKey(
        MahsulotKategoriya,
        on_delete=models.PROTECT,
        verbose_name="Kategoriyasi ",
        null=True,    # vaqtincha
        blank=True
    )

    # ❗ KO‘P avtomobilga mos
    avtomobillar = models.ManyToManyField(
        Avtomobil,
        related_name="mahsulotlar",
        verbose_name="Avtomobillar ",
        blank=True
    )

    nomi = models.CharField("Nomi", max_length=200)
    tavsifi = models.TextField("Tavsifi")
    yaratilgan_vaqti = models.DateTimeField("Yaratilgan vaqti", auto_now_add=True)

    def __str__(self):
        return self.nomi
    class Meta:
        verbose_name = "Mahsulot "
        verbose_name_plural = "Mahsulotlar "
    
class MahsulotRasmi(models.Model):
    mahsulot = models.ForeignKey(
        Mahsulot,
        on_delete=models.CASCADE,
        related_name="rasmlar",
        verbose_name="Mahsulot "
    )

    rasm = models.ImageField("Rasm", upload_to="products/")
    asosiy = models.BooleanField(default=False)  # optional (asosiy rasm belgilash uchun)
    yuklangan_vaqti = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mahsulot.nomi} rasmi"
    
    class Meta:
        verbose_name = "Mahsulot rasmi "
        verbose_name_plural = "Mahsulot rasmlari "

class MahsulotXususiyati(models.Model):
    mahsulot = models.ForeignKey(
        Mahsulot,
        on_delete=models.CASCADE,
        related_name="xususiyatlar",
        verbose_name="Mahsulot "
    )
    sarlavha = models.CharField("Sarlavha", max_length=200)

    def __str__(self):
        return f"{self.mahsulot.nomi} - {self.sarlavha}"

    class Meta:
        verbose_name = "Mahsulot xususiyati "
        verbose_name_plural = "Mahsulot xususiyatlari "


class TelegramFoydalanuvchi(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    telegram_username = models.CharField(max_length=255, null=True, blank=True)
    telefon_raqam = models.CharField(max_length=20)
    yaratilgan_vaqti = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.telegram_id} - {self.telefon_raqam}"

    class Meta:
        verbose_name = "Telegram foydalanuvchisi "
        verbose_name_plural = "Telegram foydalanuvchilar "


class TasdiqlovchiSet(models.Model):
    soni = models.IntegerField("Etiketka soni")
    yaratilgan_vaqti = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Etiketka "
        verbose_name_plural = "Etiketkalar "



class TasdiqlovchiKod(models.Model):
    tasdiqlovchi_set = models.ForeignKey(
        TasdiqlovchiSet,
        on_delete=models.CASCADE,
        related_name="kodlar"
    )

    code = models.CharField(max_length=6)

    ishlatilgan = models.BooleanField(default=False)

    tekshirgan_user = models.ForeignKey(
        TelegramFoydalanuvchi,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    tekshirilgan_vaqti = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.code}"

    class Meta:
        verbose_name = "Etiketka kod "
        verbose_name_plural = "Etiketka kodlari "
