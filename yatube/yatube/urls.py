from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'core.views.page_not_found'
handler403 = 'core.views.handler_403'
handler500 = 'core.views.handler_500'

urlpatterns = [
    path('', include('posts.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls'))
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT,
    )
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
