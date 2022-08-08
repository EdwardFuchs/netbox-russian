from django import forms
from django.utils.translation import gettext as _

from dcim.models import DeviceRole, Platform, Region, Site, SiteGroup
from extras.forms import LocalConfigContextFilterForm
from ipam.models import VRF
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import ContactModelFilterForm, TenancyFilterForm
from utilities.forms import (
    DynamicModelMultipleChoiceField, MultipleChoiceField, StaticSelect, TagFilterField, BOOLEAN_WITH_BLANK_CHOICES,
)
from virtualization.choices import *
from virtualization.models import *

__all__ = (
    'ClusterFilterForm',
    'ClusterGroupFilterForm',
    'ClusterTypeFilterForm',
    'VirtualMachineFilterForm',
    'VMInterfaceFilterForm',
)


class ClusterTypeFilterForm(NetBoxModelFilterSetForm):
    model = ClusterType
    tag = TagFilterField(model)


class ClusterGroupFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = ClusterGroup
    tag = TagFilterField(model)
    fieldsets = (
        (None, ('q', 'tag')),
        ('Контакты', ('contact', 'contact_role', 'contact_group')),
    )


class ClusterFilterForm(TenancyFilterForm, ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Cluster
    fieldsets = (
        (None, ('q', 'tag')),
        ('Атрибуты', ('group_id', 'type_id')),
        ('Метоположение', ('region_id', 'site_group_id', 'site_id')),
        ('Учреждение', ('tenant_group_id', 'tenant_id')),
        ('Контакты', ('contact', 'contact_role', 'contact_group')),
    )
    type_id = DynamicModelMultipleChoiceField(
        queryset=ClusterType.objects.all(),
        required=False,
        label='Тип'
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
        null_option='None',
        query_params={
            'region_id': '$region_id',
            'site_group_id': '$site_group_id',
        },
        label='Адрес'
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        null_option='None',
        label='Группа'
    )
    tag = TagFilterField(model)


class VirtualMachineFilterForm(
    LocalConfigContextFilterForm,
    TenancyFilterForm,
    ContactModelFilterForm,
    NetBoxModelFilterSetForm
):
    model = VirtualMachine
    fieldsets = (
        (None, ('q', 'tag')),
        ('Кластер', ('cluster_group_id', 'cluster_type_id', 'cluster_id')),
        ('Метоположение', ('region_id', 'site_group_id', 'site_id')),
        ('Attriubtes', ('status', 'role_id', 'platform_id', 'mac_address', 'has_primary_ip', 'local_context_data')),
        ('Учреждение', ('tenant_group_id', 'tenant_id')),
        ('Контакты', ('contact', 'contact_role', 'contact_group')),
    )
    cluster_group_id = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        null_option='None',
        label='Группа кластера'
    )
    cluster_type_id = DynamicModelMultipleChoiceField(
        queryset=ClusterType.objects.all(),
        required=False,
        null_option='None',
        label='Тип кластера'
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label='Кластер'
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
        null_option='None',
        query_params={
            'region_id': '$region_id',
            'group_id': '$site_group_id',
        },
        label='Адрес'
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'vm_role': "True"
        },
        label='Роль'
    )
    status = MultipleChoiceField(
        label='Статус',
        choices=VirtualMachineStatusChoices,
        required=False
    )
    platform_id = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        null_option='None',
        label='Платформа'
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC адрес'
    )
    has_primary_ip = forms.NullBooleanField(
        required=False,
        label='Имеет первичный IP',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class VMInterfaceFilterForm(NetBoxModelFilterSetForm):
    model = VMInterface
    fieldsets = (
        (None, ('q', 'tag')),
        ('Virtual Machine', ('cluster_id', 'virtual_machine_id')),
        ('Атрибуты', ('enabled', 'mac_address', 'vrf_id')),
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label='Кластер'
    )
    virtual_machine_id = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        query_params={
            'cluster_id': '$cluster_id'
        },
        label='Виртуальная машина'
    )
    enabled = forms.NullBooleanField(
        label='Включен',
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC адрес'
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    tag = TagFilterField(model)
