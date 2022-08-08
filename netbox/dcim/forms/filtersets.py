from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from extras.forms import LocalConfigContextFilterForm
from ipam.models import ASN, VRF
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import ContactModelFilterForm, TenancyFilterForm
from utilities.forms import (
    APISelectMultiple, add_blank_choice, ColorField, DynamicModelMultipleChoiceField, FilterForm, MultipleChoiceField,
    StaticSelect, TagFilterField, BOOLEAN_WITH_BLANK_CHOICES, SelectSpeedWidget,
)
from wireless.choices import *

__all__ = (
    'CableFilterForm',
    'ConsoleConnectionFilterForm',
    'ConsolePortFilterForm',
    'ConsoleServerPortFilterForm',
    'DeviceBayFilterForm',
    'DeviceFilterForm',
    'DeviceRoleFilterForm',
    'DeviceTypeFilterForm',
    'FrontPortFilterForm',
    'InterfaceConnectionFilterForm',
    'InterfaceFilterForm',
    'InventoryItemFilterForm',
    'InventoryItemRoleFilterForm',
    'LocationFilterForm',
    'ManufacturerFilterForm',
    'ModuleFilterForm',
    'ModuleFilterForm',
    'ModuleBayFilterForm',
    'ModuleTypeFilterForm',
    'PlatformFilterForm',
    'PowerConnectionFilterForm',
    'PowerFeedFilterForm',
    'PowerOutletFilterForm',
    'PowerPanelFilterForm',
    'PowerPortFilterForm',
    'RackFilterForm',
    'RackElevationFilterForm',
    'RackReservationFilterForm',
    'RackRoleFilterForm',
    'RearPortFilterForm',
    'RegionFilterForm',
    'SiteFilterForm',
    'SiteGroupFilterForm',
    'VirtualChassisFilterForm',
)


class DeviceComponentFilterForm(NetBoxModelFilterSetForm):
    name = forms.CharField(
        label='Название',
        required=False
    )
    label = forms.CharField(
        label='Маркировка',
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
            'group_id': '$site_group_id',
        },
        label='Адрес'
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id',
        },
        label='Метоположение'
    )
    virtual_chassis_id = DynamicModelMultipleChoiceField(
        queryset=VirtualChassis.objects.all(),
        required=False,
        label='Виртуальные шасси'
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id',
            'location_id': '$location_id',
            'virtual_chassis_id': '$virtual_chassis_id'
        },
        label='Устройство'
    )


class RegionFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Region
    fieldsets = (
        (None, ('q', 'tag', 'parent_id')),
        ('Contacts', ('contact', 'contact_role', 'contact_group'))
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label='Родительский регион'
    )
    tag = TagFilterField(model)


class SiteGroupFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = SiteGroup
    fieldsets = (
        (None, ('q', 'tag', 'parent_id')),
        ('Contacts', ('contact', 'contact_role', 'contact_group'))
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label='Вышестоящая группа'
    )
    tag = TagFilterField(model)


class SiteFilterForm(TenancyFilterForm, ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Site
    fieldsets = (
        (None, ('q', 'tag')),
        ('Атрибуты', ('status', 'region_id', 'group_id', 'asn_id')),
        ('Учреждение', ('tenant_group_id', 'tenant_id')),
        ('Контакты', ('contact', 'contact_role', 'contact_group')),
    )
    status = MultipleChoiceField(
        label='Статус',
        choices=SiteStatusChoices,
        required=False
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label='Регион'
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label='Группа адресов'
    )
    asn_id = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        required=False,
        label='ASNы'
    )
    tag = TagFilterField(model)


class LocationFilterForm(TenancyFilterForm, ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Location
    fieldsets = (
        (None, ('q', 'tag')),
        ('Родитель', ('region_id', 'site_group_id', 'site_id', 'parent_id')),
        ('Учреждение', ('tenant_group_id', 'tenant_id')),
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
            'group_id': '$site_group_id',
        },
        label='Адрес'
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id',
            'site_id': '$site_id',
        },
        label='Родитель'
    )
    tag = TagFilterField(model)


class RackRoleFilterForm(NetBoxModelFilterSetForm):
    model = RackRole
    tag = TagFilterField(model)


