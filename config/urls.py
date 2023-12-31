from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('users.urls')),
    path('api/study/', include('studies.urls')),
    path('api/search', include('searches.urls')),
    path('api/social/', include('rankings.urls')),
    path('api/problem/', include('problems.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
