from django.urls import path

from users.views import RegisterUserView

urlpatterns = [path("register/", view=RegisterUserView.as_view(), name="Register")]
