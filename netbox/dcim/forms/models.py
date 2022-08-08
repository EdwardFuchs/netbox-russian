from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from timezone_field import TimeZoneFormField

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from ipam.models import ASN, IPAddress, VLAN, VLANGroup, VRF
from netbox.forms import NetBoxModelForm
from tenancy.forms import TenancyForm
from utilities.forms import (
    APISelect, add_blank_choice, BootstrapMixin, ClearableFileInput, CommentField, ContentTypeChoiceField,
    DynamicModelChoiceField, DynamicModelMultipleChoiceField, JSONField, NumericArrayField, SelectWithPK, SmallTextarea,
    SlugField, StaticSelect, SelectSpeedWidget,
)
from virtualization.models import Cluster, ClusterGroup
from wireless.models import WirelessLAN, WirelessLANGroup
from .common import InterfaceCommonForm

__all__ = (
    'CableForm',
    'ConsolePortForm',
    'ConsolePortTemplateForm',
    'ConsoleServerPortForm',
    'ConsoleServerPortTemplateForm',
    'DeviceBayForm',
    'DeviceBayTemplateForm',
    'DeviceForm',
    'DeviceRoleForm',
    'DeviceTypeForm',
    'DeviceVCMembershipForm',
    'FrontPortForm',
    'FrontPortTemplateForm',
    'InterfaceForm',
    'InterfaceTemplateForm',
    'InventoryItemForm',
    'InventoryItemRoleForm',
    'InventoryItemTemplateForm',
    'LocationForm',
    'ManufacturerForm',
    'ModuleForm',
    'ModuleBayForm',
    'ModuleBayTemplateForm',
    'ModuleTypeForm',
    'PlatformForm',
    'PopulateDeviceBayForm',
    'PowerFeedForm',
    'PowerOutletForm',
    'PowerOutletTemplateForm',
    'PowerPanelForm',
    'PowerPortForm',
    'PowerPortTemplateForm',
    'RackForm',
    'RackReservationForm',
    'RackRoleForm',
    'RearPortForm',
    'RearPortTemplateForm',
    'RegionForm',
    'SiteForm',
    'SiteGroupForm',
    'VCMemberSelectForm',
    'VirtualChassisForm',
)

INTERFACE_MODE_HELP_TEXT = """
Access: One untagged VLAN<br />
Tagged: One untagged VLAN and/or one or more tagged VLANs<br />
Tagged (All): Implies all VLANs are available (w/optional untagged VLAN)
"""


class RegionForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    slug = SlugField()

    class Meta:
        verbose_name = "Region Form"
        verbose_name_plural = "Region Forms"
        model = Region
        fields = (
            'parent', 'name', 'slug', 'description', 'tags',
        )


class SiteGroupForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    slug = SlugField()

    class Meta:
        verbose_name = "Site Group Form"
        verbose_name_plural = "Site Group Forms"
        model = SiteGroup
        fields = (
            'parent', 'name', 'slug', 'description', 'tags',
        )


class SiteForm(TenancyForm, NetBoxModelForm):
    region = DynamicModelChoiceField(
        label='Регион',
        queryset=Region.objects.all(),
        required=False
    )
    group = DynamicModelChoiceField(
        label='Группа',
        queryset=SiteGroup.objects.all(),
        required=False
    )
    asns = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        label='ASNы',
        required=False
    )
    slug = SlugField()
    time_zone = TimeZoneFormField(
        label='Временная зона',
        choices=add_blank_choice(TimeZoneFormField().choices),
        required=False,
        widget=StaticSelect()
    )
    comments = CommentField()

    fieldsets = (
        ('Адрес', (
            'name', 'slug', 'status', 'region', 'group', 'facility', 'asns', 'time_zone', 'description', 'tags',
        )),
        ('Учреждения', ('tenant_group', 'tenant')),
        ('Contact Info', ('physical_address', 'shipping_address', 'latitude', 'longitude')),
    )

    class Meta:
        verbose_name = "Site Form"
        verbose_name_plural = "Site Forms"
        model = Site
        fields = (
            'name', 'slug', 'status', 'region', 'group', 'tenant_group', 'tenant', 'facility', 'asns', 'time_zone',
            'description', 'physical_address', 'shipping_address', 'latitude', 'longitude', 'comments', 'tags',
        )
        widgets = {
            'physical_address': SmallTextarea(
                attrs={
                    'rows': 3,
                }
            ),
            'shipping_address': SmallTextarea(
                attrs={
                    'rows': 3,
                }
            ),
            'status': StaticSelect(),
            'time_zone': StaticSelect(),
        }
        help_texts = {
            'name': "Full name of the site",
            'facility': "Data center provider and facility (e.g. Equinix NY7)",
            'time_zone': "Local time zone",
            'description': "Short description (will appear in sites list)",
            'physical_address': "Physical location of the building (e.g. for GPS)",
            'shipping_address': "If different from the physical address",
            'latitude': "Latitude in decimal format (xx.yyyyyy)",
            'longitude': "Longitude in decimal format (xx.yyyyyy)"
        }


