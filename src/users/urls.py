from django.urls import include, path

from users.views import LoginUserView, RegisterUserView

base_urlpatterns = [
    path("register/", view=RegisterUserView.as_view(), name="Register"),
    path("login/", view=LoginUserView.as_view(), name="Login"),
]

urlpatterns = [
    path("users/", include(base_urlpatterns)),
]
