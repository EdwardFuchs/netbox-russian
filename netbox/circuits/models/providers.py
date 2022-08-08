from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse

from dcim.fields import ASNField
from netbox.models import NetBoxModel

__all__ = (
    'ProviderNetwork',
    'Provider',
)


class Provider(NetBoxModel):
    """
    Each Circuit belongs to a Provider. This is usually a telecommunications company or similar organization. This model
    stores information pertinent to the user's relationship with the Provider.
    """
    name = models.CharField(
        verbose_name = "название",
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        verbose_name = "короткий URL",
        max_length=100,
        unique=True
    )
    asn = ASNField(
        blank=True,
        null=True,
        verbose_name='ASN',
        help_text='32-bit autonomous system number'
    )
    asns = models.ManyToManyField(
        to='ipam.ASN',
        related_name='providers',
        blank=True
    )
    account = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Номер счета'
    )
    portal_url = models.URLField(
        blank=True,
        verbose_name='URL портала'
    )
    noc_contact = models.TextField(
        blank=True,
        verbose_name='Контакты управляющего сетью'
    )
    admin_contact = models.TextField(
        blank=True,
        verbose_name='Контакты администратора'
    )
    comments = models.TextField(
        verbose_name = "комментарий",
        blank=True
    )

    # Generic relations
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    clone_fields = [
        'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact',
    ]

    class Meta:
        verbose_name = "Поставщик услуг"
        verbose_name_plural = "Поставщики услуг"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('circuits:provider', args=[self.pk])


class ProviderNetwork(NetBoxModel):
    """
    This represents a provider network which exists outside of NetBox, the details of which are unknown or
    unimportant to the user.
    """
    name = models.CharField(
        verbose_name = "название",
        max_length=100
    )
    provider = models.ForeignKey(
        verbose_name = "поставщик услуг",
        to='circuits.Provider',
        on_delete=models.PROTECT,
        related_name='networks'
    )
    service_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Service ID'
    )
    description = models.CharField(
        verbose_name = "Описание",
        max_length=200,
        blank=True
    )
    comments = models.TextField(
        verbose_name = "комментарий",
        blank=True
    )

    class Meta:
        verbose_name = "Сеть провайдера"
        verbose_name_plural = "Сети провайдеров"
        ordering = ('provider', 'name')
        constraints = (
            models.UniqueConstraint(
                fields=('provider', 'name'),
                name='circuits_providernetwork_provider_name'
            ),
        )
        unique_together = ('provider', 'name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('circuits:providernetwork', args=[self.pk])
