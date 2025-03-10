import django_filters
from django.db.models import Q

from dcim.filtersets import CableTerminationFilterSet
from dcim.models import Region, Site, SiteGroup
from ipam.models import ASN
from netbox.filtersets import ChangeLoggedModelFilterSet, NetBoxModelFilterSet, OrganizationalModelFilterSet
from tenancy.filtersets import ContactModelFilterSet, TenancyFilterSet
from utilities.filters import TreeNodeMultipleChoiceFilter
from .choices import *
from .models import *

__all__ = (
    'CircuitFilterSet',
    'CircuitTerminationFilterSet',
    'CircuitTypeFilterSet',
    'ProviderNetworkFilterSet',
    'ProviderFilterSet',
)


class ProviderFilterSet(NetBoxModelFilterSet, ContactModelFilterSet):
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='circuits__terminations__site__region',
        lookup_expr='in',
        label='Регион (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='circuits__terminations__site__region',
        lookup_expr='in',
        to_field_name='slug',
        label='Регион (slug)',
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='circuits__terminations__site__group',
        lookup_expr='in',
        label='Site group (ID)',
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='circuits__terminations__site__group',
        lookup_expr='in',
        to_field_name='slug',
        label='Site group (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='circuits__terminations__site',
        queryset=Site.objects.all(),
        label='Адрес',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='circuits__terminations__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Адрес (slug)',
    )
    asn_id = django_filters.ModelMultipleChoiceFilter(
        field_name='asns',
        queryset=ASN.objects.all(),
        label='ASN (ID)',
    )

    class Meta:
        model = Provider
        fields = ['id', 'name', 'slug', 'asn', 'account']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(account__icontains=value) |
            Q(noc_contact__icontains=value) |
            Q(admin_contact__icontains=value) |
            Q(comments__icontains=value)
        )


class ProviderNetworkFilterSet(NetBoxModelFilterSet):
    provider_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Provider.objects.all(),
        label='Поставщик услуг (ID)',
    )
    provider = django_filters.ModelMultipleChoiceFilter(
        field_name='provider__slug',
        queryset=Provider.objects.all(),
        to_field_name='slug',
        label='Поставщик услуг (slug)',
    )

    class Meta:
        model = ProviderNetwork
        fields = ['id', 'name', 'service_id', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(service_id__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        ).distinct()


class CircuitTypeFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = CircuitType
        fields = ['id', 'name', 'slug', 'description']


class CircuitFilterSet(NetBoxModelFilterSet, TenancyFilterSet, ContactModelFilterSet):
    provider_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Provider.objects.all(),
        label='Поставщик услуг (ID)',
    )
    provider = django_filters.ModelMultipleChoiceFilter(
        field_name='provider__slug',
        queryset=Provider.objects.all(),
        to_field_name='slug',
        label='Поставщик услуг (slug)',
    )
    provider_network_id = django_filters.ModelMultipleChoiceFilter(
        field_name='terminations__provider_network',
        queryset=ProviderNetwork.objects.all(),
        label='ProviderNetwork (ID)',
    )
    type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=CircuitType.objects.all(),
        label='Тип внешнего канала (ID)',
    )
    type = django_filters.ModelMultipleChoiceFilter(
        field_name='type__slug',
        queryset=CircuitType.objects.all(),
        to_field_name='slug',
        label='Тип внешнего канала (slug)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=CircuitStatusChoices,
        null_value=None
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='terminations__site__region',
        lookup_expr='in',
        label='Регион (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='terminations__site__region',
        lookup_expr='in',
        to_field_name='slug',
        label='Регион (slug)',
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='terminations__site__group',
        lookup_expr='in',
        label='Site group (ID)',
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='terminations__site__group',
        lookup_expr='in',
        to_field_name='slug',
        label='Site group (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='terminations__site',
        queryset=Site.objects.all(),
        label='Адрес (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='terminations__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Адрес (slug)',
    )

    class Meta:
        model = Circuit
        fields = ['id', 'cid', 'description', 'install_date', 'commit_rate']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(cid__icontains=value) |
            Q(terminations__xconnect_id__icontains=value) |
            Q(terminations__pp_info__icontains=value) |
            Q(terminations__description__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        ).distinct()


class CircuitTerminationFilterSet(ChangeLoggedModelFilterSet, CableTerminationFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Поиск',
    )
    circuit_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Circuit.objects.all(),
        label='Внешний канал',
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
    provider_network_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ProviderNetwork.objects.all(),
        label='ProviderNetwork (ID)',
    )

    class Meta:
        model = CircuitTermination
        fields = ['id', 'term_side', 'port_speed', 'upstream_speed', 'xconnect_id', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(circuit__cid__icontains=value) |
            Q(xconnect_id__icontains=value) |
            Q(pp_info__icontains=value) |
            Q(description__icontains=value)
        ).distinct()
