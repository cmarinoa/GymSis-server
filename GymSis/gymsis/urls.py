from django.contrib import admin
from django.urls import path
from gymsisAPI.views import exercises, login_user, measurements, register_user, sessions

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', register_user),
    path('auth/login/', login_user),
    path('sessions/', sessions),
    path('exercises/', exercises),
    path('profile/measurements/', measurements),
]
