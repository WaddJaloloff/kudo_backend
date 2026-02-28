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

    avtomobillar = serializers.StringRelatedField(many=True)
    mahsulot_kategoriyasi = serializers.StringRelatedField()

    asosiy_rasm = serializers.SerializerMethodField()

    class Meta:
        model = Mahsulot
        fields = [
            "id",
            "nomi",
            "tavsifi",
            "mahsulot_kategoriyasi",
            "avtomobillar",
            "xususiyatlar",
            "rasmlar",
            "asosiy_rasm"
        ]

    def get_asosiy_rasm(self, obj):
        rasm = obj.rasmlar.filter(asosiy=True).first() or obj.rasmlar.first()
        if rasm:
            request = self.context.get("request")
            return request.build_absolute_uri(rasm.rasm.url)
        return None


class AvtomobilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avtomobil
        fields = ["id", "nomi", "slug"]


class MahsulotKategoriyaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MahsulotKategoriya
        fields = ["id", "nomi", "slug"]