class LocationForm(TenancyForm, NetBoxModelForm):
    region = DynamicModelChoiceField(
        label='Регион',
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        label='Группа адресов',
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        label='Адрес',
        queryset=Site.objects.all(),
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    parent = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    slug = SlugField()

    fieldsets = (
        ('Метоположение', (
            'region', 'site_group', 'site', 'parent', 'name', 'slug', 'description', 'tags',
        )),
        ('Учреждения', ('tenant_group', 'tenant')),
    )

    class Meta:
        verbose_name = "Location Form"
        verbose_name_plural = "Location Forms"
        model = Location
        fields = (
            'region', 'site_group', 'site', 'parent', 'name', 'slug', 'description', 'tenant_group', 'tenant', 'tags',
        )


class RackRoleForm(NetBoxModelForm):
    slug = SlugField()

    class Meta:
        verbose_name = "Rack Role Form"
        verbose_name_plural = "Rack Role Forms"
        model = RackRole
        fields = [
            'name', 'slug', 'color', 'description', 'tags',
        ]


class RackForm(TenancyForm, NetBoxModelForm):
    region = DynamicModelChoiceField(
        label='Регион',
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        label='Группа адресов',
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        label='Адрес',
        queryset=Site.objects.all(),
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    location = DynamicModelChoiceField(
        label='Метоположение',
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    role = DynamicModelChoiceField(
        label='Роль',
        queryset=RackRole.objects.all(),
        required=False
    )
    comments = CommentField()

    class Meta:
        verbose_name = "Rack Form"
        verbose_name_plural = "Rack Forms"
        model = Rack
        fields = [
            'region', 'site_group', 'site', 'location', 'name', 'facility_id', 'tenant_group', 'tenant', 'status',
            'role', 'serial', 'asset_tag', 'type', 'width', 'u_height', 'desc_units', 'outer_width', 'outer_depth',
            'outer_unit', 'comments', 'tags',
        ]
        help_texts = {
            'site': "The site at which the rack exists",
            'name': "Organizational rack name",
            'facility_id': "The unique rack ID assigned by the facility",
            'u_height': "Height in rack units",
        }
        widgets = {
            'status': StaticSelect(),
            'type': StaticSelect(),
            'width': StaticSelect(),
            'outer_unit': StaticSelect(),
        }


class RackReservationForm(TenancyForm, NetBoxModelForm):
    region = DynamicModelChoiceField(
        label='Регион',
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        label='Группа адресов',
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
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
    location = DynamicModelChoiceField(
        label='Метоположение',
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    rack = DynamicModelChoiceField(
        label='Стойка',
        queryset=Rack.objects.all(),
        query_params={
            'site_id': '$site',
            'location_id': '$location',
        }
    )
    units = NumericArrayField(
        label='Юниты',
        base_field=forms.IntegerField(),
        help_text="Comma-separated list of numeric unit IDs. A range may be specified using a hyphen."
    )
    user = forms.ModelChoiceField(
        label='Пользователь',
        queryset=User.objects.order_by(
            'username'
        ),
        widget=StaticSelect()
    )

    fieldsets = (
        ('Бронирование', ('region', 'site', 'location', 'rack', 'units', 'user', 'description', 'tags')),
        ('Учреждения', ('tenant_group', 'tenant')),
    )

    class Meta:
        verbose_name = "Rack Reservation Form"
        verbose_name_plural = "Rack Reservation Forms"
        model = RackReservation
        fields = [
            'region', 'site_group', 'site', 'location', 'rack', 'units', 'user', 'tenant_group', 'tenant',
            'description', 'tags',
        ]


class ManufacturerForm(NetBoxModelForm):
    slug = SlugField()

    class Meta:
        verbose_name = "Manufacturer Form"
        verbose_name_plural = "Manufacturer Forms"
        model = Manufacturer
        fields = [
            'name', 'slug', 'description', 'tags',
        ]


class DeviceTypeForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        label='Производитель',
        queryset=Manufacturer.objects.all()
    )
    slug = SlugField(
        label='URL',
        slug_source='model'
    )
    comments = CommentField()

    fieldsets = (
        ('Device Type', (
            'manufacturer', 'model', 'slug', 'part_number', 'tags',
        )),
        ('Chassis', (
            'u_height', 'is_full_depth', 'subdevice_role', 'airflow',
        )),
        ('Images', ('front_image', 'rear_image')),
    )

    class Meta:
        verbose_name = "Device Type Form"
        verbose_name_plural = "Device Type Forms"
        model = DeviceType
        fields = [
            'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role', 'airflow',
            'front_image', 'rear_image', 'comments', 'tags',
        ]
        widgets = {
            'subdevice_role': StaticSelect(),
            'front_image': ClearableFileInput(attrs={
                'accept': DEVICETYPE_IMAGE_FORMATS
            }),
            'rear_image': ClearableFileInput(attrs={
                'accept': DEVICETYPE_IMAGE_FORMATS
            })
        }


class ModuleTypeForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        label='Производитель',
        queryset=Manufacturer.objects.all()
    )
    comments = CommentField()

    fieldsets = (
        ('Module Type', (
            'manufacturer', 'model', 'part_number', 'tags',
        )),
    )

    class Meta:
        verbose_name = "Module Type Form"
        verbose_name_plural = "Module Type Forms"
        model = ModuleType
        fields = [
            'manufacturer', 'model', 'part_number', 'comments', 'tags',
        ]


class DeviceRoleForm(NetBoxModelForm):
    slug = SlugField()

    class Meta:
        verbose_name = "Device Role Form"
        verbose_name_plural = "Device Role Forms"
        model = DeviceRole
        fields = [
            'name', 'slug', 'color', 'vm_role', 'description', 'tags',
        ]


class PlatformForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        label='Производитель',
        queryset=Manufacturer.objects.all(),
        required=False
    )
    slug = SlugField(
        label='URL',
        max_length=64
    )

    class Meta:
        verbose_name = "Platform Form"
        verbose_name_plural = "Platform Forms"
        model = Platform
        fields = [
            'name', 'slug', 'manufacturer', 'napalm_driver', 'napalm_args', 'description', 'tags',
        ]
        widgets = {
            'napalm_args': SmallTextarea(),
        }


class DeviceForm(TenancyForm, NetBoxModelForm):
    region = DynamicModelChoiceField(
        label='Регион',
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        label='Группа адресов',
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        label='Адрес',
        queryset=Site.objects.all(),
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    location = DynamicModelChoiceField(
        label='Метоположение',
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        },
        initial_params={
            'racks': '$rack'
        }
    )
    rack = DynamicModelChoiceField(
        label='Стойка',
        queryset=Rack.objects.all(),
        required=False,
        query_params={
            'site_id': '$site',
            'location_id': '$location',
        }
    )
    position = forms.IntegerField(
        label='Позиция',
        required=False,
        help_text="The lowest-numbered unit occupied by the device",
        widget=APISelect(
            api_url='/api/dcim/racks/{{rack}}/elevation/',
            attrs={
                'disabled-indicator': 'device',
                'data-dynamic-params': '[{"fieldName":"face","queryParam":"face"}]'
            }
        )
    )
    manufacturer = DynamicModelChoiceField(
        label='Производитель',
        queryset=Manufacturer.objects.all(),
        required=False,
        initial_params={
            'device_types': '$device_type'
        }
    )
    device_type = DynamicModelChoiceField(
        label='Тип устройства',
        queryset=DeviceType.objects.all(),
        query_params={
            'manufacturer_id': '$manufacturer'
        }
    )
    device_role = DynamicModelChoiceField(
        label='Роль устройства',
        queryset=DeviceRole.objects.all()
    )
    platform = DynamicModelChoiceField(
        label='Платформа',
        queryset=Platform.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': ['$manufacturer', 'null']
        }
    )
    cluster_group = DynamicModelChoiceField(
        label='Группа кластера',
        queryset=ClusterGroup.objects.all(),
        required=False,
        null_option='None',
        initial_params={
            'clusters': '$cluster'
        }
    )
    cluster = DynamicModelChoiceField(
        label='Кластер',
        queryset=Cluster.objects.all(),
        required=False,
        query_params={
            'group_id': '$cluster_group'
        }
    )
    comments = CommentField()
    local_context_data = JSONField(
        required=False,
        label=''
    )
    virtual_chassis = DynamicModelChoiceField(
        label='Виртуальное шасси',
        queryset=VirtualChassis.objects.all(),
        required=False
    )
    vc_position = forms.IntegerField(
        required=False,
        label='Позиция',
        help_text="The position in the virtual chassis this device is identified by"
    )
    vc_priority = forms.IntegerField(
        required=False,
        label='Priority',
        help_text="The priority of the device in the virtual chassis"
    )

    class Meta:
        verbose_name = "Device Form"
        verbose_name_plural = "Device Forms"
        model = Device
        fields = [
            'name', 'device_role', 'device_type', 'serial', 'asset_tag', 'region', 'site_group', 'site', 'rack',
            'location', 'position', 'face', 'status', 'airflow', 'platform', 'primary_ip4', 'primary_ip6',
            'cluster_group', 'cluster', 'tenant_group', 'tenant', 'virtual_chassis', 'vc_position', 'vc_priority',
            'comments', 'tags', 'local_context_data'
        ]
        help_texts = {
            'device_role': "The function this device serves",
            'serial': "Chassis serial number",
            'local_context_data': "Local config context data overwrites all source contexts in the final rendered "
                                  "config context",
        }
        widgets = {
            'face': StaticSelect(),
            'status': StaticSelect(),
            'airflow': StaticSelect(),
            'primary_ip4': StaticSelect(),
            'primary_ip6': StaticSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:

            # Compile list of choices for primary IPv4 and IPv6 addresses
            for family in [4, 6]:
                ip_choices = [(None, '---------')]

                # Gather PKs of all interfaces belonging to this Device or a peer VirtualChassis member
                interface_ids = self.instance.vc_interfaces(if_master=False).values_list('pk', flat=True)

                # Collect interface IPs
                interface_ips = IPAddress.objects.filter(
                    address__family=family,
                    assigned_object_type=ContentType.objects.get_for_model(Interface),
                    assigned_object_id__in=interface_ids
                ).prefetch_related('assigned_object')
                if interface_ips:
                    ip_list = [(ip.id, f'{ip.address} ({ip.assigned_object})') for ip in interface_ips]
                    ip_choices.append(('Interface IPs', ip_list))
                # Collect NAT IPs
                nat_ips = IPAddress.objects.prefetch_related('nat_inside').filter(
                    address__family=family,
                    nat_inside__assigned_object_type=ContentType.objects.get_for_model(Interface),
                    nat_inside__assigned_object_id__in=interface_ids
                ).prefetch_related('assigned_object')
                if nat_ips:
                    ip_list = [(ip.id, f'{ip.address} (NAT)') for ip in nat_ips]
                    ip_choices.append(('NAT IPs', ip_list))
                self.fields['primary_ip{}'.format(family)].choices = ip_choices

            # If editing an existing device, exclude it from the list of occupied rack units. This ensures that a device
            # can be flipped from one face to another.
            self.fields['position'].widget.add_query_param('exclude', self.instance.pk)

            # Disable rack assignment if this is a child device installed in a parent device
            if self.instance.device_type.is_child_device and hasattr(self.instance, 'parent_bay'):
                self.fields['site'].disabled = True
                self.fields['rack'].disabled = True
                self.initial['site'] = self.instance.parent_bay.device.site_id
                self.initial['rack'] = self.instance.parent_bay.device.rack_id

        else:

            # An object that doesn't exist yet can't have any IPs assigned to it
            self.fields['primary_ip4'].choices = []
            self.fields['primary_ip4'].widget.attrs['readonly'] = True
            self.fields['primary_ip6'].choices = []
            self.fields['primary_ip6'].widget.attrs['readonly'] = True

        # Rack position
        position = self.data.get('position') or self.initial.get('position')
        if position:
            self.fields['position'].widget.choices = [(position, f'U{position}')]


class ModuleForm(NetBoxModelForm):
    device = DynamicModelChoiceField(
        label='Устройство',
        queryset=Device.objects.all(),
        initial_params={
            'modulebays': '$module_bay'
        }
    )
    module_bay = DynamicModelChoiceField(
        label='Модульный отсек',
        queryset=ModuleBay.objects.all(),
        query_params={
            'device_id': '$device'
        }
    )
    manufacturer = DynamicModelChoiceField(
        label='Производитель',
        queryset=Manufacturer.objects.all(),
        required=False,
        initial_params={
            'module_types': '$module_type'
        }
    )
    module_type = DynamicModelChoiceField(
        label='Тип модуля',
        queryset=ModuleType.objects.all(),
        query_params={
            'manufacturer_id': '$manufacturer'
        }
    )
    comments = CommentField()
    replicate_components = forms.BooleanField(
        label='Репликация',
        required=False,
        initial=True,
        help_text="Automatically populate components associated with this module type"
    )

    adopt_components = forms.BooleanField(
        label='Принять',
        required=False,
        initial=False,
        help_text="Adopt already existing components"
    )

    fieldsets = (
        ('Модуль', (
            'device', 'module_bay', 'manufacturer', 'module_type', 'tags',
        )),
        ('Аппаратное обеспечение', (
            'serial', 'asset_tag', 'replicate_components', 'adopt_components',
        )),
    )

    class Meta:
        verbose_name = "Module Form"
        verbose_name_plural = "Module Forms"
        model = Module
        fields = [
            'device', 'module_bay', 'manufacturer', 'module_type', 'serial', 'asset_tag', 'tags',
            'replicate_components', 'adopt_components', 'comments',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['replicate_components'].initial = False
            self.fields['replicate_components'].disabled = True
            self.fields['adopt_components'].initial = False
            self.fields['adopt_components'].disabled = True

    def save(self, *args, **kwargs):

        # If replicate_components is False, disable automatic component replication on the instance
        if self.instance.pk or not self.cleaned_data['replicate_components']:
            self.instance._disable_replication = True

        if self.cleaned_data['adopt_components']:
            self.instance._adopt_components = True

        return super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        replicate_components = self.cleaned_data.get("replicate_components")
        adopt_components = self.cleaned_data.get("adopt_components")
        device = self.cleaned_data['device']
        module_type = self.cleaned_data['module_type']
        module_bay = self.cleaned_data['module_bay']

        # Bail out if we are not installing a new module or if we are not replicating components
        if self.instance.pk or not replicate_components:
            return

        for templates, component_attribute in [
                ("consoleporttemplates", "consoleports"),
                ("consoleserverporttemplates", "consoleserverports"),
                ("interfacetemplates", "interfaces"),
                ("powerporttemplates", "powerports"),
                ("poweroutlettemplates", "poweroutlets"),
                ("rearporttemplates", "rearports"),
                ("frontporttemplates", "frontports")
        ]:
            # Prefetch installed components
            installed_components = {
                component.name: component for component in getattr(device, component_attribute).all()
            }

            # Get the templates for the module type.
            for template in getattr(module_type, templates).all():
                # Installing modules with placeholders require that the bay has a position value
                if MODULE_TOKEN in template.name and not module_bay.position:
                    raise forms.ValidationError(
                        "Cannot install module with placeholder values in a module bay with no position defined"
                    )

                resolved_name = template.name.replace(MODULE_TOKEN, module_bay.position)
                existing_item = installed_components.get(resolved_name)

                # It is not possible to adopt components already belonging to a module
                if adopt_components and existing_item and existing_item.module:
                    raise forms.ValidationError(
                        f"Cannot adopt {template.component_model.__name__} '{resolved_name}' as it already belongs "
                        f"to a module"
                    )

                # If we are not adopting components we error if the component exists
                if not adopt_components and resolved_name in installed_components:
                    raise forms.ValidationError(
                        f"{template.component_model.__name__} - {resolved_name} already exists"
                    )


class CableForm(TenancyForm, NetBoxModelForm):

    class Meta:
        verbose_name = "Cable Form"
        verbose_name_plural = "Cable Forms"
        model = Cable
        fields = [
            'type', 'status', 'tenant_group', 'tenant', 'label', 'color', 'length', 'length_unit', 'tags',
        ]
        widgets = {
            'status': StaticSelect,
            'type': StaticSelect,
            'length_unit': StaticSelect,
        }
        error_messages = {
            'length': {
                'max_value': 'Maximum length is 32767 (any unit)'
            }
        }


class PowerPanelForm(NetBoxModelForm):
    region = DynamicModelChoiceField(
        label='Регион',
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        label='Группа адресов',
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        label='Адрес',
        queryset=Site.objects.all(),
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    location = DynamicModelChoiceField(
        label='Метоположение',
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )

    fieldsets = (
        ('Power Panel', ('region', 'site_group', 'site', 'location', 'name', 'tags')),
    )

    class Meta:
        verbose_name = "Power Panel Form"
        verbose_name_plural = "Power Panel Forms"
        model = PowerPanel
        fields = [
            'region', 'site_group', 'site', 'location', 'name', 'tags',
        ]


class PowerFeedForm(NetBoxModelForm):
    region = DynamicModelChoiceField(
        label='Регион',
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites__powerpanel': '$power_panel'
        }
    )
    site_group = DynamicModelChoiceField(
        label='Группа адресов',
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        label='Адрес',
        queryset=Site.objects.all(),
        required=False,
        initial_params={
            'powerpanel': '$power_panel'
        },
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    power_panel = DynamicModelChoiceField(
        label='Силовая панель',
        queryset=PowerPanel.objects.all(),
        query_params={
            'site_id': '$site'
        }
    )
    rack = DynamicModelChoiceField(
        label='Стойка',
        queryset=Rack.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    comments = CommentField()

    fieldsets = (
        ('Power Panel', ('region', 'site', 'power_panel')),
        ('Power Feed', ('rack', 'name', 'status', 'type', 'mark_connected', 'tags')),
        ('Characteristics', ('supply', 'voltage', 'amperage', 'phase', 'max_utilization')),
    )

    class Meta:
        verbose_name = "Power Feed Form"
        verbose_name_plural = "Power Feed Forms"
        model = PowerFeed
        fields = [
            'region', 'site_group', 'site', 'power_panel', 'rack', 'name', 'status', 'type', 'mark_connected', 'supply',
            'phase', 'voltage', 'amperage', 'max_utilization', 'comments', 'tags',
        ]
        widgets = {
            'status': StaticSelect(),
            'type': StaticSelect(),
            'supply': StaticSelect(),
            'phase': StaticSelect(),
        }


#
# Virtual chassis
#

class VirtualChassisForm(NetBoxModelForm):
    master = forms.ModelChoiceField(
        label='Главный',
        queryset=Device.objects.all(),
        required=False,
    )

    class Meta:
        verbose_name = "Virtual Chassis Form"
        verbose_name_plural = "Virtual Chassis Forms"
        model = VirtualChassis
        fields = [
            'name', 'domain', 'master', 'tags',
        ]
        widgets = {
            'master': SelectWithPK(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['master'].queryset = Device.objects.filter(virtual_chassis=self.instance)


class DeviceVCMembershipForm(forms.ModelForm):
    class Meta:
        verbose_name = "Device VCMembership Form"
        verbose_name_plural = "Device VCMembership Forms"
        model = Device
        fields = [
            'vc_position', 'vc_priority',
        ]
        labels = {
            'vc_position': 'Position',
            'vc_priority': 'Priority',
        }

    def __init__(self, validate_vc_position=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Require VC position (only required when the Device is a VirtualChassis member)
        self.fields['vc_position'].required = True

        # Add bootstrap classes to form elements.
        self.fields['vc_position'].widget.attrs = {'class': 'form-control'}
        self.fields['vc_priority'].widget.attrs = {'class': 'form-control'}

        # Validation of vc_position is optional. This is only required when adding a new member to an existing
        # VirtualChassis. Otherwise, vc_position validation is handled by BaseVCMemberFormSet.
        self.validate_vc_position = validate_vc_position

    def clean_vc_position(self):
        vc_position = self.cleaned_data['vc_position']

        if self.validate_vc_position:
            conflicting_members = Device.objects.filter(
                virtual_chassis=self.instance.virtual_chassis,
                vc_position=vc_position
            )
            if conflicting_members.exists():
                raise forms.ValidationError(
                    'A virtual chassis member already exists in position {}.'.format(vc_position)
                )

        return vc_position


class VCMemberSelectForm(BootstrapMixin, forms.Form):
    region = DynamicModelChoiceField(
        label='Регион',
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        label='Группа адресов',
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
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
    rack = DynamicModelChoiceField(
        label='Стойка',
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site'
        }
    )
    device = DynamicModelChoiceField(
        label='Устройство',
        queryset=Device.objects.all(),
        query_params={
            'site_id': '$site',
            'rack_id': '$rack',
            'virtual_chassis_id': 'null',
        }
    )

    def clean_device(self):
        device = self.cleaned_data['device']
        if device.virtual_chassis is not None:
            raise forms.ValidationError(
                f"Device {device} is already assigned to a virtual chassis."
            )
        return device


#
# Device component templates
#


class ConsolePortTemplateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        verbose_name = "Console Port Template Form"
        verbose_name_plural = "Console Port Template Forms"
        model = ConsolePortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'module_type': forms.HiddenInput(),
            'type': StaticSelect,
        }


class ConsoleServerPortTemplateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        verbose_name = "Console Server Port Template Form"
        verbose_name_plural = "Console Server Port Template Forms"
        model = ConsoleServerPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'module_type': forms.HiddenInput(),
            'type': StaticSelect,
        }


class PowerPortTemplateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        verbose_name = "Power Port Template Form"
        verbose_name_plural = "Power Port Template Forms"
        model = PowerPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'module_type': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class PowerOutletTemplateForm(BootstrapMixin, forms.ModelForm):
    power_port = DynamicModelChoiceField(
        label='Силовой порт',
        queryset=PowerPortTemplate.objects.all(),
        required=False,
        query_params={
            'devicetype_id': '$device_type',
        }
    )

    class Meta:
        verbose_name = "Power Outlet Template Form"
        verbose_name_plural = "Power Outlet Template Forms"
        model = PowerOutletTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'module_type': forms.HiddenInput(),
            'type': StaticSelect(),
            'feed_leg': StaticSelect(),
        }


class InterfaceTemplateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        verbose_name = "Interface Template Form"
        verbose_name_plural = "Interface Template Forms"
        model = InterfaceTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'mgmt_only', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'module_type': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class FrontPortTemplateForm(BootstrapMixin, forms.ModelForm):
    rear_port = DynamicModelChoiceField(
        label='Задний порт',
        queryset=RearPortTemplate.objects.all(),
        required=False,
        query_params={
            'devicetype_id': '$device_type',
        }
    )

    class Meta:
        verbose_name = "Front Port Template Form"
        verbose_name_plural = "Front Port Template Forms"
        model = FrontPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position',
            'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'module_type': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class RearPortTemplateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        verbose_name = "Rear Port Template Form"
        verbose_name_plural = "Rear Port Template Forms"
        model = RearPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'color', 'positions', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'module_type': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class ModuleBayTemplateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        verbose_name = "Module Bay Template Form"
        verbose_name_plural = "Module Bay Template Forms"
        model = ModuleBayTemplate
        fields = [
            'device_type', 'name', 'label', 'position', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class DeviceBayTemplateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        verbose_name = "Device Bay Template Form"
        verbose_name_plural = "Device Bay Template Forms"
        model = DeviceBayTemplate
        fields = [
            'device_type', 'name', 'label', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class InventoryItemTemplateForm(BootstrapMixin, forms.ModelForm):
    parent = DynamicModelChoiceField(
        queryset=InventoryItemTemplate.objects.all(),
        required=False,
        query_params={
            'devicetype_id': '$device_type'
        }
    )
    role = DynamicModelChoiceField(
        label='Роль',
        queryset=InventoryItemRole.objects.all(),
        required=False
    )
    manufacturer = DynamicModelChoiceField(
        label='Производитель',
        queryset=Manufacturer.objects.all(),
        required=False
    )
    component_type = ContentTypeChoiceField(
        label='Тип',
        queryset=ContentType.objects.all(),
        limit_choices_to=MODULAR_COMPONENT_TEMPLATE_MODELS,
        required=False,
        widget=forms.HiddenInput
    )
    component_id = forms.IntegerField(
        label='ID',
        required=False,
        widget=forms.HiddenInput
    )

    class Meta:
        verbose_name = "Inventory Item Template Form"
        verbose_name_plural = "Inventory Item Template Forms"
        model = InventoryItemTemplate
        fields = [
            'device_type', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id', 'description',
            'component_type', 'component_id',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
        }


#
# Device components
#

class ConsolePortForm(NetBoxModelForm):
    module = DynamicModelChoiceField(
        label='Модуль',
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )

    class Meta:
        verbose_name = "Console Port Form"
        verbose_name_plural = "Console Port Forms"
        model = ConsolePort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'speed', 'mark_connected', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
            'speed': StaticSelect(),
        }


class ConsoleServerPortForm(NetBoxModelForm):
    module = DynamicModelChoiceField(
        label='Модуль',
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )

    class Meta:
        verbose_name = "Console Server Port Form"
        verbose_name_plural = "Console Server Port Forms"
        model = ConsoleServerPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'speed', 'mark_connected', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
            'speed': StaticSelect(),
        }


class PowerPortForm(NetBoxModelForm):
    module = DynamicModelChoiceField(
        label='Модуль',
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )

    class Meta:
        verbose_name = "Power Port Form"
        verbose_name_plural = "Power Port Forms"
        model = PowerPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'mark_connected',
            'description',
            'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class PowerOutletForm(NetBoxModelForm):
    module = DynamicModelChoiceField(
        label='Модуль',
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )
    power_port = DynamicModelChoiceField(
        label='Силовой порт',
        queryset=PowerPort.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )

    class Meta:
        verbose_name = "Power Outlet Form"
        verbose_name_plural = "Power Outlet Forms"
        model = PowerOutlet
        fields = [
            'device', 'module', 'name', 'label', 'type', 'power_port', 'feed_leg', 'mark_connected', 'description',
            'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
            'feed_leg': StaticSelect(),
        }


class InterfaceForm(InterfaceCommonForm, NetBoxModelForm):
    module = DynamicModelChoiceField(
        label='Модуль',
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )
    parent = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label='Parent interface',
        query_params={
            'device_id': '$device',
        }
    )
    bridge = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label='Bridged interface',
        query_params={
            'device_id': '$device',
        }
    )
    lag = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label='LAG interface',
        query_params={
            'device_id': '$device',
            'type': 'lag',
        }
    )
    wireless_lan_group = DynamicModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False,
        label='Wireless LAN group'
    )
    wireless_lans = DynamicModelMultipleChoiceField(
        queryset=WirelessLAN.objects.all(),
        required=False,
        label='Wi-fi сети',
        query_params={
            'group_id': '$wireless_lan_group',
        }
    )
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label='Граппа VLAN'
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='Нетегированный VLAN',
        query_params={
            'group_id': '$vlan_group',
            'available_on_device': '$device',
        }
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='Тегированный VLAN',
        query_params={
            'group_id': '$vlan_group',
            'available_on_device': '$device',
        }
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )

    fieldsets = (
        ('Интерфейс', ('device', 'module', 'name', 'type', 'speed', 'duplex', 'label', 'description', 'tags')),
        ('Адресация', ('vrf', 'mac_address', 'wwn')),
        ('Управление', ('mtu', 'tx_power', 'enabled', 'mgmt_only', 'mark_connected')),
        ('Related Interfaces', ('parent', 'bridge', 'lag')),
        ('802.1Q Switching', ('mode', 'vlan_group', 'untagged_vlan', 'tagged_vlans')),
        ('Wi-Fi', (
            'rf_role', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width', 'wireless_lan_group', 'wireless_lans',
        )),
    )

    class Meta:
        verbose_name = "Interface Form"
        verbose_name_plural = "Interface Forms"
        model = Interface
        fields = [
            'device', 'module', 'name', 'label', 'type', 'speed', 'duplex', 'enabled', 'parent', 'bridge', 'lag',
            'mac_address', 'wwn', 'mtu', 'mgmt_only', 'mark_connected', 'description', 'mode', 'rf_role', 'rf_channel',
            'rf_channel_frequency', 'rf_channel_width', 'tx_power', 'wireless_lans', 'untagged_vlan', 'tagged_vlans',
            'vrf', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
            'speed': SelectSpeedWidget(),
            'duplex': StaticSelect(),
            'mode': StaticSelect(),
            'rf_role': StaticSelect(),
            'rf_channel': StaticSelect(),
        }
        labels = {
            'mode': '802.1Q Mode',
        }
        help_texts = {
            'mode': INTERFACE_MODE_HELP_TEXT,
            'rf_channel_frequency': "Populated by selected channel (if set)",
            'rf_channel_width': "Populated by selected channel (if set)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Restrict LAG/bridge interface assignment by device/VC
        device_id = self.data['device'] if self.is_bound else self.initial.get('device')
        device = Device.objects.filter(pk=device_id).first()
        if device and device.virtual_chassis and device.virtual_chassis.master:
            self.fields['lag'].widget.add_query_param('device_id', device.virtual_chassis.master.pk)
            self.fields['bridge'].widget.add_query_param('device_id', device.virtual_chassis.master.pk)


class FrontPortForm(NetBoxModelForm):
    module = DynamicModelChoiceField(
        label='Модуль',
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )
    rear_port = DynamicModelChoiceField(
        label='Задний порт',
        queryset=RearPort.objects.all(),
        query_params={
            'device_id': '$device',
        }
    )

    class Meta:
        verbose_name = "Front Port Form"
        verbose_name_plural = "Front Port Forms"
        model = FrontPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position', 'mark_connected',
            'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class RearPortForm(NetBoxModelForm):
    module = DynamicModelChoiceField(
        label='Модуль',
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )

    class Meta:
        verbose_name = "Rear Port Form"
        verbose_name_plural = "Rear Port Forms"
        model = RearPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'color', 'positions', 'mark_connected', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class ModuleBayForm(NetBoxModelForm):

    class Meta:
        verbose_name = "Module Bay Form"
        verbose_name_plural = "Module Bay Forms"
        model = ModuleBay
        fields = [
            'device', 'name', 'label', 'position', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }


class DeviceBayForm(NetBoxModelForm):

    class Meta:
        verbose_name = "Device Bay Form"
        verbose_name_plural = "Device Bay Forms"
        model = DeviceBay
        fields = [
            'device', 'name', 'label', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }


class PopulateDeviceBayForm(BootstrapMixin, forms.Form):
    installed_device = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        label='Дочернее устройство',
        help_text="Child devices must first be created and assigned to the site/rack of the parent device.",
        widget=StaticSelect(),
    )

    def __init__(self, device_bay, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['installed_device'].queryset = Device.objects.filter(
            site=device_bay.device.site,
            rack=device_bay.device.rack,
            parent_bay__isnull=True,
            device_type__u_height=0,
            device_type__subdevice_role=SubdeviceRoleChoices.ROLE_CHILD
        ).exclude(pk=device_bay.device.pk)


class InventoryItemForm(NetBoxModelForm):
    device = DynamicModelChoiceField(
        label='Устройство',
        queryset=Device.objects.all()
    )
    parent = DynamicModelChoiceField(
        queryset=InventoryItem.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        }
    )
    role = DynamicModelChoiceField(
        label='Роль',
        queryset=InventoryItemRole.objects.all(),
        required=False
    )
    manufacturer = DynamicModelChoiceField(
        label='Производитель',
        queryset=Manufacturer.objects.all(),
        required=False
    )
    component_type = ContentTypeChoiceField(
        label='Тип',
        queryset=ContentType.objects.all(),
        limit_choices_to=MODULAR_COMPONENT_MODELS,
        required=False,
        widget=forms.HiddenInput
    )
    component_id = forms.IntegerField(
        label='ID',
        required=False,
        widget=forms.HiddenInput
    )

    fieldsets = (
        ('Inventory Item', ('device', 'parent', 'name', 'label', 'role', 'description', 'tags')),
        ('Аппаратное обеспечение', ('manufacturer', 'part_id', 'serial', 'asset_tag')),
    )

    class Meta:
        verbose_name = "Inventory Item Form"
        verbose_name_plural = "Inventory Item Forms"
        model = InventoryItem
        fields = [
            'device', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id', 'serial', 'asset_tag',
            'description', 'component_type', 'component_id', 'tags',
        ]


#
# Device component roles
#

class InventoryItemRoleForm(NetBoxModelForm):
    slug = SlugField()

    class Meta:
        verbose_name = "Inventory Item Role Form"
        verbose_name_plural = "Inventory Item Role Forms"
        model = InventoryItemRole
        fields = [
            'name', 'slug', 'color', 'description', 'tags',
        ]
