from django.contrib import admin
from django.urls import include
from django.urls import path, re_path
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
from django.conf.urls import url


from tourists import views

urlpatterns = [
    path('crm/', include('overview.urls')),
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/admin/'), name='home'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]