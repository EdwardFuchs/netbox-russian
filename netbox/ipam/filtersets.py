import django_filters
import netaddr
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Q
from netaddr.core import AddrFormatError

from dcim.models import Device, Interface, Region, Site, SiteGroup
from netbox.filtersets import ChangeLoggedModelFilterSet, OrganizationalModelFilterSet, NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from utilities.filters import (
    ContentTypeFilter, MultiValueCharFilter, MultiValueNumberFilter, NumericArrayFilter, TreeNodeMultipleChoiceFilter,
)
from virtualization.models import VirtualMachine, VMInterface
from .choices import *
from .models import *


__all__ = (
    'AggregateFilterSet',
    'ASNFilterSet',
    'FHRPGroupAssignmentFilterSet',
    'FHRPGroupFilterSet',
    'IPAddressFilterSet',
    'IPRangeFilterSet',
    'PrefixFilterSet',
    'RIRFilterSet',
    'RoleFilterSet',
    'RouteTargetFilterSet',
    'ServiceFilterSet',
    'ServiceTemplateFilterSet',
    'VLANFilterSet',
    'VLANGroupFilterSet',
    'VRFFilterSet',
)


class VRFFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    import_target_id = django_filters.ModelMultipleChoiceFilter(
        field_name='import_targets',
        queryset=RouteTarget.objects.all(),
        label='Import target',
    )
    import_target = django_filters.ModelMultipleChoiceFilter(
        field_name='import_targets__name',
        queryset=RouteTarget.objects.all(),
        to_field_name='name',
        label='Import target (name)',
    )
    export_target_id = django_filters.ModelMultipleChoiceFilter(
        field_name='export_targets',
        queryset=RouteTarget.objects.all(),
        label='Export target',
    )
    export_target = django_filters.ModelMultipleChoiceFilter(
        field_name='export_targets__name',
        queryset=RouteTarget.objects.all(),
        to_field_name='name',
        label='Export target (name)',
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(rd__icontains=value) |
            Q(description__icontains=value)
        )

    class Meta:
        model = VRF
        fields = ['id', 'name', 'rd', 'enforce_unique', 'description']


class RouteTargetFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    importing_vrf_id = django_filters.ModelMultipleChoiceFilter(
        field_name='importing_vrfs',
        queryset=VRF.objects.all(),
        label='Importing VRF',
    )
    importing_vrf = django_filters.ModelMultipleChoiceFilter(
        field_name='importing_vrfs__rd',
        queryset=VRF.objects.all(),
        to_field_name='rd',
        label='Import VRF (RD)',
    )
    exporting_vrf_id = django_filters.ModelMultipleChoiceFilter(
        field_name='exporting_vrfs',
        queryset=VRF.objects.all(),
        label='Exporting VRF',
    )
    exporting_vrf = django_filters.ModelMultipleChoiceFilter(
        field_name='exporting_vrfs__rd',
        queryset=VRF.objects.all(),
        to_field_name='rd',
        label='Export VRF (RD)',
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )

    class Meta:
        model = RouteTarget
        fields = ['id', 'name', 'description']


class RIRFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = RIR
        fields = ['id', 'name', 'slug', 'is_private', 'description']


class AggregateFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    family = django_filters.NumberFilter(
        field_name='prefix',
        lookup_expr='family'
    )
    prefix = django_filters.CharFilter(
        method='filter_prefix',
        label='Подсеть',
    )
    rir_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RIR.objects.all(),
        label='RIR (ID)',
    )
    rir = django_filters.ModelMultipleChoiceFilter(
        field_name='rir__slug',
        queryset=RIR.objects.all(),
        to_field_name='slug',
        label='RIR (slug)',
    )

    class Meta:
        model = Aggregate
        fields = ['id', 'date_added', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(description__icontains=value)
        qs_filter |= Q(prefix__contains=value.strip())
        try:
            prefix = str(netaddr.IPNetwork(value.strip()).cidr)
            qs_filter |= Q(prefix__net_contains_or_equals=prefix)
            qs_filter |= Q(prefix__contains=value.strip())
        except (AddrFormatError, ValueError):
            pass
        return queryset.filter(qs_filter)

    def filter_prefix(self, queryset, name, value):
        if not value.strip():
            return queryset
        try:
            query = str(netaddr.IPNetwork(value).cidr)
            return queryset.filter(prefix=query)
        except (AddrFormatError, ValueError):
            return queryset.none()


class ASNFilterSet(OrganizationalModelFilterSet, TenancyFilterSet):
    rir_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RIR.objects.all(),
        label='RIR (ID)',
    )
    rir = django_filters.ModelMultipleChoiceFilter(
        field_name='rir__slug',
        queryset=RIR.objects.all(),
        to_field_name='slug',
        label='RIR (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='sites',
        queryset=Site.objects.all(),
        label='Адрес (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='sites__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Адрес (slug)',
    )

    class Meta:
        model = ASN
        fields = ['id', 'asn', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(description__icontains=value)
        try:
            qs_filter |= Q(asn=int(value))
        except ValueError:
            pass
        return queryset.filter(qs_filter)


class RoleFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = Role
        fields = ['id', 'name', 'slug', 'description']


class PrefixFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    family = django_filters.NumberFilter(
        field_name='prefix',
        lookup_expr='family'
    )
    prefix = MultiValueCharFilter(
        method='filter_prefix',
        label='Подсеть',
    )
    within = django_filters.CharFilter(
        method='search_within',
        label='Within prefix',
    )
    within_include = django_filters.CharFilter(
        method='search_within_include',
        label='Внутри и включая подсеть',
    )
    contains = django_filters.CharFilter(
        method='search_contains',
        label='Подсети, содержащие эту подсеть или IP-адрес',
    )
    depth = MultiValueNumberFilter(
        field_name='_depth'
    )
    children = MultiValueNumberFilter(
        field_name='_children'
    )
    mask_length = MultiValueNumberFilter(
        field_name='prefix',
        lookup_expr='net_mask_length'
    )
    mask_length__gte = django_filters.NumberFilter(
        field_name='prefix',
        lookup_expr='net_mask_length__gte'
    )
    mask_length__lte = django_filters.NumberFilter(
        field_name='prefix',
        lookup_expr='net_mask_length__lte'
    )
    vrf_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VRF.objects.all(),
        label='VRF',
    )
    vrf = django_filters.ModelMultipleChoiceFilter(
        field_name='vrf__rd',
        queryset=VRF.objects.all(),
        to_field_name='rd',
        label='VRF (RD)',
    )
    present_in_vrf_id = django_filters.ModelChoiceFilter(
        queryset=VRF.objects.all(),
        method='filter_present_in_vrf',
        label='VRF'
    )
    present_in_vrf = django_filters.ModelChoiceFilter(
        queryset=VRF.objects.all(),
        method='filter_present_in_vrf',
        to_field_name='rd',
        label='VRF (RD)',
    )
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
    vlan_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VLAN.objects.all(),
        label='VLAN (ID)',
    )
    vlan_vid = django_filters.NumberFilter(
        field_name='vlan__vid',
        label='VLAN number (1-4094)',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Role.objects.all(),
        label='Роль (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=Role.objects.all(),
        to_field_name='slug',
        label='Роль (slug)\"',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=PrefixStatusChoices,
        null_value=None
    )

    class Meta:
        model = Prefix
        fields = ['id', 'is_pool', 'mark_utilized', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(description__icontains=value)
        qs_filter |= Q(prefix__contains=value.strip())
        try:
            prefix = str(netaddr.IPNetwork(value.strip()).cidr)
            qs_filter |= Q(prefix__net_contains_or_equals=prefix)
            qs_filter |= Q(prefix__contains=value.strip())
        except (AddrFormatError, ValueError):
            pass
        return queryset.filter(qs_filter)

    def filter_prefix(self, queryset, name, value):
        query_values = []
        for v in value:
            try:
                query_values.append(netaddr.IPNetwork(v))
            except (AddrFormatError, ValueError):
                pass
        return queryset.filter(prefix__in=query_values)

    def search_within(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            query = str(netaddr.IPNetwork(value).cidr)
            return queryset.filter(prefix__net_contained=query)
        except (AddrFormatError, ValueError):
            return queryset.none()

    def search_within_include(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            query = str(netaddr.IPNetwork(value).cidr)
            return queryset.filter(prefix__net_contained_or_equal=query)
        except (AddrFormatError, ValueError):
            return queryset.none()

    def search_contains(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            # Searching by prefix
            if '/' in value:
                return queryset.filter(prefix__net_contains_or_equals=str(netaddr.IPNetwork(value).cidr))
            # Searching by IP address
            else:
                return queryset.filter(prefix__net_contains=str(netaddr.IPAddress(value)))
        except (AddrFormatError, ValueError):
            return queryset.none()

    def filter_present_in_vrf(self, queryset, name, vrf):
        if vrf is None:
            return queryset.none
        return queryset.filter(
            Q(vrf=vrf) |
            Q(vrf__export_targets__in=vrf.import_targets.all())
        )


class IPRangeFilterSet(TenancyFilterSet, NetBoxModelFilterSet):
    family = django_filters.NumberFilter(
        field_name='start_address',
        lookup_expr='family'
    )
    contains = django_filters.CharFilter(
        method='search_contains',
        label='Ranges which contain this prefix or IP',
    )
    vrf_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VRF.objects.all(),
        label='VRF',
    )
    vrf = django_filters.ModelMultipleChoiceFilter(
        field_name='vrf__rd',
        queryset=VRF.objects.all(),
        to_field_name='rd',
        label='VRF (RD)',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Role.objects.all(),
        label='Роль (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=Role.objects.all(),
        to_field_name='slug',
        label='Роль (slug)\"',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=IPRangeStatusChoices,
        null_value=None
    )

    class Meta:
        model = IPRange
        fields = ['id', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(description__icontains=value)
        try:
            ipaddress = str(netaddr.IPNetwork(value.strip()).cidr)
            qs_filter |= Q(start_address=ipaddress)
            qs_filter |= Q(end_address=ipaddress)
        except (AddrFormatError, ValueError):
            pass
        return queryset.filter(qs_filter)

    def search_contains(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            # Strip mask
            ipaddress = netaddr.IPNetwork(value)
            return queryset.filter(start_address__lte=ipaddress, end_address__gte=ipaddress)
        except (AddrFormatError, ValueError):
            return queryset.none()


class IPAddressFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    family = django_filters.NumberFilter(
        field_name='address',
        lookup_expr='family'
    )
    parent = MultiValueCharFilter(
        method='search_by_parent',
        label='Родительская подсеть',
    )
    address = MultiValueCharFilter(
        method='filter_address',
        label='IP Адрес',
    )
    mask_length = django_filters.NumberFilter(
        method='filter_mask_length',
        label='Длина маски',
    )
    vrf_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VRF.objects.all(),
        label='VRF',
    )
    vrf = django_filters.ModelMultipleChoiceFilter(
        field_name='vrf__rd',
        queryset=VRF.objects.all(),
        to_field_name='rd',
        label='VRF (RD)',
    )
    present_in_vrf_id = django_filters.ModelChoiceFilter(
        queryset=VRF.objects.all(),
        method='filter_present_in_vrf',
        label='VRF'
    )
    present_in_vrf = django_filters.ModelChoiceFilter(
        queryset=VRF.objects.all(),
        method='filter_present_in_vrf',
        to_field_name='rd',
        label='VRF (RD)',
    )
    device = MultiValueCharFilter(
        method='filter_device',
        field_name='name',
        label='Устройство (Название)',
    )
    device_id = MultiValueNumberFilter(
        method='filter_device',
        field_name='pk',
        label='Устройство (ID)',
    )
    virtual_machine = MultiValueCharFilter(
        method='filter_virtual_machine',
        field_name='name',
        label='Виртуальная машина (название)',
    )
    virtual_machine_id = MultiValueNumberFilter(
        method='filter_virtual_machine',
        field_name='pk',
        label='Виртуальная машина (ID)',
    )
    interface = django_filters.ModelMultipleChoiceFilter(
        field_name='interface__name',
        queryset=Interface.objects.all(),
        to_field_name='name',
        label='Интерфейс (название)',
    )
    interface_id = django_filters.ModelMultipleChoiceFilter(
        field_name='interface',
        queryset=Interface.objects.all(),
        label='Интерфейс (ID)',
    )
    vminterface = django_filters.ModelMultipleChoiceFilter(
        field_name='vminterface__name',
        queryset=VMInterface.objects.all(),
        to_field_name='name',
        label='Интерфейс ВМ (имя)',
    )
    vminterface_id = django_filters.ModelMultipleChoiceFilter(
        field_name='vminterface',
        queryset=VMInterface.objects.all(),
        label='Интерфейс ВМ (ID)',
    )
    fhrpgroup_id = django_filters.ModelMultipleChoiceFilter(
        field_name='fhrpgroup',
        queryset=FHRPGroup.objects.all(),
        label='FHRP group (ID)',
    )
    assigned_to_interface = django_filters.BooleanFilter(
        method='_assigned_to_interface',
        label='Привязан к интерфейсу',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=IPAddressStatusChoices,
        null_value=None
    )
    role = django_filters.MultipleChoiceFilter(
        choices=IPAddressRoleChoices
    )

    class Meta:
        model = IPAddress
        fields = ['id', 'dns_name', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(dns_name__icontains=value) |
            Q(description__icontains=value) |
            Q(address__istartswith=value)
        )
        return queryset.filter(qs_filter)

    def search_by_parent(self, queryset, name, value):
        if not value:
            return queryset
        q = Q()
        for prefix in value:
            try:
                query = str(netaddr.IPNetwork(prefix.strip()).cidr)
                q |= Q(address__net_host_contained=query)
            except (AddrFormatError, ValueError):
                return queryset.none()
        return queryset.filter(q)

    def filter_address(self, queryset, name, value):
        try:
            return queryset.filter(address__net_in=value)
        except ValidationError:
            return queryset.none()

    def filter_mask_length(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(address__net_mask_length=value)

    def filter_present_in_vrf(self, queryset, name, vrf):
        if vrf is None:
            return queryset.none
        return queryset.filter(
            Q(vrf=vrf) |
            Q(vrf__export_targets__in=vrf.import_targets.all())
        )

    def filter_device(self, queryset, name, value):
        devices = Device.objects.filter(**{'{}__in'.format(name): value})
        if not devices.exists():
            return queryset.none()
        interface_ids = []
        for device in devices:
            interface_ids.extend(device.vc_interfaces().values_list('id', flat=True))
        return queryset.filter(
            interface__in=interface_ids
        )

    def filter_virtual_machine(self, queryset, name, value):
        virtual_machines = VirtualMachine.objects.filter(**{'{}__in'.format(name): value})
        if not virtual_machines.exists():
            return queryset.none()
        interface_ids = []
        for vm in virtual_machines:
            interface_ids.extend(vm.interfaces.values_list('id', flat=True))
        return queryset.filter(
            vminterface__in=interface_ids
        )

    def _assigned_to_interface(self, queryset, name, value):
        content_types = ContentType.objects.get_for_models(Interface, VMInterface).values()
        if value:
            return queryset.filter(
                assigned_object_type__in=content_types,
                assigned_object_id__isnull=False
            )
        else:
            return queryset.exclude(
                assigned_object_type__in=content_types,
                assigned_object_id__isnull=False
            )


class FHRPGroupFilterSet(NetBoxModelFilterSet):
    protocol = django_filters.MultipleChoiceFilter(
        choices=FHRPGroupProtocolChoices
    )
    auth_type = django_filters.MultipleChoiceFilter(
        choices=FHRPGroupAuthTypeChoices
    )
    related_ip = django_filters.ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        method='filter_related_ip'
    )

    class Meta:
        model = FHRPGroup
        fields = ['id', 'group_id', 'auth_key']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(description__icontains=value)
        )

    def filter_related_ip(self, queryset, name, value):
        """
        Filter by VRF & prefix of assigned IP addresses.
        """
        ip_filter = Q()
        for ipaddress in value:
            if ipaddress.vrf:
                q = Q(
                    ip_addresses__address__net_contained_or_equal=ipaddress.address,
                    ip_addresses__vrf=ipaddress.vrf
                )
            else:
                q = Q(
                    ip_addresses__address__net_contained_or_equal=ipaddress.address,
                    ip_addresses__vrf__isnull=True
                )
            ip_filter |= q

        return queryset.filter(ip_filter)


class FHRPGroupAssignmentFilterSet(ChangeLoggedModelFilterSet):
    interface_type = ContentTypeFilter()
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=FHRPGroup.objects.all(),
        label='Группа (ID)',
    )
    device = MultiValueCharFilter(
        method='filter_device',
        field_name='name',
        label='Устройство (Название)',
    )
    device_id = MultiValueNumberFilter(
        method='filter_device',
        field_name='pk',
        label='Устройство (ID)',
    )
    virtual_machine = MultiValueCharFilter(
        method='filter_virtual_machine',
        field_name='name',
        label='Виртуальная машина (название)',
    )
    virtual_machine_id = MultiValueNumberFilter(
        method='filter_virtual_machine',
        field_name='pk',
        label='Виртуальная машина (ID)',
    )

    class Meta:
        model = FHRPGroupAssignment
        fields = ['id', 'group_id', 'interface_type', 'interface_id', 'priority']

    def filter_device(self, queryset, name, value):
        devices = Device.objects.filter(**{f'{name}__in': value})
        if not devices.exists():
            return queryset.none()
        interface_ids = []
        for device in devices:
            interface_ids.extend(device.vc_interfaces().values_list('id', flat=True))
        return queryset.filter(
            Q(interface_type=ContentType.objects.get_for_model(Interface), interface_id__in=interface_ids)
        )

    def filter_virtual_machine(self, queryset, name, value):
        virtual_machines = VirtualMachine.objects.filter(**{f'{name}__in': value})
        if not virtual_machines.exists():
            return queryset.none()
        interface_ids = []
        for vm in virtual_machines:
            interface_ids.extend(vm.interfaces.values_list('id', flat=True))
        return queryset.filter(
            Q(interface_type=ContentType.objects.get_for_model(VMInterface), interface_id__in=interface_ids)
        )


class VLANGroupFilterSet(OrganizationalModelFilterSet):
    scope_type = ContentTypeFilter()
    region = django_filters.NumberFilter(
        method='filter_scope'
    )
    sitegroup = django_filters.NumberFilter(
        method='filter_scope'
    )
    site = django_filters.NumberFilter(
        method='filter_scope'
    )
    location = django_filters.NumberFilter(
        method='filter_scope'
    )
    rack = django_filters.NumberFilter(
        method='filter_scope'
    )
    clustergroup = django_filters.NumberFilter(
        method='filter_scope'
    )
    cluster = django_filters.NumberFilter(
        method='filter_scope'
    )

    class Meta:
        model = VLANGroup
        fields = ['id', 'name', 'slug', 'min_vid', 'max_vid', 'description', 'scope_id']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)

    def filter_scope(self, queryset, name, value):
        return queryset.filter(
            scope_type=ContentType.objects.get(model=name),
            scope_id=value
        )


class VLANFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
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
        queryset=VLANGroup.objects.all(),
        label='Группа (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='group__slug',
        queryset=VLANGroup.objects.all(),
        to_field_name='slug',
        label='Группа',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Role.objects.all(),
        label='Роль (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=Role.objects.all(),
        to_field_name='slug',
        label='Роль (slug)\"',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=VLANStatusChoices,
        null_value=None
    )
    available_on_device = django_filters.ModelChoiceFilter(
        queryset=Device.objects.all(),
        method='get_for_device'
    )
    available_on_virtualmachine = django_filters.ModelChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        method='get_for_virtualmachine'
    )

    class Meta:
        model = VLAN
        fields = ['id', 'vid', 'name', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        try:
            qs_filter |= Q(vid=int(value.strip()))
        except ValueError:
            pass
        return queryset.filter(qs_filter)

    def get_for_device(self, queryset, name, value):
        return queryset.get_for_device(value)

    def get_for_virtualmachine(self, queryset, name, value):
        return queryset.get_for_virtualmachine(value)


class ServiceTemplateFilterSet(NetBoxModelFilterSet):
    port = NumericArrayFilter(
        field_name='ports',
        lookup_expr='contains'
    )

    class Meta:
        model = ServiceTemplate
        fields = ['id', 'name', 'protocol']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)


class ServiceFilterSet(NetBoxModelFilterSet):
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label='Устройство (ID)',
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name='device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Устройство (Название)',
    )
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        label='Виртуальная машина (ID)',
    )
    virtual_machine = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine__name',
        queryset=VirtualMachine.objects.all(),
        to_field_name='name',
        label='Виртуальная машина (название)',
    )
    port = NumericArrayFilter(
        field_name='ports',
        lookup_expr='contains'
    )

    class Meta:
        model = Service
        fields = ['id', 'name', 'protocol', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)
