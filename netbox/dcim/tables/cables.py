import django_tables2 as tables
from django_tables2.utils import Accessor

from dcim.models import Cable
from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenancyColumnsMixin
from .template_code import CABLE_LENGTH, CABLE_TERMINATION_PARENT

__all__ = (
    'CableTable',
)


#
# Cables
#

class CableTable(TenancyColumnsMixin, NetBoxTable):
    termination_a_parent = tables.TemplateColumn(
        template_code=CABLE_TERMINATION_PARENT,
        accessor=Accessor('termination_a'),
        orderable=False,
        verbose_name='Точка 1'
    )
    rack_a = tables.Column(
        accessor=Accessor('termination_a__device__rack'),
        orderable=False,
        linkify=True,
        verbose_name='Rack A'
    )
    termination_a = tables.Column(
        accessor=Accessor('termination_a'),
        orderable=False,
        linkify=True,
        verbose_name='Подключение 1'
    )
    termination_b_parent = tables.TemplateColumn(
        template_code=CABLE_TERMINATION_PARENT,
        accessor=Accessor('termination_b'),
        orderable=False,
        verbose_name='Точка 2'
    )
    rack_b = tables.Column(
        accessor=Accessor('termination_b__device__rack'),
        orderable=False,
        linkify=True,
        verbose_name='Rack B'
    )
    termination_b = tables.Column(
        accessor=Accessor('termination_b'),
        orderable=False,
        linkify=True,
        verbose_name='Подключение 2'
    )
    status = columns.ChoiceFieldColumn()
    length = columns.TemplateColumn(
        template_code=CABLE_LENGTH,
        order_by=('_abs_length', 'length_unit')
    )
    color = columns.ColorColumn()
    tags = columns.TagColumn(
        url_name='dcim:cable_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Cable
        fields = (
            'pk', 'id', 'label', 'termination_a_parent', 'rack_a', 'termination_a', 'termination_b_parent', 'rack_b', 'termination_b',
            'status', 'type', 'tenant', 'tenant_group', 'color', 'length', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'id', 'label', 'termination_a_parent', 'termination_a', 'termination_b_parent', 'termination_b',
            'status', 'type',
        )
