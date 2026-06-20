from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from studysphere import views as landing_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_views.landing_view, name='landing'),
    path('', include('studysphere.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)