from rest_framework import viewsets
from openpyxl import Workbook
from .models import TasdiqlovchiSet
from django.http import HttpResponse
from .models import Kategoriya, Mahsulot
from .serializers import KategoriyaSerializer, MahsulotSerializer


class KategoriyaViewSet(viewsets.ModelViewSet):
    queryset = Kategoriya.objects.all()
    serializer_class = KategoriyaSerializer


class MahsulotViewSet(viewsets.ModelViewSet):
    queryset = Mahsulot.objects.all().prefetch_related(
        'rasmlar',
        'kategoriyalar',
        'xususiyatlar'
    )
    serializer_class = MahsulotSerializer



def export_excel(request, set_id):
    tasdiqlovchi_set = TasdiqlovchiSet.objects.get(id=set_id)
    kodlar = tasdiqlovchi_set.kodlar.all()

    wb = Workbook()
    ws = wb.active

    ws.append(["ID", "CODE"])

    for kod in kodlar:
        ws.append([kod.unique_id, kod.code])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = f'attachment; filename=kodlar_{set_id}.xlsx'

    wb.save(response)
    return response