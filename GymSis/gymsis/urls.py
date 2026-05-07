from django.contrib import admin
from django.urls import path
from gymsisAPI.views import get_exercises, get_sessions, login_user, register_exercise, register_session, register_user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', register_user),
    path('login/', login_user),
    path('sessions/', get_sessions),
    path('sessions/register/', register_session),
    path('exercises/', get_exercises),
    path('exercises/register/', register_exercise),
]
