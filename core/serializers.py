from rest_framework import serializers
from .models import Kategoriya, Mahsulot, MahsulotXususiyati, MahsulotRasmi

class MahsulotXususiyatiSerializer(serializers.ModelSerializer):
    class Meta:
        model = MahsulotXususiyati
        fields = ["id", "sarlavha"]

class MahsulotRasmiSerializer(serializers.ModelSerializer):
    class Meta:
        model = MahsulotRasmi
        fields = ['id', 'rasm', 'asosiy']


class MahsulotSerializer(serializers.ModelSerializer):
    rasmlar = MahsulotRasmiSerializer(many=True, read_only=True)
    kategoriyalar = serializers.StringRelatedField(many=True)
    xususiyatlar = MahsulotXususiyatiSerializer(many=True, read_only=True)

    asosiy_rasm = serializers.SerializerMethodField()

    class Meta:
        model = Mahsulot
        fields = [
            'id',
            'nomi',
            'tavsifi',
            'kategoriyalar',
            'xususiyatlar',
            'rasmlar',        # 🔥 barcha rasmlar
            'asosiy_rasm',    # 🔥 frontend uchun qulay
        ]

    def get_asosiy_rasm(self, obj):
        rasm = obj.rasmlar.filter(asosiy=True).first() or obj.rasmlar.first()
        if rasm:
            request = self.context.get('request')
            return request.build_absolute_uri(rasm.rasm.url)
        return None


class KategoriyaSerializer(serializers.ModelSerializer):
    mahsulotlar = MahsulotSerializer(many=True, read_only=True)

    class Meta:
        model = Kategoriya
        fields = ["id", "nomi", "slug", "mahsulotlar"]
