from django import forms

from dcim.models import Region, Site, SiteGroup
from ipam.choices import *
from ipam.constants import *
from ipam.models import *
from ipam.models import ASN
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import (
    add_blank_choice, BulkEditNullBooleanSelect, DatePicker, DynamicModelChoiceField, NumericArrayField, StaticSelect,
    DynamicModelMultipleChoiceField,
)

__all__ = (
    'AggregateBulkEditForm',
    'ASNBulkEditForm',
    'FHRPGroupBulkEditForm',
    'IPAddressBulkEditForm',
    'IPRangeBulkEditForm',
    'PrefixBulkEditForm',
    'RIRBulkEditForm',
    'RoleBulkEditForm',
    'RouteTargetBulkEditForm',
    'ServiceBulkEditForm',
    'ServiceTemplateBulkEditForm',
    'VLANBulkEditForm',
    'VLANGroupBulkEditForm',
    'VRFBulkEditForm',
)


class VRFBulkEditForm(NetBoxModelBulkEditForm):
    tenant = DynamicModelChoiceField(
        label='Учреждение',
        queryset=Tenant.objects.all(),
        required=False
    )
    enforce_unique = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label='Принудительное использование уникального пространства'
    )
    description = forms.CharField(
        label='Описание',
        max_length=100,
        required=False
    )

    model = VRF
    fieldsets = (
        (None, ('tenant', 'enforce_unique', 'description')),
    )
    nullable_fields = ('tenant', 'description')


class RouteTargetBulkEditForm(NetBoxModelBulkEditForm):
    tenant = DynamicModelChoiceField(
        label='Учреждение',
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        label='Описание',
        max_length=200,
        required=False
    )

    model = RouteTarget
    fieldsets = (
        (None, ('tenant', 'description')),
    )
    nullable_fields = ('tenant', 'description')


class RIRBulkEditForm(NetBoxModelBulkEditForm):
    is_private = forms.NullBooleanField(
        label='Частный',
        required=False,
        widget=BulkEditNullBooleanSelect
    )
    description = forms.CharField(
        label='Описание',
        max_length=200,
        required=False
    )

    model = RIR
    fieldsets = (
        (None, ('is_private', 'description')),
    )
    nullable_fields = ('is_private', 'description')


class ASNBulkEditForm(NetBoxModelBulkEditForm):
    sites = DynamicModelMultipleChoiceField(
        label='Адреса',
        queryset=Site.objects.all(),
        required=False
    )
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label='RIR'
    )
    tenant = DynamicModelChoiceField(
        label='Учреждение',
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        label='Описание',
        max_length=100,
        required=False
    )

    model = ASN
    fieldsets = (
        (None, ('sites', 'rir', 'tenant', 'description')),
    )
    nullable_fields = ('date_added', 'description')


class AggregateBulkEditForm(NetBoxModelBulkEditForm):
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label='RIR'
    )
    tenant = DynamicModelChoiceField(
        label='Учреждение',
        queryset=Tenant.objects.all(),
        required=False
    )
    date_added = forms.DateField(
        label='Дата добавления',
        required=False
    )
    description = forms.CharField(
        label='Описание',
        max_length=100,
        required=False
    )

    model = Aggregate
    fieldsets = (
        (None, ('rir', 'tenant', 'date_added', 'description')),
    )
    nullable_fields = ('date_added', 'description')


class RoleBulkEditForm(NetBoxModelBulkEditForm):
    weight = forms.IntegerField(
        label='Вес',
        required=False
    )
    description = forms.CharField(
        label='Описание',
        max_length=200,
        required=False
    )

    model = Role
    fieldsets = (
        (None, ('weight', 'description')),
    )
    nullable_fields = ('description',)


class PrefixBulkEditForm(NetBoxModelBulkEditForm):
    region = DynamicModelChoiceField(
        label='Регион',
        queryset=Region.objects.all(),
        required=False
    )
    site_group = DynamicModelChoiceField(
        label='Группа адресов',
        queryset=SiteGroup.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        label='Адрес',
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    prefix_length = forms.IntegerField(
        label='Длина префикса',
        min_value=PREFIX_LENGTH_MIN,
        max_value=PREFIX_LENGTH_MAX,
        required=False
    )
    tenant = DynamicModelChoiceField(
        label='Учреждение',
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        label='Статус',
        choices=add_blank_choice(PrefixStatusChoices),
        required=False,
        widget=StaticSelect()
    )
    role = DynamicModelChoiceField(
        label='Роль',
        queryset=Role.objects.all(),
        required=False
    )
    is_pool = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label='Это диапазон адресов'
    )
    mark_utilized = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label='Treat as 100% utilized'
    )
    description = forms.CharField(
        label='Описание',
        max_length=100,
        required=False
    )

    model = Prefix
    fieldsets = (
        (None, ('tenant', 'status', 'role', 'description')),
        ('Адрес', ('region', 'site_group', 'site')),
        ('Адресация', ('vrf', 'prefix_length', 'is_pool', 'mark_utilized')),
    )
    nullable_fields = (
        'site', 'vrf', 'tenant', 'role', 'description',
    )


