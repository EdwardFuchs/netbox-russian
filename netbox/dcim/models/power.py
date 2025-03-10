from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from dcim.choices import *
from dcim.constants import *
from netbox.config import ConfigItem
from netbox.models import NetBoxModel
from utilities.validators import ExclusionValidator
from .device_components import LinkTermination, PathEndpoint

__all__ = (
    'PowerFeed',
    'PowerPanel',
)


#
# Power
#

class PowerPanel(NetBoxModel):
    """
    A distribution point for electrical power; e.g. a data center RPP.
    """
    site = models.ForeignKey(
        verbose_name = "адрес",
        to='Site',
        on_delete=models.PROTECT
    )
    location = models.ForeignKey(
        verbose_name = "расположение",
        to='dcim.Location',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    name = models.CharField(
        verbose_name = "название",
        max_length=100
    )

    # Generic relations
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    class Meta:
        verbose_name = "Силовая панель"
        verbose_name_plural = "Силовая панели"
        ordering = ['site', 'name']
        unique_together = ['site', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:powerpanel', args=[self.pk])

    def clean(self):
        super().clean()

        # Location must belong to assigned Site
        if self.location and self.location.site != self.site:
            raise ValidationError(
                f"Location {self.location} ({self.location.site}) is in a different site than {self.site}"
            )


class PowerFeed(NetBoxModel, PathEndpoint, LinkTermination):
    """
    An electrical circuit delivered from a PowerPanel.
    """
    power_panel = models.ForeignKey(
        verbose_name = "Силовая панель",
        to='PowerPanel',
        on_delete=models.PROTECT,
        related_name='powerfeeds'
    )
    rack = models.ForeignKey(
        verbose_name = "стойка",
        to='Rack',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    name = models.CharField(
        verbose_name = "название",
        max_length=100
    )
    status = models.CharField(
        verbose_name = "статус",
        max_length=50,
        choices=PowerFeedStatusChoices,
        default=PowerFeedStatusChoices.STATUS_ACTIVE
    )
    type = models.CharField(
        verbose_name = "тип",
        max_length=50,
        choices=PowerFeedTypeChoices,
        default=PowerFeedTypeChoices.TYPE_PRIMARY
    )
    supply = models.CharField(
        verbose_name = "тип питания",
        max_length=50,
        choices=PowerFeedSupplyChoices,
        default=PowerFeedSupplyChoices.SUPPLY_AC
    )
    phase = models.CharField(
        verbose_name = "фаза",
        max_length=50,
        choices=PowerFeedPhaseChoices,
        default=PowerFeedPhaseChoices.PHASE_SINGLE
    )
    voltage = models.SmallIntegerField(
        verbose_name = "напряжение",
        default=ConfigItem('POWERFEED_DEFAULT_VOLTAGE'),
        validators=[ExclusionValidator([0])]
    )
    amperage = models.PositiveSmallIntegerField(
        verbose_name = "сила тока",
        validators=[MinValueValidator(1)],
        default=ConfigItem('POWERFEED_DEFAULT_AMPERAGE')
    )
    max_utilization = models.PositiveSmallIntegerField(
        verbose_name = "Максимальное использование",
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        default=ConfigItem('POWERFEED_DEFAULT_MAX_UTILIZATION'),
        help_text="Maximum permissible draw (percentage)"
    )
    available_power = models.PositiveIntegerField(
        verbose_name = "доступная нагрузка",
        default=0,
        editable=False
    )
    comments = models.TextField(
        verbose_name = "комментарий",
        blank=True
    )

    clone_fields = [
        'power_panel', 'rack', 'status', 'type', 'mark_connected', 'supply', 'phase', 'voltage', 'amperage',
        'max_utilization', 'available_power',
    ]

    class Meta:
        verbose_name = "Подача питания"
        verbose_name_plural = "Подача питания"
        ordering = ['power_panel', 'name']
        unique_together = ['power_panel', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:powerfeed', args=[self.pk])

    def clean(self):
        super().clean()

        # Rack must belong to same Site as PowerPanel
        if self.rack and self.rack.site != self.power_panel.site:
            raise ValidationError("Rack {} ({}) and power panel {} ({}) are in different sites".format(
                self.rack, self.rack.site, self.power_panel, self.power_panel.site
            ))

        # AC voltage cannot be negative
        if self.voltage < 0 and self.supply == PowerFeedSupplyChoices.SUPPLY_AC:
            raise ValidationError({
                "voltage": "Voltage cannot be negative for AC supply"
            })

    def save(self, *args, **kwargs):

        # Cache the available_power property on the instance
        kva = abs(self.voltage) * self.amperage * (self.max_utilization / 100)
        if self.phase == PowerFeedPhaseChoices.PHASE_3PHASE:
            self.available_power = round(kva * 1.732)
        else:
            self.available_power = round(kva)

        super().save(*args, **kwargs)

    @property
    def parent_object(self):
        return self.power_panel

    def get_type_color(self):
        return PowerFeedTypeChoices.colors.get(self.type)

    def get_status_color(self):
        return PowerFeedStatusChoices.colors.get(self.status)
