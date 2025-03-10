from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from dcim.models import BaseInterface, Device
from extras.models import ConfigContextModel
from extras.querysets import ConfigContextModelQuerySet
from netbox.config import get_config
from netbox.models import OrganizationalModel, NetBoxModel
from utilities.fields import NaturalOrderingField
from utilities.ordering import naturalize_interface
from utilities.query_functions import CollateAsChar
from .choices import *

__all__ = (
    'Cluster',
    'ClusterGroup',
    'ClusterType',
    'VirtualMachine',
    'VMInterface',
)


#
# Cluster types
#

class ClusterType(OrganizationalModel):
    """
    A type of Cluster.
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
        blank=True
    )

    class Meta:
        verbose_name = "Тип кластеров"
        verbose_name_plural = "Типы кластеров"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:clustertype', args=[self.pk])


#
# Cluster groups
#

class ClusterGroup(OrganizationalModel):
    """
    An organizational group of Clusters.
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
        blank=True
    )

    # Generic relations
    vlan_groups = GenericRelation(
        to='ipam.VLANGroup',
        content_type_field='scope_type',
        object_id_field='scope_id',
        related_query_name='cluster_group'
    )
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    class Meta:
        verbose_name = "Группа кластеров"
        verbose_name_plural = "Группы кластеров"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:clustergroup', args=[self.pk])


#
# Clusters
#

