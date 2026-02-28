from rest_framework import viewsets
from .models import Mahsulot, Avtomobil, MahsulotKategoriya
from .serializers import (
    MahsulotSerializer,
    AvtomobilSerializer,
    MahsulotKategoriyaSerializer
)


class AvtomobilViewSet(viewsets.ModelViewSet):
    queryset = Avtomobil.objects.all()
    serializer_class = AvtomobilSerializer


class MahsulotKategoriyaViewSet(viewsets.ModelViewSet):
    queryset = MahsulotKategoriya.objects.all()
    serializer_class = MahsulotKategoriyaSerializer


class MahsulotViewSet(viewsets.ModelViewSet):
    serializer_class = MahsulotSerializer

    def get_queryset(self):
        qs = Mahsulot.objects.all().prefetch_related(
            "rasmlar",
            "xususiyatlar",
            "avtomobillar"
        ).select_related("mahsulot_kategoriyasi")

        avtomobil = self.request.query_params.get("avtomobil")
        kategoriya = self.request.query_params.get("kategoriya")

        if avtomobil:
            qs = qs.filter(avtomobillar__slug=avtomobil)

        if kategoriya:
            qs = qs.filter(mahsulot_kategoriyasi__slug=kategoriya)

        return qs.distinct()