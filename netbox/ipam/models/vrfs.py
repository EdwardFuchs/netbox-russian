from django.db import models
from django.urls import reverse

from ipam.constants import *
from netbox.models import NetBoxModel


__all__ = (
    'RouteTarget',
    'VRF',
)


class VRF(NetBoxModel):
    """
    A virtual routing and forwarding (VRF) table represents a discrete layer three forwarding domain (e.g. a routing
    table). Prefixes and IPAddresses can optionally be assigned to VRFs. (Prefixes and IPAddresses not assigned to a VRF
    are said to exist in the "global" table.)
    """
    name = models.CharField(
        verbose_name = "название",
        max_length=100
    )
    rd = models.CharField(
        max_length=VRF_RD_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Route distinguisher',
        help_text='Unique route distinguisher (as defined in RFC 4364)'
    )
    tenant = models.ForeignKey(
        verbose_name = "учреждение",
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='vrfs',
        blank=True,
        null=True
    )
    enforce_unique = models.BooleanField(
        default=True,
        verbose_name='Принудительное использование уникального пространства',
        help_text='Prevent duplicate prefixes/IP addresses within this VRF'
    )
    description = models.CharField(
        verbose_name = "Описание",
        max_length=200,
        blank=True
    )
    import_targets = models.ManyToManyField(
        verbose_name = "Импортировать",
        to='ipam.RouteTarget',
        related_name='importing_vrfs',
        blank=True
    )
    export_targets = models.ManyToManyField(
        verbose_name = "Экспортировать",
        to='ipam.RouteTarget',
        related_name='exporting_vrfs',
        blank=True
    )

    clone_fields = [
        'tenant', 'enforce_unique', 'description',
    ]

    class Meta:
        ordering = ('name', 'rd', 'pk')  # (name, rd) may be non-unique
        verbose_name = 'VRF'
        verbose_name_plural = 'VRF'

    def __str__(self):
        if self.rd:
            return f'{self.name} ({self.rd})'
        return self.name

    def get_absolute_url(self):
        return reverse('ipam:vrf', args=[self.pk])


class RouteTarget(NetBoxModel):
    """
    A BGP extended community used to control the redistribution of routes among VRFs, as defined in RFC 4364.
    """
    name = models.CharField(
        max_length=VRF_RD_MAX_LENGTH,  # Same format options as VRF RD (RFC 4360 section 4)
        unique=True,
        help_text='Route target value (formatted in accordance with RFC 4360)'
    )
    description = models.CharField(
        verbose_name = "Описание",
        max_length=200,
        blank=True
    )
    tenant = models.ForeignKey(
        verbose_name = "учреждение",
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='route_targets',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Цель маршрута"
        verbose_name_plural = "Цели маршрута"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ipam:routetarget', args=[self.pk])