class Cluster(NetBoxModel):
    """
    A cluster of VirtualMachines. Each Cluster may optionally be associated with one or more Devices.
    """
    name = models.CharField(
        verbose_name = "название",
        max_length=100
    )
    type = models.ForeignKey(
        verbose_name = "тип",
        to=ClusterType,
        on_delete=models.PROTECT,
        related_name='clusters'
    )
    group = models.ForeignKey(
        verbose_name = "Группа",
        to=ClusterGroup,
        on_delete=models.PROTECT,
        related_name='clusters',
        blank=True,
        null=True
    )
    tenant = models.ForeignKey(
        verbose_name = "учреждение",
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='clusters',
        blank=True,
        null=True
    )
    site = models.ForeignKey(
        verbose_name = "адрес",
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='clusters',
        blank=True,
        null=True
    )
    comments = models.TextField(
        verbose_name = "комментарий",
        blank=True
    )

    # Generic relations
    vlan_groups = GenericRelation(
        to='ipam.VLANGroup',
        content_type_field='scope_type',
        object_id_field='scope_id',
        related_query_name='cluster'
    )
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    clone_fields = [
        'type', 'group', 'tenant', 'site',
    ]

    class Meta:
        verbose_name = "Кластер"
        verbose_name_plural = "Кластеры"
        ordering = ['name']
        unique_together = (
            ('group', 'name'),
            ('site', 'name'),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:cluster', args=[self.pk])

    def clean(self):
        super().clean()

        # If the Cluster is assigned to a Site, verify that all host Devices belong to that Site.
        if self.pk and self.site:
            nonsite_devices = Device.objects.filter(cluster=self).exclude(site=self.site).count()
            if nonsite_devices:
                raise ValidationError({
                    'site': "{} devices are assigned as hosts for this cluster but are not in site {}".format(
                        nonsite_devices, self.site
                    )
                })


#
# Virtual machines
#

class VirtualMachine(NetBoxModel, ConfigContextModel):
    """
    A virtual machine which runs inside a Cluster.
    """
    cluster = models.ForeignKey(
        verbose_name = "кластер",
        to='virtualization.Cluster',
        on_delete=models.PROTECT,
        related_name='virtual_machines'
    )
    tenant = models.ForeignKey(
        verbose_name = "учреждение",
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='virtual_machines',
        blank=True,
        null=True
    )
    platform = models.ForeignKey(
        verbose_name = "платформа",
        to='dcim.Platform',
        on_delete=models.SET_NULL,
        related_name='virtual_machines',
        blank=True,
        null=True
    )
    name = models.CharField(
        verbose_name = "название",
        max_length=64
    )
    _name = NaturalOrderingField(
        verbose_name = "название",
        target_field='name',
        max_length=100,
        blank=True
    )
    status = models.CharField(
        max_length=50,
        choices=VirtualMachineStatusChoices,
        default=VirtualMachineStatusChoices.STATUS_ACTIVE,
        verbose_name='Статус'
    )
    role = models.ForeignKey(
        to='dcim.DeviceRole',
        on_delete=models.PROTECT,
        related_name='virtual_machines',
        limit_choices_to={'vm_role': True},
        blank=True,
        null=True
    )
    primary_ip4 = models.OneToOneField(
        to='ipam.IPAddress',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
        verbose_name='Первичный IPv4 адрес'
    )
    primary_ip6 = models.OneToOneField(
        to='ipam.IPAddress',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
        verbose_name='Первичный IPv6 адрес'
    )
    vcpus = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Виртульный CPU',
        validators=(
            MinValueValidator(0.01),
        )
    )
    memory = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Память (ГБ)'
    )
    disk = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Диск ГБ'
    )
    comments = models.TextField(
        verbose_name = "комментарий",
        blank=True
    )

    # Generic relation
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    objects = ConfigContextModelQuerySet.as_manager()

    clone_fields = [
        'cluster', 'tenant', 'platform', 'status', 'role', 'vcpus', 'memory', 'disk',
    ]

    class Meta:
        verbose_name = "Виртуальная машина"
        verbose_name_plural = "Виртуальные машины"
        ordering = ('_name', 'pk')  # Name may be non-unique
        unique_together = [
            ['cluster', 'tenant', 'name']
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:virtualmachine', args=[self.pk])

    def validate_unique(self, exclude=None):

        # Check for a duplicate name on a VM assigned to the same Cluster and no Tenant. This is necessary
        # because Django does not consider two NULL fields to be equal, and thus will not trigger a violation
        # of the uniqueness constraint without manual intervention.
        if self.tenant is None and VirtualMachine.objects.exclude(pk=self.pk).filter(
                name=self.name, cluster=self.cluster, tenant__isnull=True
        ):
            raise ValidationError({
                'name': 'A virtual machine with this name already exists in the assigned cluster.'
            })

        super().validate_unique(exclude)

    def clean(self):
        super().clean()

        # Validate primary IP addresses
        interfaces = self.interfaces.all()
        for field in ['primary_ip4', 'primary_ip6']:
            ip = getattr(self, field)
            if ip is not None:
                if ip.assigned_object in interfaces:
                    pass
                elif ip.nat_inside is not None and ip.nat_inside.assigned_object in interfaces:
                    pass
                else:
                    raise ValidationError({
                        field: f"The specified IP address ({ip}) is not assigned to this VM.",
                    })

    def get_status_color(self):
        return VirtualMachineStatusChoices.colors.get(self.status)

    @property
    def primary_ip(self):
        if get_config().PREFER_IPV4 and self.primary_ip4:
            return self.primary_ip4
        elif self.primary_ip6:
            return self.primary_ip6
        elif self.primary_ip4:
            return self.primary_ip4
        else:
            return None

    @property
    def site(self):
        return self.cluster.site


#
# Interfaces
#

class VMInterface(NetBoxModel, BaseInterface):
    virtual_machine = models.ForeignKey(
        verbose_name = "Виртуальная машина",
        to='virtualization.VirtualMachine',
        on_delete=models.CASCADE,
        related_name='interfaces'
    )
    name = models.CharField(
        verbose_name = "название",
        max_length=64
    )
    _name = NaturalOrderingField(
        verbose_name = "название",
        target_field='name',
        naturalize_function=naturalize_interface,
        max_length=100,
        blank=True
    )
    description = models.CharField(
        verbose_name = "Описание",
        max_length=200,
        blank=True
    )
    untagged_vlan = models.ForeignKey(
        to='ipam.VLAN',
        on_delete=models.SET_NULL,
        related_name='vminterfaces_as_untagged',
        null=True,
        blank=True,
        verbose_name='Нетегированный VLAN'
    )
    tagged_vlans = models.ManyToManyField(
        to='ipam.VLAN',
        related_name='vminterfaces_as_tagged',
        blank=True,
        verbose_name='Тегированный VLAN'
    )
    ip_addresses = GenericRelation(
        to='ipam.IPAddress',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='vminterface'
    )
    vrf = models.ForeignKey(
        to='ipam.VRF',
        on_delete=models.SET_NULL,
        related_name='vminterfaces',
        null=True,
        blank=True,
        verbose_name='VRF'
    )
    fhrp_group_assignments = GenericRelation(
        to='ipam.FHRPGroupAssignment',
        content_type_field='interface_type',
        object_id_field='interface_id',
        related_query_name='+'
    )

    class Meta:
        verbose_name_plural = "Интерфейсы"
        verbose_name = 'интерфейс'
        ordering = ('virtual_machine', CollateAsChar('_name'))
        unique_together = ('virtual_machine', 'name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:vminterface', kwargs={'pk': self.pk})

    def clean(self):
        super().clean()

        # Parent validation

        # An interface cannot be its own parent
        if self.pk and self.parent_id == self.pk:
            raise ValidationError({'parent': "An interface cannot be its own parent."})

        # An interface's parent must belong to the same virtual machine
        if self.parent and self.parent.virtual_machine != self.virtual_machine:
            raise ValidationError({
                'parent': f"The selected parent interface ({self.parent}) belongs to a different virtual machine "
                          f"({self.parent.virtual_machine})."
            })

        # Bridge validation

        # An interface cannot be bridged to itself
        if self.pk and self.bridge_id == self.pk:
            raise ValidationError({'bridge': "An interface cannot be bridged to itself."})

        # A bridged interface belong to the same virtual machine
        if self.bridge and self.bridge.virtual_machine != self.virtual_machine:
            raise ValidationError({
                'bridge': f"The selected bridge interface ({self.bridge}) belongs to a different virtual machine "
                          f"({self.bridge.virtual_machine})."
            })

        # VLAN validation

        # Validate untagged VLAN
        if self.untagged_vlan and self.untagged_vlan.site not in [self.virtual_machine.site, None]:
            raise ValidationError({
                'untagged_vlan': f"The untagged VLAN ({self.untagged_vlan}) must belong to the same site as the "
                                 f"interface's parent virtual machine, or it must be global."
            })

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.virtual_machine
        return objectchange

    @property
    def parent_object(self):
        return self.virtual_machine
