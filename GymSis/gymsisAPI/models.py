from django.db import models


# Stores the basic data for each user
class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120)
    password = models.CharField(max_length=120)
    weight = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    height = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    chest = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    waist = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    hips = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    thighs = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)


# Stores one gym session for one user
class Session(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")


# Stores the cardio exercise names
class Cardio(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120)


# Links one cardio exercise with one session
class SessionCardio(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    cardio = models.ForeignKey(Cardio, on_delete=models.CASCADE)
    time = models.DecimalField(decimal_places=2, max_digits=20)
    level = models.PositiveIntegerField()
    incline = models.PositiveIntegerField()


# Stores one saved weight exercise for one user
# This is now the main exercise record used by the app.
# The same exercise can be reused in many different sessions.
class UserExercise(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_exercises")
    name = models.CharField(max_length=120)
    # Deleted exercises should stay in the database so the user can still
    # see the progress they made in the past.
    is_active = models.BooleanField(default=True)


# Links one saved weight exercise with one session
# The weight and reps belong to one workout day, but the exercise identity
# comes from UserExercise so the app can track progress over time.
class SessionTraining(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    user_exercise = models.ForeignKey(UserExercise, on_delete=models.CASCADE)
    weight = models.DecimalField(decimal_places=2, max_digits=20)
    reps = models.PositiveIntegerField()


