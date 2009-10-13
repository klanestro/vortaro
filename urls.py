from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^vortaro/', include('vortaro.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', 'vortaro.words.views.dictionary'),
    (r'^(?P<lang>\w*)/$', 'vortaro.words.views.dictionary'),
    (r'^admin/', include(admin.site.urls)),
    (r'^vortaro/(?P<lang>\w*)/(?P<lang2>\w*)/(?P<word>\w*)$', 'vortaro.words.views.dict'),
    (r'^(?P<lang>\w*)/search$', 'vortaro.words.views.search'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/boroninh/vortaro/media/'}),
    #(r'^(?P<url>.*)$', 'vortaro.words.views.url'),
)
