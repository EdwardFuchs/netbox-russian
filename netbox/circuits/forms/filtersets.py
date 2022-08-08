from django import forms
from django.utils.translation import gettext as _

from circuits.choices import CircuitStatusChoices
from circuits.models import *
from dcim.models import Region, Site, SiteGroup
from ipam.models import ASN
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import TenancyFilterForm, ContactModelFilterForm
from utilities.forms import DynamicModelMultipleChoiceField, MultipleChoiceField, TagFilterField

__all__ = (
    'CircuitFilterForm',
    'CircuitTypeFilterForm',
    'ProviderFilterForm',
    'ProviderNetworkFilterForm',
)


class ProviderFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Provider
    fieldsets = (
        (None, ('q', 'tag')),
        ('Метоположение', ('region_id', 'site_group_id', 'site_id')),
        ('ASN', ('asn',)),
        ('Контакты', ('contact', 'contact_role', 'contact_group')),
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label='Регион'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label='Группа адресов'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id',
            'site_group_id': '$site_group_id',
        },
        label='Адрес'
    )
    asn = forms.IntegerField(
        required=False,
        label=_('ASN (legacy)')
    )
    asn_id = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        required=False,
        label='ASNы'
    )
    tag = TagFilterField(model)


class ProviderNetworkFilterForm(NetBoxModelFilterSetForm):
    model = ProviderNetwork
    fieldsets = (
        (None, ('q', 'tag')),
        ('Атрибуты', ('provider_id', 'service_id')),
    )
    provider_id = DynamicModelMultipleChoiceField(
        queryset=Provider.objects.all(),
        required=False,
        label='Поставщик услуг'
    )
    service_id = forms.CharField(
        label='ID',
        max_length=100,
        required=False
    )
    tag = TagFilterField(model)


class CircuitTypeFilterForm(NetBoxModelFilterSetForm):
    model = CircuitType
    tag = TagFilterField(model)


class CircuitFilterForm(TenancyFilterForm, ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Circuit
    fieldsets = (
        (None, ('q', 'tag')),
        ('Поставщик услуг', ('provider_id', 'provider_network_id')),
        ('Атрибуты', ('type_id', 'status', 'commit_rate')),
        ('Метоположение', ('region_id', 'site_group_id', 'site_id')),
        ('Учреждение', ('tenant_group_id', 'tenant_id')),
        ('Контакты', ('contact', 'contact_role', 'contact_group')),
    )
    type_id = DynamicModelMultipleChoiceField(
        queryset=CircuitType.objects.all(),
        required=False,
        label='Тип'
    )
    provider_id = DynamicModelMultipleChoiceField(
        queryset=Provider.objects.all(),
        required=False,
        label='Поставщик услуг'
    )
    provider_network_id = DynamicModelMultipleChoiceField(
        queryset=ProviderNetwork.objects.all(),
        required=False,
        query_params={
            'provider_id': '$provider_id'
        },
        label='Сеть провайдера'
    )
    status = MultipleChoiceField(
        label='Статус',
        choices=CircuitStatusChoices,
        required=False
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label='Регион'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label='Группа адресов'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id',
            'site_group_id': '$site_group_id',
        },
        label='Адрес'
    )
    commit_rate = forms.IntegerField(
        required=False,
        min_value=0,
        label=_('Commit rate (Kbps)')
    )
    tag = TagFilterField(model)
