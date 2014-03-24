from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('qurkexp.join.views',
    (r'^pair/(\d+)/$', 'turk_pair'),
    (r'^features/(\d+)/(\d+)$', 'features'),
    (r'^movie/features/(\d+)/$', 'movie_features'),                       
    (r'^batchpairs/(\d+)$', 'superjoin'),
    (r'^movie/batchpairs/(\d+)$', 'movie_superjoin'),                       
    (r'^sort/(\d+)$', 'sort'),
    (r'^movie/sort/(\d+)$', 'sort'),
    (r'^sorry$', 'sorry'),
)
