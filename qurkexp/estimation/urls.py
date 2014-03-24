from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('qurkexp.estimation.views',
    (r'^counts/(\d+)/$', 'counts'),
    (r'^sorry$', 'sorry'),
)
