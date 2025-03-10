import django_tables2 as tables

from netbox.tables import NetBoxTable, columns
from tenancy.models import *

__all__ = (
    'TenantGroupTable',
    'TenantTable',
)


class TenantGroupTable(NetBoxTable):
    name = columns.MPTTColumn(
        verbose_name = "название",
        linkify=True
    )
    tenant_count = columns.LinkedCountColumn(
        viewname='tenancy:tenant_list',
        url_params={'group_id': 'pk'},
        verbose_name='Учреждения'
    )
    tags = columns.TagColumn(
        url_name='tenancy:tenantgroup_list'
    )

    class Meta(NetBoxTable.Meta):
        model = TenantGroup
        fields = (
            'pk', 'id', 'name', 'tenant_count', 'description', 'slug', 'tags', 'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'tenant_count', 'description')


class TenantTable(NetBoxTable):
    name = tables.Column(
        verbose_name = "название",
        linkify=True
    )
    group = tables.Column(
        verbose_name = "Группа",
        linkify=True
    )
    comments = columns.MarkdownColumn()
    contacts = columns.ManyToManyColumn(
        verbose_name = "Контакты",
        linkify_item=True
    )
    tags = columns.TagColumn(
        url_name='tenancy:tenant_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Tenant
        fields = (
            'pk', 'id', 'name', 'slug', 'group', 'description', 'comments', 'contacts', 'tags', 'created',
            'last_updated',
        )
        default_columns = ('pk', 'name', 'group', 'description')
