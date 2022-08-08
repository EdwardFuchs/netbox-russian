from circuits.models import Circuit, CircuitTermination, Provider
from dcim.models import *
from extras.models import Tag
from netbox.forms import NetBoxModelForm
from tenancy.forms import TenancyForm
from utilities.forms import DynamicModelChoiceField, DynamicModelMultipleChoiceField, StaticSelect

__all__ = (
    'ConnectCableToCircuitTerminationForm',
    'ConnectCableToConsolePortForm',
    'ConnectCableToConsoleServerPortForm',
    'ConnectCableToFrontPortForm',
    'ConnectCableToInterfaceForm',
    'ConnectCableToPowerFeedForm',
    'ConnectCableToPowerPortForm',
    'ConnectCableToPowerOutletForm',
    'ConnectCableToRearPortForm',
)


class ConnectCableToDeviceForm(TenancyForm, NetBoxModelForm):
    """
    Base form for connecting a Cable to a Device component
    """
    termination_b_region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        label='Регион',
        required=False
    )
    termination_b_sitegroup = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        label='Группа адресов',
        required=False
    )
    termination_b_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label='Адрес',
        required=False,
        query_params={
            'region_id': '$termination_b_region',
            'group_id': '$termination_b_sitegroup',
        }
    )
    termination_b_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        label='Метоположение',
        required=False,
        null_option='None',
        query_params={
            'site_id': '$termination_b_site'
        }
    )
    termination_b_rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        label='Стойка',
        required=False,
        null_option='None',
        query_params={
            'site_id': '$termination_b_site',
            'location_id': '$termination_b_location',
        }
    )
    termination_b_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label='Устройство',
        required=False,
        query_params={
            'site_id': '$termination_b_site',
            'location_id': '$termination_b_location',
            'rack_id': '$termination_b_rack',
        }
    )

    class Meta:
        model = Cable
        fields = [
            'termination_b_region', 'termination_b_sitegroup', 'termination_b_site', 'termination_b_rack',
            'termination_b_device', 'termination_b_id', 'type', 'status', 'tenant_group', 'tenant', 'label', 'color',
            'length', 'length_unit', 'tags',
        ]
        widgets = {
            'status': StaticSelect,
            'type': StaticSelect,
            'length_unit': StaticSelect,
        }

    def clean_termination_b_id(self):
        # Return the PK rather than the object
        return getattr(self.cleaned_data['termination_b_id'], 'pk', None)


class ConnectCableToConsolePortForm(ConnectCableToDeviceForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=ConsolePort.objects.all(),
        label='Имя',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToConsoleServerPortForm(ConnectCableToDeviceForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=ConsoleServerPort.objects.all(),
        label='Имя',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToPowerPortForm(ConnectCableToDeviceForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=PowerPort.objects.all(),
        label='Имя',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToPowerOutletForm(ConnectCableToDeviceForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=PowerOutlet.objects.all(),
        label='Имя',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToInterfaceForm(ConnectCableToDeviceForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        label='Имя',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device',
            'kind': 'physical',
        }
    )


class ConnectCableToFrontPortForm(ConnectCableToDeviceForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=FrontPort.objects.all(),
        label='Имя',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToRearPortForm(ConnectCableToDeviceForm):
    termination_b_id = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        label='Имя',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToCircuitTerminationForm(TenancyForm, NetBoxModelForm):
    termination_b_provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        label='Поставщик услуг',
        required=False
    )
    termination_b_region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        label='Регион',
        required=False
    )
    termination_b_sitegroup = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        label='Группа адресов',
        required=False
    )
    termination_b_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label='Адрес',
        required=False,
        query_params={
            'region_id': '$termination_b_region',
            'group_id': '$termination_b_sitegroup',
        }
    )
    termination_b_circuit = DynamicModelChoiceField(
        queryset=Circuit.objects.all(),
        label='Внешний канал',
        query_params={
            'provider_id': '$termination_b_provider',
            'site_id': '$termination_b_site',
        }
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=CircuitTermination.objects.all(),
        label='Сторона',
        disabled_indicator='_occupied',
        query_params={
            'circuit_id': '$termination_b_circuit'
        }
    )

    class Meta(ConnectCableToDeviceForm.Meta):
        fields = [
            'termination_b_provider', 'termination_b_region', 'termination_b_sitegroup', 'termination_b_site',
            'termination_b_circuit', 'termination_b_id', 'type', 'status', 'tenant_group', 'tenant', 'label', 'color',
            'length', 'length_unit', 'tags',
        ]

    def clean_termination_b_id(self):
        # Return the PK rather than the object
        return getattr(self.cleaned_data['termination_b_id'], 'pk', None)


class ConnectCableToPowerFeedForm(TenancyForm, NetBoxModelForm):
    termination_b_region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        label='Регион',
        required=False
    )
    termination_b_sitegroup = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        label='Группа адресов',
        required=False
    )
    termination_b_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label='Адрес',
        required=False,
        query_params={
            'region_id': '$termination_b_region',
            'group_id': '$termination_b_sitegroup',
        }
    )
    termination_b_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        label='Метоположение',
        required=False,
        query_params={
            'site_id': '$termination_b_site'
        }
    )
    termination_b_powerpanel = DynamicModelChoiceField(
        queryset=PowerPanel.objects.all(),
        label='Силовая панель',
        required=False,
        query_params={
            'site_id': '$termination_b_site',
            'location_id': '$termination_b_location',
        }
    )
    termination_b_id = DynamicModelChoiceField(
        queryset=PowerFeed.objects.all(),
        label='Имя',
        disabled_indicator='_occupied',
        query_params={
            'power_panel_id': '$termination_b_powerpanel'
        }
    )

    class Meta(ConnectCableToDeviceForm.Meta):
        fields = [
            'termination_b_region', 'termination_b_sitegroup', 'termination_b_site', 'termination_b_location',
            'termination_b_powerpanel', 'termination_b_id', 'type', 'status', 'tenant_group', 'tenant', 'label',
            'color', 'length', 'length_unit', 'tags',
        ]

    def clean_termination_b_id(self):
        # Return the PK rather than the object
        return getattr(self.cleaned_data['termination_b_id'], 'pk', None)
