from django.urls import re_path
from .views import Register, LoginView, LogoutView

urlpatterns = [
    re_path(r'^register/$', Register.as_view()),
    re_path(r'^login/$', LoginView.as_view()),
    re_path(r'^logout/$', LogoutView.as_view()),
]