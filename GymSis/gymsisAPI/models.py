from django.db import models


# Stores the basic data for each user
class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120)
    password = models.CharField(max_length=120)
    weight = models.DecimalField(decimal_places=2, max_digits=20)
    height = models.DecimalField(decimal_places=2, max_digits=20)
    chest = models.DecimalField(decimal_places=2, max_digits=20)
    waist = models.DecimalField(decimal_places=2, max_digits=20)
    hips = models.DecimalField(decimal_places=2, max_digits=20)
    thighs = models.DecimalField(decimal_places=2, max_digits=20)


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


# Stores the weight training exercise names
class WeightTraining(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120)


# Links one weight exercise with one session
class SessionTraining(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    training = models.ForeignKey(WeightTraining, on_delete=models.CASCADE)
    weight = models.DecimalField(decimal_places=2, max_digits=20)
    reps = models.PositiveIntegerField()


