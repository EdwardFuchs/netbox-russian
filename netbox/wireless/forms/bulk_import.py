from dcim.choices import LinkStatusChoices
from dcim.models import Interface
from ipam.models import VLAN
from netbox.forms import NetBoxModelCSVForm
from utilities.forms import CSVChoiceField, CSVModelChoiceField, SlugField
from wireless.choices import *
from wireless.models import *

__all__ = (
    'WirelessLANCSVForm',
    'WirelessLANGroupCSVForm',
    'WirelessLinkCSVForm',
)


class WirelessLANGroupCSVForm(NetBoxModelCSVForm):
    parent = CSVModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent group'
    )
    slug = SlugField()

    class Meta:
        model = WirelessLANGroup
        fields = ('name', 'slug', 'parent', 'description')


class WirelessLANCSVForm(NetBoxModelCSVForm):
    group = CSVModelChoiceField(
        label='Группа',
        queryset=WirelessLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned group'
    )
    vlan = CSVModelChoiceField(
        label='VLAN',
        queryset=VLAN.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Bridged VLAN'
    )
    auth_type = CSVChoiceField(
        label='Тип',
        choices=WirelessAuthTypeChoices,
        required=False,
        help_text='Authentication type'
    )
    auth_cipher = CSVChoiceField(
        label='Шифр',
        choices=WirelessAuthCipherChoices,
        required=False,
        help_text='Authentication cipher'
    )

    class Meta:
        model = WirelessLAN
        fields = ('ssid', 'group', 'description', 'vlan', 'auth_type', 'auth_cipher', 'auth_psk')


class WirelessLinkCSVForm(NetBoxModelCSVForm):
    status = CSVChoiceField(
        label='Статус',
        choices=LinkStatusChoices,
        help_text='Connection status'
    )
    interface_a = CSVModelChoiceField(
        label='Интерфейс А',
        queryset=Interface.objects.all()
    )
    interface_b = CSVModelChoiceField(
        label='Интерфейс Б',
        queryset=Interface.objects.all()
    )
    auth_type = CSVChoiceField(
        label='Тип',
        choices=WirelessAuthTypeChoices,
        required=False,
        help_text='Authentication type'
    )
    auth_cipher = CSVChoiceField(
        label='Шифр',
        choices=WirelessAuthCipherChoices,
        required=False,
        help_text='Authentication cipher'
    )

    class Meta:
        model = WirelessLink
        fields = ('interface_a', 'interface_b', 'ssid', 'description', 'auth_type', 'auth_cipher', 'auth_psk')
