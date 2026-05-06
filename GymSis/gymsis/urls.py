from django.contrib import admin
from django.urls import path
from gymsisAPI.views import login_user, register_session, register_user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', register_user),
    path('login/', login_user),
    path('sessions/register/', register_session),
]