class RackFilterForm(TenancyFilterForm, ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Rack
    fieldsets = (
        (None, ('q', 'tag')),
        ('Метоположение', ('region_id', 'site_group_id', 'site_id', 'location_id')),
        ('Назначение', ('status', 'role_id')),
        ('Аппаратное обеспечение', ('type', 'width', 'serial', 'asset_tag')),
        ('Учреждение', ('tenant_group_id', 'tenant_id')),
        ('Контакты', ('contact', 'contact_role', 'contact_group')),
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label='Регион'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label='Адрес'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label='Группа адресов'
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label='Метоположение'
    )
    status = MultipleChoiceField(
        label='Статус',
        choices=RackStatusChoices,
        required=False
    )
    type = MultipleChoiceField(
        label='Тип',
        choices=RackTypeChoices,
        required=False
    )
    width = MultipleChoiceField(
        label='Ширина',
        choices=RackWidthChoices,
        required=False
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=RackRole.objects.all(),
        required=False,
        null_option='None',
        label='Роль'
    )
    serial = forms.CharField(
        label='Серийный',
        required=False
    )
    asset_tag = forms.CharField(
        label='Тег',
        required=False
    )
    tag = TagFilterField(model)


class RackElevationFilterForm(RackFilterForm):
    id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        label='Стойка',
        required=False,
        query_params={
            'site_id': '$site_id',
            'location_id': '$location_id',
        }
    )


class RackReservationFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = RackReservation
    fieldsets = (
        (None, ('q', 'tag')),
        ('Пользователь', ('user_id',)),
        ('Стойка', ('region_id', 'site_group_id', 'site_id', 'location_id')),
        ('Учреждение', ('tenant_group_id', 'tenant_id')),
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label='Регион'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label='Адрес'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label='Группа адресов'
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.prefetch_related('site'),
        required=False,
        label='Метоположение',
        null_option='None'
    )
    user_id = DynamicModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label='Пользователь',
        widget=APISelectMultiple(
            api_url='/api/users/users/',
        )
    )
    tag = TagFilterField(model)


class ManufacturerFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Manufacturer
    fieldsets = (
        (None, ('q', 'tag')),
        ('Contacts', ('contact', 'contact_role', 'contact_group'))
    )
    tag = TagFilterField(model)


