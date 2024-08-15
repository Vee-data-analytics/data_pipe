from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('customer/',include('apps.customer.urls')),
    path('data-processing/', include('apps.process_data.urls')),
    path('auth/', include('apps.authentication.urls', namespace='authentication')),
    path('app/', include('apps.app.urls', namespace='app')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_r=settings.STATIC_ROOT)