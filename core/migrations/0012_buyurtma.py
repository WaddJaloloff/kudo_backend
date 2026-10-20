from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_merge_20260308_0020"),
    ]

    operations = [
        migrations.CreateModel(
            name="Buyurtma",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ism", models.CharField(max_length=200, verbose_name="Ismi")),
                (
                    "telefon",
                    models.CharField(max_length=20, verbose_name="Telefon raqami"),
                ),
                (
                    "izoh",
                    models.TextField(blank=True, default="", verbose_name="Izoh"),
                ),
                (
                    "latitude",
                    models.FloatField(blank=True, null=True, verbose_name="Latitude"),
                ),
                (
                    "longitude",
                    models.FloatField(blank=True, null=True, verbose_name="Longitude"),
                ),
                (
                    "manzil",
                    models.TextField(blank=True, default="", verbose_name="Manzil"),
                ),
                (
                    "mahsulotlar",
                    models.JSONField(default=list, verbose_name="Mahsulotlar (JSON)"),
                ),
                (
                    "holat",
                    models.CharField(
                        choices=[
                            ("yangi", "Yangi"),
                            ("qabul_qilindi", "Qabul qilindi"),
                            ("yetkazildi", "Yetkazildi"),
                            ("bekor_qilindi", "Bekor qilindi"),
                        ],
                        default="yangi",
                        max_length=30,
                        verbose_name="Holat",
                    ),
                ),
                (
                    "yaratilgan_vaqti",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Yaratilgan vaqti"
                    ),
                ),
            ],
            options={
                "verbose_name": "Buyurtma",
                "verbose_name_plural": "Buyurtmalar",
                "ordering": ["-yaratilgan_vaqti"],
            },
        ),
    ]
