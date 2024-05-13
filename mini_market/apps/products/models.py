from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Max, Min, Sum

User = get_user_model()


class Category(models.Model):
    """ Модель категорий """

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
        """
        Выдача множества id всех подкатегорий,
        для переданой категории, в полную глубину
         """

        try:
            parent = cls.objects.get(slug=slug)
        except cls.DoesNotExist:
            return None

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
    """ Модель товаров """

    title = models.CharField(verbose_name='Название', max_length=100)
    price = models.DecimalField(
        verbose_name='Цена',
        max_digits=8,
        decimal_places=2,
        validators=(MinValueValidator(0.01),),
    )
    discount_price = models.DecimalField(
        verbose_name='Цена со скидкой',
        max_digits=8,
        decimal_places=2,
        validators=(MinValueValidator(0.01),),
    )
    balance = models.PositiveIntegerField(verbose_name='Остаток')
    description = models.TextField(verbose_name='Описание', default='')
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

    @classmethod
    def get_statistic(cls):
        """
        Возвращает минимальную, максимальную цену и остаток всех товаров
        """
        return cls.objects.aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            total_count=Sum('balance'),
        )


class ShippingCart(models.Model):
    """ Модель корзины """

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
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=1,
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        default_related_name = 'carts'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'product'),
                name='unique_user_product',
            ),
        )

    @classmethod
    def get_data_for_order(cls, user):
        """
        Выдает общую сумму товаров в корзине и общее количество.
        Вторым аргументом словарь с недостающими товарами.
        """
        items = ShippingCart.objects.filter(
            user=user,
        ).select_related('product')

        data = {
            'total_cost': 0,
            'total_count': 0,
        }
        not_enough = {}
        for item in items:
            if item.amount > item.product.balance:
                not_enough[item.product.title] = item.product.balance
            data['total_count'] += item.amount
            data['total_cost'] += item.amount * item.product.price

        return data, not_enough


class Order(models.Model):
    """ Модель заказа """

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

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
