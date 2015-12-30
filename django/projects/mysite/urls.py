import re

from django.conf.urls import include, url
from django.views.static import serve
from django.conf import settings

from catmaid.control.authentication import ObtainAuthToken

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from adminplus.sites import AdminSitePlus
admin.site = AdminSitePlus()
admin.autodiscover()

# CATMAID
urlpatterns = [
    url(r'^', include('catmaid.urls')),
]

# Admin site
urlpatterns += [
    url(r'^admin/', include(admin.site.urls))
]

# API Documentation
urlpatterns += [
    url(r'^apis/', include('rest_framework_swagger.urls')),
    url(r'^api-token-auth/', ObtainAuthToken.as_view()),
]

# Serve static files in debug mode and if explicitely requested
if settings.DEBUG or settings.SERVE_STATIC:
    def serve_static(prefix, root):
        return url(r'^%s(?P<path>.*)$' % re.escape(prefix), serve,
                kwargs={'document_root': root})

    urlpatterns += [
        # General static files
        serve_static('static/', settings.STATIC_ROOT),
        # Access to static extensions in debug mode, remove leading slash.
        serve_static(settings.STATIC_EXTENSION_URL[1:], settings.STATIC_EXTENSION_ROOT),
        # Media files, i.e. cropped images or exports
        serve_static(settings.MEDIA_URL.replace(settings.CATMAID_URL, ''),
            settings.MEDIA_ROOT)
    ]
