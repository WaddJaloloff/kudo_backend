from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_add_mashina_turi_to_buyurtma'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyurtmamahsuloti',
            name='mashina_turi',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Mashina turi'),
        ),
    ]
