from django.conf.urls import url
from django.views.generic import TemplateView
from . import views


urlpatterns = [
    url(r'^confirm_email', TemplateView.as_view(template_name='confirm_email.html')),
    url(r'^register/$', views.RegisterFormView.as_view()),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^$', views.LoginFormView.as_view(), name="login"),
    url(r'^logout/$', views.LogoutView.as_view()),
]