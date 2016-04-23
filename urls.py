from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$',  views.register, name='register'),
    url(r'^roster/(?P<label>[\w-]{,50})/$',  views.roster, name='roster'),
    #url(r'^assign/(?P<label>[\w-]{,50})/$',  views.assign_roles, name='assign_roles'),
    url(r'^remote/(?P<label>[\w-]{,50})/$',  views.remote, name='remote'),
    url(r'^result/(?P<label>[\w-]{,50})/$',  views.result, name='result'),
    url(r'^newgame/(?P<label>[\w-]{,50})/$',  views.newGame, name='newgame'),
]
