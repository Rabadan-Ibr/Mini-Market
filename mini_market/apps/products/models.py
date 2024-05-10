from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Category(models.Model):

    title = models.CharField(verbose_name='Название', max_length=50)
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=50,
        unique=True,
    )
    parent = models.ForeignKey(
        'Category',
        verbose_name='Родительская категория',
        on_delete=models.CASCADE,
        related_name='sub_categories',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = 'title',
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title

    @classmethod
    def all_sub_categories(cls, slug):

        try:
            parent = cls.objects.get(slug=slug)
        except cls.DoesNotExist:
            return set()

        result = {parent.id}
        categories = cls.objects.all()

        i = 0
        while i < len(categories):
            if (
                    categories[i].parent_id in result and
                    categories[i].id not in result
            ):
                result.add(categories[i].id)
                i = 0
            i += 1
        return result


class Product(models.Model):

    title = models.CharField(verbose_name='Название', max_length=100)
    price = models.DecimalField(
        verbose_name='Цена',
        max_digits=8,
        decimal_places=2,
    )
    discount_price = models.DecimalField(
        verbose_name='Цена со скидкой',
        max_digits=8,
        decimal_places=2,
    )
    balance = models.PositiveIntegerField(verbose_name='Остаток')
    description = models.TextField(verbose_name='Описание')
    short_description = models.CharField(
        verbose_name='Краткое описание',
        max_length=250,
        default='',
    )
    category = models.ForeignKey(
        'Category',
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = 'title',
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        default_related_name = 'products'

    def __str__(self):
        return self.title


class ShippingCart(models.Model):

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        'Product',
        verbose_name='Товар',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        default_related_name = 'carts'


class Order(models.Model):

    data_created = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        editable=False,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='orders',
        blank=True,
        null=True,
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name='Количество товара',
    )
    total_cost = models.DecimalField(
        verbose_name='Сумма к оплате',
        max_digits=10,
        decimal_places=2,
    )
    is_payed = models.BooleanField(
        verbose_name='Статус оплаты',
        default=False,
    )
    order_id = models.CharField(
        verbose_name='Номер заказа',
        max_length=100,
        null=True,
        blank=True,
    )
    payment_url = models.CharField(
        verbose_name='Ссылка на оплату',
        max_length=100,
        null=True,
        blank=True,
    )

