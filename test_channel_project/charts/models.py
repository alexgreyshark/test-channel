from django.db import models


class Order(models.Model):
    order = models.IntegerField(
        verbose_name='Заказ №',
        unique=True,
    )
    dollar_cost = models.FloatField(
        verbose_name='Стоимость, $',
    )
    ruble_cost = models.FloatField(
        verbose_name='Стоимость, Р',
    )
    date_finish = models.DateField(
        verbose_name='Дата поставки',
    )

