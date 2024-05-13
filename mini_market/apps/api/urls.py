from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import SimpleRouter

from apps.api.views import CategoryViewSet, OrderViewSet, ProductViewSet

router_v1 = SimpleRouter()
router_v1.register('categories', CategoryViewSet)
router_v1.register('products', ProductViewSet)
router_v1.register('orders', OrderViewSet)


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include('djoser.urls')),
    path('v1/auth/', include('djoser.urls.jwt')),
    path('v1/docs/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'v1/docs/swagger/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger',
    ),
]
