import django_tables2 as tables

from dcim.models import Module, ModuleType
from netbox.tables import NetBoxTable, columns

__all__ = (
    'ModuleTable',
    'ModuleTypeTable',
)


class ModuleTypeTable(NetBoxTable):
    model = tables.Column(
        linkify=True,
        verbose_name='Тип модуля'
    )
    instance_count = columns.LinkedCountColumn(
        viewname='dcim:module_list',
        url_params={'module_type_id': 'pk'},
        verbose_name='Экземпляры'
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='dcim:moduletype_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ModuleType
        fields = (
            'pk', 'id', 'model', 'manufacturer', 'part_number', 'comments', 'tags',
        )
        default_columns = (
            'pk', 'model', 'manufacturer', 'part_number',
        )


class ModuleTable(NetBoxTable):
    device = tables.Column(
        verbose_name = "устройство",
        linkify=True
    )
    module_bay = tables.Column(
        verbose_name = "Модульный отсек",
        linkify=True
    )
    module_type = tables.Column(
        verbose_name = "Тип модуля",
        linkify=True
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='dcim:module_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Module
        fields = (
            'pk', 'id', 'device', 'module_bay', 'module_type', 'serial', 'asset_tag', 'comments', 'tags',
        )
        default_columns = (
            'pk', 'id', 'device', 'module_bay', 'module_type', 'serial', 'asset_tag',
        )
