import django_tables2 as tables

from dcim.models import (
    ConsolePortTemplate, ConsoleServerPortTemplate, DeviceBayTemplate, DeviceType, FrontPortTemplate, InterfaceTemplate,
    InventoryItemTemplate, Manufacturer, ModuleBayTemplate, PowerOutletTemplate, PowerPortTemplate, RearPortTemplate,
)
from netbox.tables import NetBoxTable, columns
from .template_code import MODULAR_COMPONENT_TEMPLATE_BUTTONS

__all__ = (
    'ConsolePortTemplateTable',
    'ConsoleServerPortTemplateTable',
    'DeviceBayTemplateTable',
    'DeviceTypeTable',
    'FrontPortTemplateTable',
    'InterfaceTemplateTable',
    'InventoryItemTemplateTable',
    'ManufacturerTable',
    'ModuleBayTemplateTable',
    'PowerOutletTemplateTable',
    'PowerPortTemplateTable',
    'RearPortTemplateTable',
)


#
# Manufacturers
#

class ManufacturerTable(NetBoxTable):
    name = tables.Column(
        verbose_name = "название",
        linkify=True
    )
    devicetype_count = columns.LinkedCountColumn(
        viewname='dcim:devicetype_list',
        url_params={'manufacturer_id': 'pk'},
        verbose_name='Типы устройств'
    )
    inventoryitem_count = tables.Column(
        verbose_name='Встроенные устройства'
    )
    platform_count = tables.Column(
        verbose_name='Платформы'
    )
    slug = tables.Column(
        verbose_name = "короткий URL",)
    contacts = columns.ManyToManyColumn(
        verbose_name = "Контакты",
        linkify_item=True
    )
    tags = columns.TagColumn(
        url_name='dcim:manufacturer_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Manufacturer
        fields = (
            'pk', 'id', 'name', 'devicetype_count', 'inventoryitem_count', 'platform_count', 'description', 'slug',
            'contacts', 'actions', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'devicetype_count', 'inventoryitem_count', 'platform_count', 'description', 'slug',
        )


#
# Device types
#

class DeviceTypeTable(NetBoxTable):
    model = tables.Column(
        linkify=True,
        verbose_name='Тип устройства'
    )
    manufacturer = tables.Column(
        verbose_name = "производитель",
        linkify=True
    )
    is_full_depth = columns.BooleanColumn(
        verbose_name='На всю глубину'
    )
    instance_count = columns.LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'device_type_id': 'pk'},
        verbose_name='Экземпляры'
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='dcim:devicetype_list'
    )

    class Meta(NetBoxTable.Meta):
        model = DeviceType
        fields = (
            'pk', 'id', 'model', 'manufacturer', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role',
            'airflow', 'comments', 'instance_count', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'model', 'manufacturer', 'part_number', 'u_height', 'is_full_depth', 'instance_count',
        )


#
# Device type components
#

class ComponentTemplateTable(NetBoxTable):
    id = tables.Column(
        verbose_name='ID'
    )
    name = tables.Column(
        verbose_name = "название",
        order_by=('_name',)
    )

    class Meta(NetBoxTable.Meta):
        exclude = ('id', )


class ConsolePortTemplateTable(ComponentTemplateTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = ConsolePortTemplate
        fields = ('pk', 'name', 'label', 'type', 'description', 'actions')
        empty_text = "None"


class ConsoleServerPortTemplateTable(ComponentTemplateTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = ConsoleServerPortTemplate
        fields = ('pk', 'name', 'label', 'type', 'description', 'actions')
        empty_text = "None"


class PowerPortTemplateTable(ComponentTemplateTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = PowerPortTemplate
        fields = ('pk', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description', 'actions')
        empty_text = "None"


class PowerOutletTemplateTable(ComponentTemplateTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = PowerOutletTemplate
        fields = ('pk', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description', 'actions')
        empty_text = "None"


class InterfaceTemplateTable(ComponentTemplateTable):
    mgmt_only = columns.BooleanColumn(
        verbose_name='Только управление'
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = InterfaceTemplate
        fields = ('pk', 'name', 'label', 'mgmt_only', 'type', 'description', 'actions')
        empty_text = "None"


class FrontPortTemplateTable(ComponentTemplateTable):
    rear_port_position = tables.Column(
        verbose_name='Позиция'
    )
    color = columns.ColorColumn()
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = FrontPortTemplate
        fields = ('pk', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position', 'description', 'actions')
        empty_text = "None"


class RearPortTemplateTable(ComponentTemplateTable):
    color = columns.ColorColumn()
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = RearPortTemplate
        fields = ('pk', 'name', 'label', 'type', 'color', 'positions', 'description', 'actions')
        empty_text = "None"


class ModuleBayTemplateTable(ComponentTemplateTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete')
    )

    class Meta(ComponentTemplateTable.Meta):
        model = ModuleBayTemplate
        fields = ('pk', 'name', 'label', 'position', 'description', 'actions')
        empty_text = "None"


class DeviceBayTemplateTable(ComponentTemplateTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete')
    )

    class Meta(ComponentTemplateTable.Meta):
        model = DeviceBayTemplate
        fields = ('pk', 'name', 'label', 'description', 'actions')
        empty_text = "None"


class InventoryItemTemplateTable(ComponentTemplateTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete')
    )
    role = tables.Column(
        verbose_name = "Роль",
        linkify=True
    )
    manufacturer = tables.Column(
        verbose_name = "производитель",
        linkify=True
    )
    component = tables.Column(
        orderable=False
    )

    class Meta(ComponentTemplateTable.Meta):
        model = InventoryItemTemplate
        fields = (
            'pk', 'name', 'label', 'parent', 'role', 'manufacturer', 'part_id', 'component', 'description', 'actions',
        )
        empty_text = "None"
