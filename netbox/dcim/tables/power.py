import django_tables2 as tables

from dcim.models import PowerFeed, PowerPanel
from netbox.tables import NetBoxTable, columns
from .devices import CableTerminationTable

__all__ = (
    'PowerFeedTable',
    'PowerPanelTable',
)


#
# Power panels
#

class PowerPanelTable(NetBoxTable):
    name = tables.Column(
        verbose_name = "название",
        linkify=True
    )
    site = tables.Column(
        verbose_name = "адрес",
        linkify=True
    )
    powerfeed_count = columns.LinkedCountColumn(
        viewname='dcim:powerfeed_list',
        url_params={'power_panel_id': 'pk'},
        verbose_name='Питание'
    )
    contacts = columns.ManyToManyColumn(
        verbose_name = "Контакты",
        linkify_item=True
    )
    tags = columns.TagColumn(
        url_name='dcim:powerpanel_list'
    )

    class Meta(NetBoxTable.Meta):
        model = PowerPanel
        fields = ('pk', 'id', 'name', 'site', 'location', 'powerfeed_count', 'contacts', 'tags', 'created', 'last_updated',)
        default_columns = ('pk', 'name', 'site', 'location', 'powerfeed_count')


#
# Power feeds
#

# We're not using PathEndpointTable for PowerFeed because power connections
# cannot traverse pass-through ports.
class PowerFeedTable(CableTerminationTable):
    name = tables.Column(
        verbose_name = "название",
        linkify=True
    )
    power_panel = tables.Column(
        verbose_name = "Силовая панель",
        linkify=True
    )
    rack = tables.Column(
        verbose_name = "стойка",
        linkify=True
    )
    status = columns.ChoiceFieldColumn()
    type = columns.ChoiceFieldColumn()
    max_utilization = tables.TemplateColumn(
        template_code="{{ value }}%"
    )
    available_power = tables.Column(
        verbose_name='Доступное электропитание (VA)'
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='dcim:powerfeed_list'
    )

    class Meta(NetBoxTable.Meta):
        model = PowerFeed
        fields = (
            'pk', 'id', 'name', 'power_panel', 'rack', 'status', 'type', 'supply', 'voltage', 'amperage', 'phase',
            'max_utilization', 'mark_connected', 'cable', 'cable_color', 'link_peer', 'connection', 'available_power',
            'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'power_panel', 'rack', 'status', 'type', 'supply', 'voltage', 'amperage', 'phase', 'cable',
            'link_peer',
        )
