from django.conf.urls import patterns, url
from rec import views

urlpatterns = patterns('',
    url(r'^$',views.index,name="index" ),
    url(r'^each/$',views.each,name="each" ),
    url(r'^vote/$',views.vote,name="vote" ),
    url(r'^uauth/$',views.uauth,name="uauth" ),
)
