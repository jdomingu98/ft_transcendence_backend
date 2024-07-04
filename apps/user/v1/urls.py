from django.urls import re_path
from .views import Register, LoginView, PasswordResetRequestView

urlpatterns = [
    re_path(r'^register/$', Register.as_view()),
    re_path(r'^login/$', LoginView.as_view()),
    re_path(r'^passResetRequest', PasswordResetRequestView.as_view()),
]