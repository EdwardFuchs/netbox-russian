import django_tables2 as tables
from django_tables2.utils import Accessor

from dcim.models import Rack, RackReservation, RackRole
from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenancyColumnsMixin

__all__ = (
    'RackTable',
    'RackReservationTable',
    'RackRoleTable',
)


#
# Rack roles
#

class RackRoleTable(NetBoxTable):
    name = tables.Column(linkify=True)
    rack_count = tables.Column(verbose_name='Стойки')
    color = columns.ColorColumn()
    tags = columns.TagColumn(
        url_name='dcim:rackrole_list'
    )

    class Meta(NetBoxTable.Meta):
        model = RackRole
        fields = (
            'pk', 'id', 'name', 'rack_count', 'color', 'description', 'slug', 'tags', 'actions', 'created',
            'last_updated',
        )
        default_columns = ('pk', 'name', 'rack_count', 'color', 'description')


#
# Racks
#

class RackTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        verbose_name = "название",
        order_by=('_name',),
        linkify=True
    )
    location = tables.Column(
        verbose_name = "расположение",
        linkify=True
    )
    site = tables.Column(
        verbose_name = "адрес",
        linkify=True
    )
    status = columns.ChoiceFieldColumn()
    role = columns.ColoredLabelColumn()
    u_height = tables.TemplateColumn(
        template_code="{{ record.u_height }}U",
        verbose_name='Высота'
    )
    comments = columns.MarkdownColumn()
    device_count = columns.LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'rack_id': 'pk'},
        verbose_name='Устройства'
    )
    get_utilization = columns.UtilizationColumn(
        orderable=False,
        verbose_name='место'
    )
    get_power_utilization = columns.UtilizationColumn(
        orderable=False,
        verbose_name='Электропитание'
    )
    contacts = columns.ManyToManyColumn(
        verbose_name = "Контакты",
        linkify_item=True
    )
    tags = columns.TagColumn(
        url_name='dcim:rack_list'
    )
    outer_width = tables.TemplateColumn(
        template_code="{{ record.outer_width }} {{ record.outer_unit }}",
        verbose_name='Внешняя Ширина'
    )
    outer_depth = tables.TemplateColumn(
        template_code="{{ record.outer_depth }} {{ record.outer_unit }}",
        verbose_name='Внешняя Глубина'
    )

    class Meta(NetBoxTable.Meta):
        model = Rack
        fields = (
            'pk', 'id', 'name', 'site', 'location', 'status', 'facility_id', 'tenant', 'tenant_group', 'role', 'serial', 'asset_tag',
            'type', 'width', 'outer_width', 'outer_depth', 'u_height', 'comments', 'device_count', 'get_utilization',
            'get_power_utilization', 'contacts', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'site', 'location', 'status', 'facility_id', 'tenant', 'role', 'u_height', 'device_count',
            'get_utilization',
        )


#
# Rack reservations
#

class RackReservationTable(TenancyColumnsMixin, NetBoxTable):
    reservation = tables.Column(
        verbose_name = "Резервирование",
        accessor='pk',
        linkify=True
    )
    site = tables.Column(
        verbose_name = "адрес",
        accessor=Accessor('rack__site'),
        linkify=True
    )
    rack = tables.Column(
        verbose_name = "стойка",
        linkify=True
    )
    unit_list = tables.Column(
        orderable=False,
        verbose_name='Юниты'
    )
    tags = columns.TagColumn(
        url_name='dcim:rackreservation_list'
    )

    class Meta(NetBoxTable.Meta):
        model = RackReservation
        fields = (
            'pk', 'id', 'reservation', 'site', 'rack', 'unit_list', 'user', 'created', 'tenant', 'tenant_group', 'description', 'tags',
            'actions', 'created', 'last_updated',
        )
        default_columns = ('pk', 'reservation', 'site', 'rack', 'unit_list', 'user', 'description')
