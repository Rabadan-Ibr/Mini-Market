from rest_framework import serializers

from apps.products.models import Product


class ProductListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'price', 'discount_price', 'short_description'
        )
