from django.db import models


class MahsulotKategoriya(models.Model):
    nomi = models.CharField('Kategoriya nomi', max_length=100)
    slug = models.SlugField(unique=True, allow_unicode=True)

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name = 'Mahsulot kategoriyasi'
        verbose_name_plural = 'Mahsulot kategoriyalari'


class Avtomobil(models.Model):
    nomi = models.CharField('Avtomobil nomi', max_length=100)
    slug = models.SlugField(unique=True, allow_unicode=True)

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name = 'Avtomobil'
        verbose_name_plural = 'Avtomobillar'


class Mahsulot(models.Model):
    nomi = models.CharField('Nomi', max_length=200)
    tavsifi = models.TextField('Tavsifi', blank=True)
    mahsulot_kategoriyasi = models.ForeignKey(
        MahsulotKategoriya,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='mahsulotlar',
        verbose_name='Mahsulot kategoriyasi'
    )
    avtomobillar = models.ManyToManyField(
        Avtomobil,
        blank=True,
        related_name='mahsulotlar',
        verbose_name='Avtomobillar'
    )

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name = 'Mahsulot'
        verbose_name_plural = 'Mahsulotlar'


class MahsulotXususiyati(models.Model):
    mahsulot = models.ForeignKey(
        Mahsulot,
        on_delete=models.CASCADE,
        related_name='xususiyatlar',
        verbose_name='Mahsulot'
    )
    sarlavha = models.CharField('Sarlavha', max_length=200)

    def __str__(self):
        return self.sarlavha

    class Meta:
        verbose_name = 'Mahsulot xususiyati'
        verbose_name_plural = 'Mahsulot xususiyatlari'


class MahsulotRasmi(models.Model):
    mahsulot = models.ForeignKey(
        Mahsulot,
        on_delete=models.CASCADE,
        related_name='rasmlar',
        verbose_name='Mahsulot'
    )
    rasm = models.ImageField('Rasm', upload_to='mahsulot_rasmlari/')
    asosiy = models.BooleanField('Asosiy rasm', default=False)

    def __str__(self):
        return f"{self.mahsulot.nomi} rasmi"

    class Meta:
        verbose_name = 'Mahsulot rasmi'
        verbose_name_plural = 'Mahsulot rasmlari'


class Buyurtma(models.Model):
    ism = models.CharField('Ism', max_length=200)
    telefon = models.CharField('Telefon', max_length=30)
    izoh = models.TextField('Izoh', blank=True, default='')
    manzil = models.TextField('Manzil', blank=True, default='')
    latitude = models.FloatField('Latitude', null=True, blank=True)
    longitude = models.FloatField('Longitude', null=True, blank=True)
    mashina_turi = models.CharField('Mashina turi', max_length=200, blank=True, default='')
    yaratilgan_vaqti = models.DateTimeField('Yaratilgan vaqti', auto_now_add=True)

    def __str__(self):
        return f"Buyurtma #{self.id} — {self.ism}"

    class Meta:
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'
        ordering = ['-yaratilgan_vaqti']


class BuyurtmaMahsuloti(models.Model):
    buyurtma = models.ForeignKey(
        Buyurtma,
        on_delete=models.CASCADE,
        related_name="mahsulotlar",
        verbose_name="Buyurtma"
    )
    mahsulot_id = models.IntegerField("Mahsulot ID")
    nomi = models.CharField("Nomi", max_length=200)
    soni = models.PositiveIntegerField("Soni", default=1)
    mashina_turi = models.CharField("Mashina turi", max_length=200, blank=True, default='')

    def __str__(self):
        return f"{self.nomi} x {self.soni}"

    class Meta:
        verbose_name = "Buyurtma mahsuloti "
        verbose_name_plural = "Buyurtma mahsulotlari "
