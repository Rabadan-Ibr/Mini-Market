from django.http import Http404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.api.serializers import (CategoryCreateSerializer, CategorySerializer,
                                  InfoProductsSerializer, OrderSerializer,
                                  ProductCreateSerializer,
                                  ProductDetailSerializer,
                                  ProductListSerializer,
                                  SubCategoryCreateSerializer)
from apps.products.models import Category, Order, Product, ShippingCart
from apps.products.tasks import payment


@extend_schema(tags=('Категории',))
@extend_schema_view(
    list=extend_schema(description='Выдача списка категорий'),
    create=extend_schema(description='Создание категории'),
    update=extend_schema(description='Изменение категории'),
    destroy=extend_schema(description='Удаление категории'),
    retrieve=extend_schema(description='Выдача категории по slug'),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = (permissions.IsAdminUser,)

    def get_permissions(self):
        match self.action:
            case 'list' | 'retrieve' | 'products':
                return permissions.AllowAny(),
            case _:
                return permissions.IsAdminUser(),

    def get_queryset(self):
        match self.action:
            case 'products':
                slug = self.kwargs['slug']
                categories = Category.all_sub_categories(slug)
                if categories is None:
                    raise Http404
                self.queryset = Product.objects.filter(
                    category__in=categories,
                ).select_related('category')
            case _: pass
        return self.queryset.all()

    def get_serializer_class(self, *args, **kwargs):
        match self.action:
            case 'create':
                self.serializer_class = CategoryCreateSerializer
            case 'create_sub_category':
                self.serializer_class = SubCategoryCreateSerializer
            case 'products':
                self.serializer_class = ProductListSerializer
            case _:
                self.serializer_class = CategorySerializer

        return self.serializer_class

    @action(('post',), detail=False)
    def create_sub_category(self, request, *args, **kwargs):
        """ Создание подкатегорий """
        return super().create(request)

    @action(('get',), detail=True)
    def products(self, request, slug):
        """ Выдача всех продуктов выбранной категории """
        return super(CategoryViewSet, self).list(request)


@extend_schema(tags=('Продукты',))
@extend_schema_view(
    list=extend_schema(description='Выдача списка товаров'),
    create=extend_schema(description='Создание товара'),
    update=extend_schema(description='Изменение товара'),
    destroy=extend_schema(description='Удаление товара'),
    retrieve=extend_schema(description='Детальная выдача товара'),
)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    pagination_class = PageNumberPagination

    def get_permissions(self):
        match self.action:
            case 'list' | 'retrieve' | 'get_info':
                return permissions.AllowAny(),
            case 'to_cart':
                return permissions.IsAuthenticated(),
            case _:
                return permissions.IsAdminUser(),

    def get_queryset(self):
        match self.action:
            case 'list':
                return Product.objects.select_related('category').all()
            case 'get_info':
                return Product.get_statistic()
            case _:
                return Product.objects.all()

    def get_serializer_class(self):
        match self.action:
            case 'list':
                self.serializer_class = ProductListSerializer
            case 'create':
                self.serializer_class = ProductCreateSerializer
            case 'retrieve':
                self.serializer_class = ProductDetailSerializer
            case 'update' | 'partial_update':
                self.serializer_class = ProductCreateSerializer
            case 'get_info':
                self.serializer_class = InfoProductsSerializer

        return self.serializer_class

    @action(('get',), detail=False)
    def get_info(self, request):
        """ Выдача минимальной цены, максимальной цены и остатка """
        data = self.get_queryset()
        return Response(
            self.get_serializer(data).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        request=None,
        responses={200: None},
        methods=['POST'],
        tags=('Корзина',),
    )
    @action(('post',), detail=True)
    def to_cart(self, request, pk):
        """ Добавление товара в корзину. """
        user = request.user
        product = self.get_object()

        if product.balance < 1:
            raise ValidationError('Not enough amount')

        position, created = ShippingCart.objects.get_or_create(
            product=product, user=user
        )

        if not created:
            position.amount += 1
            position.save()

        return Response(status=status.HTTP_200_OK)


class OrderViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OrderSerializer
    queryset = Order.objects

    @extend_schema(
        request=None,
        responses={201: None},
        methods=['POST'],
        tags=('Заказы',)
    )
    @action(('post',), detail=False)
    def create_order(self, request):
        """ Создание заказа. """

        # Вариант получить данные в один запрос, если смысл задания был в этом
        # Но необходимо так же проверить остаток товара
        # data = ShippingCart.objects.filter(
        #     user=request.user,
        # ).select_related('product').aggregate(
        #     total_count=Sum('amount'),
        #     total_cost=Sum(F('amount') * F('product__price'))
        # )

        data, errors = ShippingCart.get_data_for_order(request.user)
        if len(errors) > 0:
            raise ValidationError(
                f'Max available count for this product: {errors}'
            )

        serializer = self.get_serializer(
            data={
                'quantity': data['total_count'],
                'total_cost': data['total_cost'],
            }
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=request.user)
        request.user.carts.all().delete()

        payment.apply_async((order.id,))
        return Response(status=status.HTTP_201_CREATED)
