import django_tables2 as tables
from django_tables2.utils import Accessor

from netbox.tables import BaseTable, columns
from dcim.models import ConsolePort, Interface, PowerPort
from .cables import *
from .devices import *
from .devicetypes import *
from .modules import *
from .power import *
from .racks import *
from .sites import *


#
# Device connections
#

class ConsoleConnectionTable(BaseTable):
    console_server = tables.Column(
        accessor=Accessor('_path__destination__device'),
        orderable=False,
        linkify=True,
        verbose_name='Консольный сервер'
    )
    console_server_port = tables.Column(
        accessor=Accessor('_path__destination'),
        orderable=False,
        linkify=True,
        verbose_name='Порт'
    )
    device = tables.Column(
        verbose_name = "устройство",
        linkify=True
    )
    name = tables.Column(
        linkify=True,
        verbose_name='Консольный порт'
    )
    reachable = columns.BooleanColumn(
        accessor=Accessor('_path__is_active'),
        verbose_name='Доступность'
    )

    class Meta(BaseTable.Meta):
        model = ConsolePort
        fields = ('device', 'name', 'console_server', 'console_server_port', 'reachable')


class PowerConnectionTable(BaseTable):
    pdu = tables.Column(
        accessor=Accessor('_path__destination__device'),
        orderable=False,
        linkify=True,
        verbose_name='БРП'
    )
    outlet = tables.Column(
        accessor=Accessor('_path__destination'),
        orderable=False,
        linkify=True,
        verbose_name='Розетка'
    )
    device = tables.Column(
        verbose_name = "устройство",
        linkify=True
    )
    name = tables.Column(
        linkify=True,
        verbose_name='Порт питания'
    )
    reachable = columns.BooleanColumn(
        accessor=Accessor('_path__is_active'),
        verbose_name='Доступность'
    )

    class Meta(BaseTable.Meta):
        model = PowerPort
        fields = ('device', 'name', 'pdu', 'outlet', 'reachable')


class InterfaceConnectionTable(BaseTable):
    device_a = tables.Column(
        accessor=Accessor('device'),
        linkify=True,
        verbose_name='Устройство 1'
    )
    interface_a = tables.Column(
        accessor=Accessor('name'),
        linkify=True,
        verbose_name='Интерфейс 1'
    )
    device_b = tables.Column(
        accessor=Accessor('_path__destination__device'),
        orderable=False,
        linkify=True,
        verbose_name='Устройство 2'
    )
    interface_b = tables.Column(
        accessor=Accessor('_path__destination'),
        orderable=False,
        linkify=True,
        verbose_name='Интерфейс 2'
    )
    reachable = columns.BooleanColumn(
        accessor=Accessor('_path__is_active'),
        verbose_name='Доступность'
    )

    class Meta(BaseTable.Meta):
        model = Interface
        fields = ('device_a', 'interface_a', 'device_b', 'interface_b', 'reachable')
