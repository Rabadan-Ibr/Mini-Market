# Generated by Django 5.0.6 on 2024-05-13 01:43

import django.core.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(default='', verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='product',
            name='discount_price',
            field=models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0.01)], verbose_name='Цена со скидкой'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0.01)], verbose_name='Цена'),
        ),
        migrations.AlterField(
            model_name='shippingcart',
            name='amount',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Количество'),
        ),
        migrations.AddConstraint(
            model_name='shippingcart',
            constraint=models.UniqueConstraint(fields=('user', 'product'), name='unique_user_product'),
        ),
    ]
