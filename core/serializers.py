from rest_framework import serializers
from .models import (
    Mahsulot,
    MahsulotXususiyati,
    MahsulotRasmi,
    Avtomobil,
    MahsulotKategoriya
)


class MahsulotXususiyatiSerializer(serializers.ModelSerializer):
    class Meta:
        model = MahsulotXususiyati
        fields = ["id", "sarlavha"]


class MahsulotRasmiSerializer(serializers.ModelSerializer):
    class Meta:
        model = MahsulotRasmi
        fields = ["id", "rasm", "asosiy"]


class MahsulotSerializer(serializers.ModelSerializer):
    rasmlar = MahsulotRasmiSerializer(many=True, read_only=True)
    xususiyatlar = MahsulotXususiyatiSerializer(many=True, read_only=True)

    # eski avtomobil kategoriyasi
    avtomobillar = serializers.StringRelatedField(many=True)

    # mahsulot kategoriyasi (filter va catalog uchun)
    mahsulot_kategoriyasi = serializers.StringRelatedField()

    asosiy_rasm = serializers.SerializerMethodField()
    kategoriyalar = serializers.SerializerMethodField()  # catalog filter uchun

    class Meta:
        model = Mahsulot
        fields = [
            "id",
            "nomi",
            "tavsifi",
            "mahsulot_kategoriyasi",  # catalog filter
            "avtomobillar",           # modal va kartada eski joyida
            "xususiyatlar",
            "rasmlar",
            "asosiy_rasm",
            "kategoriyalar",
        ]

    def get_asosiy_rasm(self, obj):
        rasm = obj.rasmlar.filter(asosiy=True).first() or obj.rasmlar.first()
        if rasm:
            request = self.context.get("request")
            return request.build_absolute_uri(rasm.rasm.url)
        return None

    def get_kategoriyalar(self, obj):
        # catalog filter uchun faqat mahsulot kategoriyasi
        return [str(obj.mahsulot_kategoriyasi)]
    
class AvtomobilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avtomobil
        fields = ["id", "nomi", "slug"]


class MahsulotKategoriyaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MahsulotKategoriya
        fields = ["id", "nomi", "slug"]

from .models import Buyurtma, BuyurtmaMahsuloti


class BuyurtmaMahsulotiSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nomi = serializers.CharField()
    soni = serializers.IntegerField(min_value=1)
    mashina_turi = serializers.CharField(allow_blank=True, default='')


class BuyurtmaCreateSerializer(serializers.ModelSerializer):
    mahsulotlar = BuyurtmaMahsulotiSerializer(many=True, write_only=True)

    class Meta:
        model = Buyurtma
        fields = ['ism', 'telefon', 'izoh', 'manzil', 'latitude', 'longitude', 'mahsulotlar']

    def create(self, validated_data):
        mahsulotlar_data = validated_data.pop('mahsulotlar', [])
        buyurtma = Buyurtma.objects.create(**validated_data)
        for item in mahsulotlar_data:
            BuyurtmaMahsuloti.objects.create(
                buyurtma=buyurtma,
                mahsulot_id=item['id'],
                nomi=item['nomi'],
                soni=item['soni'],
                mashina_turi=item.get('mashina_turi', '')
            )
        return buyurtma


class BuyurtmaListSerializer(serializers.ModelSerializer):
    mahsulotlar = serializers.SerializerMethodField()

    class Meta:
        model = Buyurtma
        fields = '__all__'

    def get_mahsulotlar(self, obj):
        return BuyurtmaMahsulotiSerializer(obj.mahsulotlar.all(), many=True).data
