from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from circuits.choices import *
from dcim.models import LinkTermination
from netbox.models import ChangeLoggedModel, OrganizationalModel, NetBoxModel
from netbox.models.features import WebhooksMixin

__all__ = (
    'Circuit',
    'CircuitTermination',
    'CircuitType',
)


class CircuitType(OrganizationalModel):
    """
    Circuits can be organized by their functional role. For example, a user might wish to define CircuitTypes named
    "Long Haul," "Metro," or "Out-of-Band".
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
    description = models.CharField(
        verbose_name = "Описание",
        max_length=200,
        blank=True,
    )

    class Meta:
        verbose_name = "Тип цепи"
        verbose_name_plural = "Типы цепи"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('circuits:circuittype', args=[self.pk])


class Circuit(NetBoxModel):
    """
    A communications circuit connects two points. Each Circuit belongs to a Provider; Providers may have multiple
    circuits. Each circuit is also assigned a CircuitType and a Site.  Circuit port speed and commit rate are measured
    in Kbps.
    """
    cid = models.CharField(
        max_length=100,
        verbose_name='Внешний канал (ID)'
    )
    provider = models.ForeignKey(
        verbose_name = "поставщик услуг",
        to='circuits.Provider',
        on_delete=models.PROTECT,
        related_name='circuits'
    )
    type = models.ForeignKey(
        verbose_name = "тип",
        to='CircuitType',
        on_delete=models.PROTECT,
        related_name='circuits'
    )
    status = models.CharField(
        verbose_name = "статус",
        max_length=50,
        choices=CircuitStatusChoices,
        default=CircuitStatusChoices.STATUS_ACTIVE
    )
    tenant = models.ForeignKey(
        verbose_name = "учреждение",
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='circuits',
        blank=True,
        null=True
    )
    install_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата установки'
    )
    commit_rate = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Скорость Мбит/с')
    description = models.CharField(
        verbose_name = "Описание",
        max_length=200,
        blank=True
    )
    comments = models.TextField(
        verbose_name = "комментарий",
        blank=True
    )

    # Generic relations
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    # Cache associated CircuitTerminations
    termination_a = models.ForeignKey(
        to='circuits.CircuitTermination',
        on_delete=models.SET_NULL,
        related_name='+',
        editable=False,
        blank=True,
        null=True
    )
    termination_z = models.ForeignKey(
        to='circuits.CircuitTermination',
        on_delete=models.SET_NULL,
        related_name='+',
        editable=False,
        blank=True,
        null=True
    )

    clone_fields = [
        'provider', 'type', 'status', 'tenant', 'install_date', 'commit_rate', 'description',
    ]

    class Meta:
        verbose_name = "Внешний канал"
        verbose_name_plural = "Каналы"
        ordering = ['provider', 'cid']
        unique_together = ['provider', 'cid']

    def __str__(self):
        return self.cid

    def get_absolute_url(self):
        return reverse('circuits:circuit', args=[self.pk])

    def get_status_color(self):
        return CircuitStatusChoices.colors.get(self.status)


class CircuitTermination(WebhooksMixin, ChangeLoggedModel, LinkTermination):
    circuit = models.ForeignKey(
        verbose_name = "внешний канал",
        to='circuits.Circuit',
        on_delete=models.CASCADE,
        related_name='terminations'
    )
    term_side = models.CharField(
        max_length=1,
        choices=CircuitTerminationSideChoices,
        verbose_name='Подключения'
    )
    site = models.ForeignKey(
        verbose_name = "адрес",
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='circuit_terminations',
        blank=True,
        null=True
    )
    provider_network = models.ForeignKey(
        verbose_name = "Провайдер",
        to='circuits.ProviderNetwork',
        on_delete=models.PROTECT,
        related_name='circuit_terminations',
        blank=True,
        null=True
    )
    port_speed = models.PositiveIntegerField(
        verbose_name='Скорость порта (Мбит/с)',
        blank=True,
        null=True
    )
    upstream_speed = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Скорость потока (Мбит/с)',
        help_text='Upstream speed, if different from port speed'
    )
    xconnect_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Кросс-соединение ID'
    )
    pp_info = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Патч панель/порты'
    )
    description = models.CharField(
        verbose_name = "Описание",
        max_length=200,
        blank=True
    )

    class Meta:
        verbose_name = "Схема"
        verbose_name_plural = "Схемы"
        ordering = ['circuit', 'term_side']
        unique_together = ['circuit', 'term_side']

    def __str__(self):
        return f'Termination {self.term_side}: {self.site or self.provider_network}'

    def get_absolute_url(self):
        if self.site:
            return self.site.get_absolute_url()
        return self.provider_network.get_absolute_url()

    def clean(self):
        super().clean()

        # Must define either site *or* provider network
        if self.site is None and self.provider_network is None:
            raise ValidationError("A circuit termination must attach to either a site or a provider network.")
        if self.site and self.provider_network:
            raise ValidationError("A circuit termination cannot attach to both a site and a provider network.")

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.circuit
        return objectchange

    @property
    def parent_object(self):
        return self.circuit

    def get_peer_termination(self):
        peer_side = 'Z' if self.term_side == 'A' else 'A'
        try:
            return CircuitTermination.objects.prefetch_related('site').get(
                circuit=self.circuit,
                term_side=peer_side
            )
        except CircuitTermination.DoesNotExist:
            return None