class IPRangeBulkEditForm(NetBoxModelBulkEditForm):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    tenant = DynamicModelChoiceField(
        label='Учреждение',
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        label='Статус',
        choices=add_blank_choice(IPRangeStatusChoices),
        required=False,
        widget=StaticSelect()
    )
    role = DynamicModelChoiceField(
        label='Роль',
        queryset=Role.objects.all(),
        required=False
    )
    description = forms.CharField(
        label='Описание',
        max_length=100,
        required=False
    )

    model = IPRange
    fieldsets = (
        (None, ('status', 'role', 'vrf', 'tenant', 'description')),
    )
    nullable_fields = (
        'vrf', 'tenant', 'role', 'description',
    )


class IPAddressBulkEditForm(NetBoxModelBulkEditForm):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    mask_length = forms.IntegerField(
        label='Длина маски',
        min_value=IPADDRESS_MASK_LENGTH_MIN,
        max_value=IPADDRESS_MASK_LENGTH_MAX,
        required=False
    )
    tenant = DynamicModelChoiceField(
        label='Учреждение',
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        label='Статус',
        choices=add_blank_choice(IPAddressStatusChoices),
        required=False,
        widget=StaticSelect()
    )
    role = forms.ChoiceField(
        label='Роль',
        choices=add_blank_choice(IPAddressRoleChoices),
        required=False,
        widget=StaticSelect()
    )
    dns_name = forms.CharField(
        max_length=255,
        required=False,
        label='DNS name'
    )
    description = forms.CharField(
        label='Описание',
        max_length=100,
        required=False
    )

    model = IPAddress
    fieldsets = (
        (None, ('status', 'role', 'tenant', 'description')),
        ('Адресация', ('vrf', 'mask_length', 'dns_name')),
    )
    nullable_fields = (
        'vrf', 'role', 'tenant', 'dns_name', 'description',
    )


class FHRPGroupBulkEditForm(NetBoxModelBulkEditForm):
    protocol = forms.ChoiceField(
        label='Протокол',
        choices=add_blank_choice(FHRPGroupProtocolChoices),
        required=False,
        widget=StaticSelect()
    )
    group_id = forms.IntegerField(
        min_value=0,
        required=False,
        label='ID Группы'
    )
    auth_type = forms.ChoiceField(
        choices=add_blank_choice(FHRPGroupAuthTypeChoices),
        required=False,
        widget=StaticSelect(),
        label='Тип аутентификации'
    )
    auth_key = forms.CharField(
        max_length=255,
        required=False,
        label='Ключ аутентификации'
    )
    description = forms.CharField(
        label='Описание',
        max_length=200,
        required=False
    )

    model = FHRPGroup
    fieldsets = (
        (None, ('protocol', 'group_id', 'description')),
        ('Authentication', ('auth_type', 'auth_key')),
    )
    nullable_fields = ('auth_type', 'auth_key', 'description')


class VLANGroupBulkEditForm(NetBoxModelBulkEditForm):
    site = DynamicModelChoiceField(
        label='Адрес',
        queryset=Site.objects.all(),
        required=False
    )
    min_vid = forms.IntegerField(
        min_value=VLAN_VID_MIN,
        max_value=VLAN_VID_MAX,
        required=False,
        label='Minimum child VLAN VID'
    )
    max_vid = forms.IntegerField(
        min_value=VLAN_VID_MIN,
        max_value=VLAN_VID_MAX,
        required=False,
        label='Maximum child VLAN VID'
    )
    description = forms.CharField(
        label='Описание',
        max_length=200,
        required=False
    )

    model = VLANGroup
    fieldsets = (
        (None, ('site', 'min_vid', 'max_vid', 'description')),
    )
    nullable_fields = ('site', 'description')


class VLANBulkEditForm(NetBoxModelBulkEditForm):
    region = DynamicModelChoiceField(
        label='Регион',
        queryset=Region.objects.all(),
        required=False
    )
    site_group = DynamicModelChoiceField(
        label='Группа адресов',
        queryset=SiteGroup.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        label='Адрес',
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    group = DynamicModelChoiceField(
        label='Группа',
        queryset=VLANGroup.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    tenant = DynamicModelChoiceField(
        label='Учреждение',
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        label='Статус',
        choices=add_blank_choice(VLANStatusChoices),
        required=False,
        widget=StaticSelect()
    )
    role = DynamicModelChoiceField(
        label='Роль',
        queryset=Role.objects.all(),
        required=False
    )
    description = forms.CharField(
        label='Описание',
        max_length=100,
        required=False
    )

    model = VLAN
    fieldsets = (
        (None, ('status', 'role', 'tenant', 'description')),
        ('Site & Group', ('region', 'site_group', 'site', 'group')),
    )
    nullable_fields = (
        'site', 'group', 'tenant', 'role', 'description',
    )


class ServiceTemplateBulkEditForm(NetBoxModelBulkEditForm):
    protocol = forms.ChoiceField(
        label='Протокол',
        choices=add_blank_choice(ServiceProtocolChoices),
        required=False,
        widget=StaticSelect()
    )
    ports = NumericArrayField(
        label='Порты',
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN,
            max_value=SERVICE_PORT_MAX
        ),
        required=False
    )
    description = forms.CharField(
        label='Описание',
        max_length=100,
        required=False
    )

    model = ServiceTemplate
    fieldsets = (
        (None, ('protocol', 'ports', 'description')),
    )
    nullable_fields = ('description',)


class ServiceBulkEditForm(ServiceTemplateBulkEditForm):
    model = Service
