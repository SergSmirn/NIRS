from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.username, filename)


class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    process_node = models.IntegerField()
    supply_voltage = models.FloatField()
    resistance = models.FloatField(default=1.5e4)
    capacitance = models.FloatField(default=1e-15)

    def __str__(self):
        return '{0}; node: {1}; voltage: {2}, resistance: {3}, capacitance: {4}'.format(self.name, self.process_node, self.supply_voltage, self.resistance, self.capacitance)


class Experiment(models.Model):
    # device
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey(
        Device,
        default=None,
        on_delete=models.CASCADE,
        blank=True
    )

    # models
    par1 = models.FloatField(null=True)
    par2 = models.FloatField(null=True)
    model_type = models.CharField(max_length=10,
                                  choices=(('point', 'Точечная модель'),
                                           ('voltage', 'Модель напряжений')))
    sim_type = models.CharField(max_length=15,
                                choices=(('monte_carlo', 'Монте-Карло'),
                                         ('analytical', 'Аналитический')))

    geometry = models.CharField(max_length=15,
                                choices=(('disc', 'Диск'),
                                         ('sphere', 'Сфера')))

    spectre = ArrayField(ArrayField(models.FloatField()), null=True)
    experimental_data = ArrayField(ArrayField(models.FloatField()), size=2, null=True)

    # phys
    diff_coefficient = models.FloatField(default=12.)
    ambipolar_diff_coefficient = models.FloatField(default=25.)

    # accuracy
    trials_count = models.IntegerField(default=20)
    particles_count = models.IntegerField(default=50000)
    let_values_count = models.IntegerField(default=300)

    # let-cross_section
    simulation_result = ArrayField(ArrayField(models.FloatField()), null=True)

    ser = models.FloatField(null=True)
