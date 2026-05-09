from django.contrib import admin
from django.urls import path
from gymsisAPI.views import exercise_detail, exercises, login_user, measurements, register_user, session_detail, sessions

# Main routes used by the desktop app
urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', register_user),
    path('auth/login/', login_user),
    path('sessions/', sessions),
    path('sessions/<int:session_id>/', session_detail),
    path('exercises/', exercises),
    # exercise_id is a string because it includes the type too, for example cardio-3
    path('exercises/<str:exercise_id>/', exercise_detail),
    path('profile/', measurements),
]
