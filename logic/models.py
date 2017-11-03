from django.db import models
from django.contrib.auth.models import User


class Particle(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Experiment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    particle = models.ForeignKey(Particle, on_delete=models.CASCADE)
    energy = models.FloatField(default=0)
    simulationTime = models.FloatField(default=0)
    frequency = models.FloatField(default=0)

    def __str__(self):
        return self.frequency.__str__()

    def calc(self):
        if self.particle.name == "Electron":
            self.frequency = 500 / self.energy
        else: self.frequency = 100 / self.energy
