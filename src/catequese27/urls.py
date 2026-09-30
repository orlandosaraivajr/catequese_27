from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('nsa_rc/', include('core.urls')),
    path('', include('index.urls')),
]
