from django.core import serializers
from django.core.paginator import Paginator
from django.shortcuts import (
    redirect,
    render,
)
from .api import check_add
from .models import Order


def home(request):
    """ Вью обновляет данные из GOOGLE SHEETS,
    рендерит шаблон, используя данные из таблицы модели Order
    """
    check_add()
    orders = Order.objects.all().order_by('pk')
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'order_json':serializers.serialize(
            'json',
            orders,
        ),
        'page_obj': page_obj,
    }
    return render(
        request,
        'base.html',
        context,
    )
