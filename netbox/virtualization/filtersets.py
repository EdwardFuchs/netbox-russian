import django_filters
from django.db.models import Q

from dcim.models import DeviceRole, Platform, Region, Site, SiteGroup
from extras.filtersets import LocalConfigContextFilterSet
from ipam.models import VRF
from netbox.filtersets import OrganizationalModelFilterSet, NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet, ContactModelFilterSet
from utilities.filters import MultiValueMACAddressFilter, TreeNodeMultipleChoiceFilter
from .choices import *
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface

__all__ = (
    'ClusterFilterSet',
    'ClusterGroupFilterSet',
    'ClusterTypeFilterSet',
    'VirtualMachineFilterSet',
    'VMInterfaceFilterSet',
)


class ClusterTypeFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = ClusterType
        fields = ['id', 'name', 'slug', 'description']


class ClusterGroupFilterSet(OrganizationalModelFilterSet, ContactModelFilterSet):

    class Meta:
        model = ClusterGroup
        fields = ['id', 'name', 'slug', 'description']


class ClusterFilterSet(NetBoxModelFilterSet, TenancyFilterSet, ContactModelFilterSet):
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        label='Регион (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        to_field_name='slug',
        label='Регион (slug)',
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        label='Site group (ID)',
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        to_field_name='slug',
        label='Site group (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Адрес (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Адрес (slug)',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ClusterGroup.objects.all(),
        label='Вышестоящая группа (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='group__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label='Вышестоящая группа (slug)',
    )
    type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ClusterType.objects.all(),
        label='Тип кластера (ID)',
    )
    type = django_filters.ModelMultipleChoiceFilter(
        field_name='type__slug',
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        label='Тип кластера (slug)',
    )

    class Meta:
        model = Cluster
        fields = ['id', 'name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(comments__icontains=value)
        )


class VirtualMachineFilterSet(
    NetBoxModelFilterSet,
    TenancyFilterSet,
    ContactModelFilterSet,
    LocalConfigContextFilterSet
):
    status = django_filters.MultipleChoiceFilter(
        choices=VirtualMachineStatusChoices,
        null_value=None
    )
    cluster_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__group',
        queryset=ClusterGroup.objects.all(),
        label='Группа кластеров (ID)',
    )
    cluster_group = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__group__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label='Группа кластеров (slug)',
    )
    cluster_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__type',
        queryset=ClusterType.objects.all(),
        label='Тип кластера (ID)',
    )
    cluster_type = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__type__slug',
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        label='Тип кластера (slug)',
    )
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        label='Кластер (ID)',
    )
    cluster = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__name',
        queryset=Cluster.objects.all(),
        to_field_name='name',
        label='Кластер',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='cluster__site__region',
        lookup_expr='in',
        label='Регион (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='cluster__site__region',
        lookup_expr='in',
        to_field_name='slug',
        label='Регион (slug)',
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='cluster__site__group',
        lookup_expr='in',
        label='Site group (ID)',
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='cluster__site__group',
        lookup_expr='in',
        to_field_name='slug',
        label='Site group (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__site',
        queryset=Site.objects.all(),
        label='Адрес (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Адрес (slug)',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceRole.objects.all(),
        label='Роль (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label='Роль (slug)\"',
    )
    platform_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label='Платформа (ID)',
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        field_name='platform__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label='Платформа (slug)',
    )
    mac_address = MultiValueMACAddressFilter(
        field_name='interfaces__mac_address',
        label='MAC адрес',
    )
    has_primary_ip = django_filters.BooleanFilter(
        method='_has_primary_ip',
        label='Имеет первичный IP',
    )

    class Meta:
        model = VirtualMachine
        fields = ['id', 'name', 'cluster', 'vcpus', 'memory', 'disk']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(comments__icontains=value)
        )

    def _has_primary_ip(self, queryset, name, value):
        params = Q(primary_ip4__isnull=False) | Q(primary_ip6__isnull=False)
        if value:
            return queryset.filter(params)
        return queryset.exclude(params)


class VMInterfaceFilterSet(NetBoxModelFilterSet):
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine__cluster',
        queryset=Cluster.objects.all(),
        label='Кластер (ID)',
    )
    cluster = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine__cluster__name',
        queryset=Cluster.objects.all(),
        to_field_name='name',
        label='Кластер',
    )
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine',
        queryset=VirtualMachine.objects.all(),
        label='Виртуальная машина (ID)',
    )
    virtual_machine = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine__name',
        queryset=VirtualMachine.objects.all(),
        to_field_name='name',
        label='Виртуальная машина',
    )
    parent_id = django_filters.ModelMultipleChoiceFilter(
        field_name='parent',
        queryset=VMInterface.objects.all(),
        label='Parent interface (ID)',
    )
    bridge_id = django_filters.ModelMultipleChoiceFilter(
        field_name='bridge',
        queryset=VMInterface.objects.all(),
        label='Bridged interface (ID)',
    )
    mac_address = MultiValueMACAddressFilter(
        label='MAC адрес',
    )
    vrf_id = django_filters.ModelMultipleChoiceFilter(
        field_name='vrf',
        queryset=VRF.objects.all(),
        label='VRF',
    )
    vrf = django_filters.ModelMultipleChoiceFilter(
        field_name='vrf__rd',
        queryset=VRF.objects.all(),
        to_field_name='rd',
        label='VRF (RD)',
    )

    class Meta:
        model = VMInterface
        fields = ['id', 'name', 'enabled', 'mtu', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