class DeviceTypeFilterForm(NetBoxModelFilterSetForm):
    model = DeviceType
    fieldsets = (
        (None, ('q', 'tag')),
        ('Аппаратное обеспечение', ('manufacturer_id', 'part_number', 'subdevice_role', 'airflow')),
        ('Составные части', (
            'console_ports', 'console_server_ports', 'power_ports', 'power_outlets', 'interfaces',
            'pass_through_ports', 'device_bays', 'module_bays', 'inventory_items',
        )),
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label='Производитель'
    )
    part_number = forms.CharField(
        label='Номер',
        required=False
    )
    subdevice_role = MultipleChoiceField(
        label='Роль подустройства',
        choices=add_blank_choice(SubdeviceRoleChoices),
        required=False
    )
    airflow = MultipleChoiceField(
        label='Поток',
        choices=add_blank_choice(DeviceAirflowChoices),
        required=False
    )
    console_ports = forms.NullBooleanField(
        required=False,
        label='Имеет консольные порты',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_server_ports = forms.NullBooleanField(
        required=False,
        label='Имеет консольные серверные порты',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_ports = forms.NullBooleanField(
        required=False,
        label='Имеет силовые порты',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_outlets = forms.NullBooleanField(
        required=False,
        label='Имеет розетки питания',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    interfaces = forms.NullBooleanField(
        required=False,
        label='Имеет интерфейсы',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    pass_through_ports = forms.NullBooleanField(
        required=False,
        label='Имеет сквозные порты',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    device_bays = forms.NullBooleanField(
        required=False,
        label='Имеет отсеки для устройств',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    module_bays = forms.NullBooleanField(
        required=False,
        label='Имеет модульные отсеки',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    inventory_items = forms.NullBooleanField(
        required=False,
        label='Имеет предметы инвентаря',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class ModuleTypeFilterForm(NetBoxModelFilterSetForm):
    model = ModuleType
    fieldsets = (
        (None, ('q', 'tag')),
        ('Аппаратное обеспечение', ('manufacturer_id', 'part_number')),
        ('Составные части', (
            'console_ports', 'console_server_ports', 'power_ports', 'power_outlets', 'interfaces',
            'pass_through_ports',
        )),
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label='Производитель',
        fetch_trigger='open'
    )
    part_number = forms.CharField(
        label='Номер',
        required=False
    )
    console_ports = forms.NullBooleanField(
        required=False,
        label='Имеет консольные порты',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_server_ports = forms.NullBooleanField(
        required=False,
        label='Имеет консольные серверные порты',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_ports = forms.NullBooleanField(
        required=False,
        label='Имеет силовые порты',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_outlets = forms.NullBooleanField(
        required=False,
        label='Имеет розетки питания',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    interfaces = forms.NullBooleanField(
        required=False,
        label='Имеет интерфейсы',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    pass_through_ports = forms.NullBooleanField(
        required=False,
        label='Имеет сквозные порты',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class DeviceRoleFilterForm(NetBoxModelFilterSetForm):
    model = DeviceRole
    tag = TagFilterField(model)


class PlatformFilterForm(NetBoxModelFilterSetForm):
    model = Platform
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label='Производитель'
    )
    tag = TagFilterField(model)


class DeviceFilterForm(
    LocalConfigContextFilterForm,
    TenancyFilterForm,
    ContactModelFilterForm,
    NetBoxModelFilterSetForm
):
    model = Device
    fieldsets = (
        (None, ('q', 'tag')),
        ('Метоположение', ('region_id', 'site_group_id', 'site_id', 'location_id', 'rack_id')),
        ('Управление', ('status', 'role_id', 'airflow', 'serial', 'asset_tag', 'mac_address')),
        ('Аппаратное обеспечение', ('manufacturer_id', 'device_type_id', 'platform_id')),
        ('Учреждение', ('tenant_group_id', 'tenant_id')),
        ('Контакты', ('contact', 'contact_role', 'contact_group')),
        ('Составные части', (
            'console_ports', 'console_server_ports', 'power_ports', 'power_outlets', 'interfaces', 'pass_through_ports',
        )),
        ('Miscellaneous', ('has_primary_ip', 'virtual_chassis_member', 'local_context_data'))
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
            'group_id': '$site_group_id',
        },
        label='Адрес'
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label='Метоположение'
    )
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id',
            'location_id': '$location_id',
        },
        label='Стойка'
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label='Роль'
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label='Производитель'
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer_id'
        },
        label='Модель'
    )
    platform_id = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        null_option='None',
        label='Платформа'
    )
    status = MultipleChoiceField(
        label='Статус',
        choices=DeviceStatusChoices,
        required=False
    )
    airflow = MultipleChoiceField(
        label='Поток',
        choices=add_blank_choice(DeviceAirflowChoices),
        required=False
    )
    serial = forms.CharField(
        label='Серийный',
        required=False
    )
    asset_tag = forms.CharField(
        label='Тег',
        required=False
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
    virtual_chassis_member = forms.NullBooleanField(
        required=False,
        label='Входит в состав виртуальных шасси',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_ports = forms.NullBooleanField(
        required=False,
        label='Имеет консольные порты',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_server_ports = forms.NullBooleanField(
        required=False,
        label='Имеет консольные серверные порты',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_ports = forms.NullBooleanField(
        required=False,
        label='Имеет силовые порты',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_outlets = forms.NullBooleanField(
        required=False,
        label='Имеет розетки питания',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    interfaces = forms.NullBooleanField(
        required=False,
        label='Имеет интерфейсы',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    pass_through_ports = forms.NullBooleanField(
        required=False,
        label='Имеет сквозные порты',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class ModuleFilterForm(LocalConfigContextFilterForm, TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Module
    fieldsets = (
        (None, ('q', 'tag')),
        ('Аппаратное обеспечение', ('manufacturer_id', 'module_type_id', 'serial', 'asset_tag')),
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label='Производитель',
        fetch_trigger='open'
    )
    module_type_id = DynamicModelMultipleChoiceField(
        queryset=ModuleType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer_id'
        },
        label='Тип',
        fetch_trigger='open'
    )
    serial = forms.CharField(
        label='Серийный',
        required=False
    )
    asset_tag = forms.CharField(
        label='Тег',
        required=False
    )
    tag = TagFilterField(model)


class VirtualChassisFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = VirtualChassis
    fieldsets = (
        (None, ('q', 'tag')),
        ('Метоположение', ('region_id', 'site_group_id', 'site_id')),
        ('Учреждение', ('tenant_group_id', 'tenant_id')),
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
            'group_id': '$site_group_id',
        },
        label='Адрес'
    )
    tag = TagFilterField(model)


class CableFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Cable
    fieldsets = (
        (None, ('q', 'tag')),
        ('Метоположение', ('site_id', 'rack_id', 'device_id')),
        ('Атрибуты', ('type', 'status', 'color', 'length', 'length_unit')),
        ('Учреждение', ('tenant_group_id', 'tenant_id')),
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label='Регион'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label='Адрес'
    )
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label='Стойка',
        null_option='None',
        query_params={
            'site_id': '$site_id'
        }
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id',
            'tenant_id': '$tenant_id',
            'rack_id': '$rack_id',
        },
        label='Устройство'
    )
    type = MultipleChoiceField(
        label='Тип',
        choices=add_blank_choice(CableTypeChoices),
        required=False
    )
    status = MultipleChoiceField(
        label='Статус',
        required=False,
        choices=add_blank_choice(LinkStatusChoices)
    )
    color = ColorField(
        label='Цвет',
        required=False
    )
    length = forms.IntegerField(
        label='Длина',
        required=False
    )
    length_unit = forms.ChoiceField(
        label='Единица длины',
        choices=add_blank_choice(CableLengthUnitChoices),
        required=False
    )
    tag = TagFilterField(model)


class PowerPanelFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = PowerPanel
    fieldsets = (
        (None, ('q', 'tag')),
        ('Метоположение', ('region_id', 'site_group_id', 'site_id', 'location_id')),
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
            'group_id': '$site_group_id',
        },
        label='Адрес'
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label='Метоположение'
    )
    tag = TagFilterField(model)


class PowerFeedFilterForm(NetBoxModelFilterSetForm):
    model = PowerFeed
    fieldsets = (
        (None, ('q', 'tag')),
        ('Метоположение', ('region_id', 'site_group_id', 'site_id', 'power_panel_id', 'rack_id')),
        ('Атрибуты', ('status', 'type', 'supply', 'phase', 'voltage', 'amperage', 'max_utilization')),
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
            'region_id': '$region_id'
        },
        label='Адрес'
    )
    power_panel_id = DynamicModelMultipleChoiceField(
        queryset=PowerPanel.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label='Силовая панель'
    )
    rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site_id'
        },
        label='Стойка'
    )
    status = MultipleChoiceField(
        label='Статус',
        choices=PowerFeedStatusChoices,
        required=False
    )
    type = forms.ChoiceField(
        label='Тип',
        choices=add_blank_choice(PowerFeedTypeChoices),
        required=False,
        widget=StaticSelect()
    )
    supply = forms.ChoiceField(
        label='Поставка',
        choices=add_blank_choice(PowerFeedSupplyChoices),
        required=False,
        widget=StaticSelect()
    )
    phase = forms.ChoiceField(
        label='Фаза',
        choices=add_blank_choice(PowerFeedPhaseChoices),
        required=False,
        widget=StaticSelect()
    )
    voltage = forms.IntegerField(
        label='Напряжение',
        required=False
    )
    amperage = forms.IntegerField(
        label='Ток',
        required=False
    )
    max_utilization = forms.IntegerField(
        label='Максимальное использование',
        required=False
    )
    tag = TagFilterField(model)


#
# Device components
#

class ConsolePortFilterForm(DeviceComponentFilterForm):
    model = ConsolePort
    fieldsets = (
        (None, ('q', 'tag')),
        ('Атрибуты', ('name', 'label', 'type', 'speed')),
        ('Устройство', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    type = MultipleChoiceField(
        label='Тип',
        choices=ConsolePortTypeChoices,
        required=False
    )
    speed = MultipleChoiceField(
        label='Скорость',
        choices=ConsolePortSpeedChoices,
        required=False
    )
    tag = TagFilterField(model)


class ConsoleServerPortFilterForm(DeviceComponentFilterForm):
    model = ConsoleServerPort
    fieldsets = (
        (None, ('q', 'tag')),
        ('Атрибуты', ('name', 'label', 'type', 'speed')),
        ('Устройство', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    type = MultipleChoiceField(
        label='Тип',
        choices=ConsolePortTypeChoices,
        required=False
    )
    speed = MultipleChoiceField(
        label='Скорость',
        choices=ConsolePortSpeedChoices,
        required=False
    )
    tag = TagFilterField(model)


class PowerPortFilterForm(DeviceComponentFilterForm):
    model = PowerPort
    fieldsets = (
        (None, ('q', 'tag')),
        ('Атрибуты', ('name', 'label', 'type')),
        ('Устройство', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    type = MultipleChoiceField(
        label='Тип',
        choices=PowerPortTypeChoices,
        required=False
    )
    tag = TagFilterField(model)


class PowerOutletFilterForm(DeviceComponentFilterForm):
    model = PowerOutlet
    fieldsets = (
        (None, ('q', 'tag')),
        ('Атрибуты', ('name', 'label', 'type')),
        ('Устройство', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    type = MultipleChoiceField(
        label='Тип',
        choices=PowerOutletTypeChoices,
        required=False
    )
    tag = TagFilterField(model)


class InterfaceFilterForm(DeviceComponentFilterForm):
    model = Interface
    fieldsets = (
        (None, ('q', 'tag')),
        ('Атрибуты', ('name', 'label', 'kind', 'type', 'speed', 'duplex', 'enabled', 'mgmt_only')),
        ('Адресация', ('vrf_id', 'mac_address', 'wwn')),
        ('Wi-Fi', ('rf_role', 'rf_channel', 'rf_channel_width', 'tx_power')),
        ('Устройство', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    kind = MultipleChoiceField(
        label='Вид',
        choices=InterfaceKindChoices,
        required=False
    )
    type = MultipleChoiceField(
        label='Тип',
        choices=InterfaceTypeChoices,
        required=False
    )
    speed = forms.IntegerField(
        required=False,
        label='Speed',
        widget=SelectSpeedWidget()
    )
    duplex = MultipleChoiceField(
        label='Двойной',
        choices=InterfaceDuplexChoices,
        required=False
    )
    enabled = forms.NullBooleanField(
        label='Включен',
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    mgmt_only = forms.NullBooleanField(
        label='Только mgmt',
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC адрес'
    )
    wwn = forms.CharField(
        required=False,
        label='WWN'
    )
    rf_role = MultipleChoiceField(
        choices=WirelessRoleChoices,
        required=False,
        label='Роль'
    )
    rf_channel = MultipleChoiceField(
        choices=WirelessChannelChoices,
        required=False,
        label='Канал'
    )
    rf_channel_frequency = forms.IntegerField(
        required=False,
        label='Channel frequency (MHz)'
    )
    rf_channel_width = forms.IntegerField(
        required=False,
        label='Ширина канала (MHz)'
    )
    tx_power = forms.IntegerField(
        required=False,
        label='Мощность (dBm)',
        min_value=0,
        max_value=127
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    tag = TagFilterField(model)


class FrontPortFilterForm(DeviceComponentFilterForm):
    fieldsets = (
        (None, ('q', 'tag')),
        ('Атрибуты', ('name', 'label', 'type', 'color')),
        ('Устройство', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    model = FrontPort
    type = MultipleChoiceField(
        label='Тип',
        choices=PortTypeChoices,
        required=False
    )
    color = ColorField(
        label='Цвет',
        required=False
    )
    tag = TagFilterField(model)


class RearPortFilterForm(DeviceComponentFilterForm):
    model = RearPort
    fieldsets = (
        (None, ('q', 'tag')),
        ('Атрибуты', ('name', 'label', 'type', 'color')),
        ('Устройство', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    type = MultipleChoiceField(
        label='Тип',
        choices=PortTypeChoices,
        required=False
    )
    color = ColorField(
        label='Цвет',
        required=False
    )
    tag = TagFilterField(model)


class ModuleBayFilterForm(DeviceComponentFilterForm):
    model = ModuleBay
    fieldsets = (
        (None, ('q', 'tag')),
        ('Атрибуты', ('name', 'label', 'position')),
        ('Устройство', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    tag = TagFilterField(model)
    position = forms.CharField(
        label='Позиция',
        required=False
    )


class DeviceBayFilterForm(DeviceComponentFilterForm):
    model = DeviceBay
    fieldsets = (
        (None, ('q', 'tag')),
        ('Атрибуты', ('name', 'label')),
        ('Устройство', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    tag = TagFilterField(model)


class InventoryItemFilterForm(DeviceComponentFilterForm):
    model = InventoryItem
    fieldsets = (
        (None, ('q', 'tag')),
        ('Атрибуты', ('name', 'label', 'role_id', 'manufacturer_id', 'serial', 'asset_tag', 'discovered')),
        ('Устройство', ('region_id', 'site_group_id', 'site_id', 'location_id', 'virtual_chassis_id', 'device_id')),
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=InventoryItemRole.objects.all(),
        required=False,
        label='Роль',
        fetch_trigger='open'
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label='Производитель'
    )
    serial = forms.CharField(
        label='Серийный',
        required=False
    )
    asset_tag = forms.CharField(
        label='Тег',
        required=False
    )
    discovered = forms.NullBooleanField(
        label='Обнаруженный',
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


#
# Device component roles
#

class InventoryItemRoleFilterForm(NetBoxModelFilterSetForm):
    model = InventoryItemRole
    tag = TagFilterField(model)


#
# Connections
#

class ConsoleConnectionFilterForm(FilterForm):
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label='Регион'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label='Адрес'
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id'
        },
        label='Устройство'
    )


class PowerConnectionFilterForm(FilterForm):
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label='Регион'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label='Адрес'
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id'
        },
        label='Устройство'
    )


class InterfaceConnectionFilterForm(FilterForm):
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label='Регион'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label='Адрес'
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id'
        },
        label='Устройство'
    )
