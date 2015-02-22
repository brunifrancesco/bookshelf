from django.conf.urls import patterns
from django.conf.urls import url

urlpatterns = patterns('',
    url(r'^login$', 'Core.views.login', name='login'),
    url(r'^signup', 'Core.views.signup', name='signup'),
    url(r'^logout', 'Core.views.logout', name='logout'),
    url(r'^about$', 'Core.views.about', name= "about"),
    url(r'^insights$', 'Core.views.insights', name= "insights"),
    url(r'^book/(?P<name>[\w|\W]+)', 'Core.views.book_details'),
    url(r'^book', 'Core.views.book'),
    url(r'^filter', 'Core.views.filter'),
    url(r'^$', 'Core.views.index', name='index'),
)

handler404 = "Core.views.pnf"
handler500 = "Core.views.ise"
