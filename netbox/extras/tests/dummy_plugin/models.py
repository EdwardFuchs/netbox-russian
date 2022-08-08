from django.db import models


class DummyModel(models.Model):
    name = models.CharField(
        verbose_name = "название",
        max_length=20
    )
    number = models.IntegerField(
        verbose_name = "номер",
        default=100
    )

    class Meta:
        verbose_name = "Dummy Model"
        verbose_name_plural = "Dummy Models"
        ordering = ['name']
