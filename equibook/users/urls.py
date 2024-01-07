from django.urls import path
from .views import LoginView, LogoutView, UserCreationView

app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserCreationView.as_view(), name="register"),
]
