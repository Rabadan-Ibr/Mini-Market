from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import SimpleRouter


urlpatterns = [
    path('v1/auth/', include('djoser.urls')),
    path('v1/auth/', include('djoser.urls.jwt')),
    path('v1/docs/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'v1/docs/swagger/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger',
    ),
]
