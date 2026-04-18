from django.db import models

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

class Session(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")

class Cardio(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120)


class SessionCardio(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    cardio = models.ForeignKey(Cardio, on_delete=models.CASCADE)
    time = models.DecimalField(decimal_places=2, max_digits=20)
    level = models.PositiveIntegerField()
    incline = models.PositiveIntegerField()

class WeightTraining(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120)

class SessionTraining(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    training = models.ForeignKey(WeightTraining, on_delete=models.CASCADE)
    weight = models.DecimalField(decimal_places=2, max_digits=20)
    reps = models.PositiveIntegerField()


