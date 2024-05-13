from rest_framework import serializers

from apps.products.models import Category, Order, Product


class CategoryBaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'title', 'slug')


class CategoryCreateSerializer(CategoryBaseSerializer):
    pass


class SubCategoryCreateSerializer(CategoryBaseSerializer):

    parent = serializers.SlugRelatedField(
        queryset=Category.objects,
        slug_field='slug',
    )

    class Meta(CategoryBaseSerializer.Meta):
        fields = (*CategoryBaseSerializer.Meta.fields, 'parent')


class CategorySerializer(CategoryBaseSerializer):
    pass


class ProductBaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'price',
            'discount_price',
            'description',
            'short_description',
            'balance',
            'category'
        )


class ProductListSerializer(ProductBaseSerializer):
    category = serializers.StringRelatedField(read_only=True)

    class Meta(ProductBaseSerializer.Meta):
        fields = (
            'id',
            'title',
            'price',
            'discount_price',
            'short_description',
            'category',
        )


class ProductDetailSerializer(ProductBaseSerializer):

    category = CategorySerializer(read_only=True)


class ProductCreateSerializer(ProductBaseSerializer):

    category = serializers.SlugRelatedField(
        queryset=Category.objects,
        slug_field='slug',
    )


class InfoProductsSerializer(serializers.Serializer):

    min_price = serializers.DecimalField(max_digits=8, decimal_places=2)
    max_price = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_count = serializers.IntegerField(min_value=0)


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('quantity', 'total_cost')
