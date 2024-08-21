from django.urls import path
from .views import Register, LoginView, PasswordResetView, RefreshTokenView, MeView, LogoutView

urlpatterns = [
    path('register/', Register.as_view()),
    path('login/', LoginView.as_view()),
    path('pass-reset', PasswordResetView.as_view()),
    path('refresh/', RefreshTokenView.as_view()),
    path('me/', MeView.as_view()),
    path('logout/', LogoutView.as_view()),
]