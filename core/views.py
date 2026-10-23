from rest_framework import viewsets
from .models import Mahsulot, Avtomobil, MahsulotKategoriya
from .serializers import (
    MahsulotSerializer,
    AvtomobilSerializer,
    MahsulotKategoriyaSerializer,
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
                    qs = (Mahsulot.objects.all()
                                      .prefetch_related("rasmlar", "xususiyatlar", "avtomobillar")
                                      .select_related("mahsulot_kategoriyasi"))
                    avtomobil = self.request.query_params.get("avtomobil")
                    kategoriya = self.request.query_params.get("kategoriya")
                    if avtomobil:
                                    qs = qs.filter(avtomobillar__slug=avtomobil)
                                if kategoriya:
                                                qs = qs.filter(mahsulot_kategoriyasi__slug=kategoriya)
                                            return qs.distinct()

    from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Buyurtma
from .serializers import BuyurtmaCreateSerializer, BuyurtmaListSerializer
from .telegram_notify import send_order_notification

class BuyurtmaCreateView(APIView):
        authentication_classes = []
        permission_classes = []
        def post(self, request):
                    serializer = BuyurtmaCreateSerializer(data=request.data)
                    if serializer.is_valid():
                                    buyurtma = serializer.save()
                                    send_order_notification(buyurtma.id)
                                    return Response(
                                        {"id": buyurtma.id, "message": "Buyurtma muvaffaqiyatli qabul qilindi!"},
                                        status=status.HTTP_201_CREATED,
                                    )
                                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                def get(self, request):
                            buyurtmalar = Buyurtma.objects.all()
                            serializer = BuyurtmaListSerializer(buyurtmalar, many=True)
                            return Response(serializer.data)
