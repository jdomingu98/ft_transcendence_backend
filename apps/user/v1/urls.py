from django.urls import path
from .views import Register, LoginView, PasswordResetView

urlpatterns = [
    path('register/', Register.as_view()),
    path('login/', LoginView.as_view()),
    path('pass-reset', PasswordResetView.as_view()),
]