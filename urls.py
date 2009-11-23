from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from vortaro.settings import ROOT_FOLDER
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^vortaro/', include('vortaro.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': ROOT_FOLDER+'/media/'}),
    (r'^ajax/epo/eng/(?P<word>[^/]*)/$', 'vortaro.legacy.esperanto.ajax'),
    (r'^register/$', 'vortaro.words.views.register'),
    (r'^login/$', 'vortaro.words.views.logmein'),
    (r'^logout/$', 'vortaro.words.views.logmeout'),
    (r'^about/$', 'vortaro.words.views.about'),
    (r'^$', 'vortaro.words.views.about'),
    (r'^home/$', 'vortaro.words.views.homeview'),
    (r'^home/settings$', 'vortaro.words.views.settings'),
    (r'^data/search$', 'vortaro.words.views.search'),
    
    (r'^data/word$', 'vortaro.words.views.word'),
    (r'^data/word/(?P<id>\d+)$', 'vortaro.words.views.word'),
    
    #(r'^$', 'vortaro.words.views.dictionary'),
    #(r'^(?P<lang>\w*)/$', 'vortaro.words.views.dictionary'),
    #(r'^(?P<lang>\w*)/search$', 'vortaro.words.views.search'),
    #(r'^(?P<url>.*)$', 'vortaro.words.views.url'),
)
