import django_filters
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from dcim.models import DeviceRole, DeviceType, Platform, Region, Site, SiteGroup
from netbox.filtersets import BaseFilterSet, ChangeLoggedModelFilterSet, NetBoxModelFilterSet
from tenancy.models import Tenant, TenantGroup
from utilities.filters import ContentTypeFilter, MultiValueCharFilter, MultiValueNumberFilter
from virtualization.models import Cluster, ClusterGroup, ClusterType
from .choices import *
from .models import *


__all__ = (
    'ConfigContextFilterSet',
    'ContentTypeFilterSet',
    'CustomFieldFilterSet',
    'CustomLinkFilterSet',
    'ExportTemplateFilterSet',
    'ImageAttachmentFilterSet',
    'JournalEntryFilterSet',
    'LocalConfigContextFilterSet',
    'ObjectChangeFilterSet',
    'TagFilterSet',
    'WebhookFilterSet',
)


class WebhookFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Поиск',
    )
    content_type_id = MultiValueNumberFilter(
        field_name='content_types__id'
    )
    content_types = ContentTypeFilter()
    http_method = django_filters.MultipleChoiceFilter(
        choices=WebhookHttpMethodChoices
    )

    class Meta:
        model = Webhook
        fields = [
            'id', 'name', 'type_create', 'type_update', 'type_delete', 'payload_url', 'enabled', 'http_method',
            'http_content_type', 'secret', 'ssl_verification', 'ca_file_path',
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(payload_url__icontains=value)
        )


class CustomFieldFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Поиск',
    )
    type = django_filters.MultipleChoiceFilter(
        choices=CustomFieldTypeChoices
    )
    content_type_id = MultiValueNumberFilter(
        field_name='content_types__id'
    )
    content_types = ContentTypeFilter()

    class Meta:
        model = CustomField
        fields = ['id', 'name', 'required', 'filter_logic', 'weight', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(label__icontains=value) |
            Q(description__icontains=value)
        )


class CustomLinkFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Поиск',
    )

    class Meta:
        model = CustomLink
        fields = [
            'id', 'content_type', 'name', 'enabled', 'link_text', 'link_url', 'weight', 'group_name', 'new_window',
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(link_text__icontains=value) |
            Q(link_url__icontains=value) |
            Q(group_name__icontains=value)
        )


class ExportTemplateFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Поиск',
    )

    class Meta:
        model = ExportTemplate
        fields = ['id', 'content_type', 'name', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


class ImageAttachmentFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Поиск',
    )
    created = django_filters.DateTimeFilter()
    content_type = ContentTypeFilter()

    class Meta:
        model = ImageAttachment
        fields = ['id', 'content_type_id', 'object_id', 'name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(name__icontains=value)


class JournalEntryFilterSet(NetBoxModelFilterSet):
    created = django_filters.DateTimeFromToRangeFilter()
    assigned_object_type = ContentTypeFilter()
    created_by_id = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        label='Пользователь (ID)',
    )
    created_by = django_filters.ModelMultipleChoiceFilter(
        field_name='created_by__username',
        queryset=User.objects.all(),
        to_field_name='username',
        label='Пользователь (имя)',
    )
    kind = django_filters.MultipleChoiceFilter(
        choices=JournalEntryKindChoices
    )

    class Meta:
        model = JournalEntry
        fields = ['id', 'assigned_object_type_id', 'assigned_object_id', 'created', 'kind']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(comments__icontains=value)


class TagFilterSet(ChangeLoggedModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Поиск',
    )
    content_type = MultiValueCharFilter(
        method='_content_type'
    )
    content_type_id = MultiValueNumberFilter(
        method='_content_type_id'
    )

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'color', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(slug__icontains=value) |
            Q(description__icontains=value)
        )

    def _content_type(self, queryset, name, values):
        ct_filter = Q()

        # Compile list of app_label & model pairings
        for value in values:
            try:
                app_label, model = value.lower().split('.')
                ct_filter |= Q(
                    app_label=app_label,
                    model=model
                )
            except ValueError:
                pass

        # Get ContentType instances
        content_types = ContentType.objects.filter(ct_filter)

        return queryset.filter(extras_taggeditem_items__content_type__in=content_types).distinct()

    def _content_type_id(self, queryset, name, values):

        # Get ContentType instances
        content_types = ContentType.objects.filter(pk__in=values)

        return queryset.filter(extras_taggeditem_items__content_type__in=content_types).distinct()


class ConfigContextFilterSet(ChangeLoggedModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Поиск',
    )
    region_id = django_filters.ModelMultipleChoiceFilter(
        field_name='regions',
        queryset=Region.objects.all(),
        label='Регион',
    )
    region = django_filters.ModelMultipleChoiceFilter(
        field_name='regions__slug',
        queryset=Region.objects.all(),
        to_field_name='slug',
        label='Регион (slug)',
    )
    site_group = django_filters.ModelMultipleChoiceFilter(
        field_name='site_groups__slug',
        queryset=SiteGroup.objects.all(),
        to_field_name='slug',
        label='Site group (slug)',
    )
    site_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='site_groups',
        queryset=SiteGroup.objects.all(),
        label='Группа адресов',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='sites',
        queryset=Site.objects.all(),
        label='Адрес',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='sites__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Адрес (slug)',
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device_types',
        queryset=DeviceType.objects.all(),
        label='Device type',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        field_name='roles',
        queryset=DeviceRole.objects.all(),
        label='Роль',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='roles__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label='Роль (slug)\"',
    )
    platform_id = django_filters.ModelMultipleChoiceFilter(
        field_name='platforms',
        queryset=Platform.objects.all(),
        label='Платформа',
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        field_name='platforms__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label='Платформа (slug)',
    )
    cluster_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster_types',
        queryset=ClusterType.objects.all(),
        label='Тип кластера',
    )
    cluster_type = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster_types__slug',
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        label='Тип кластера (slug)',
    )
    cluster_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster_groups',
        queryset=ClusterGroup.objects.all(),
        label='Группа кластера',
    )
    cluster_group = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster_groups__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label='Группа кластеров (slug)',
    )
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        field_name='clusters',
        queryset=Cluster.objects.all(),
        label='Кластер',
    )
    tenant_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='tenant_groups',
        queryset=TenantGroup.objects.all(),
        label='Группа учреждений',
    )
    tenant_group = django_filters.ModelMultipleChoiceFilter(
        field_name='tenant_groups__slug',
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        label='Группа учреждений (slug)',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name='tenants',
        queryset=Tenant.objects.all(),
        label='Учреждение',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        field_name='tenants__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Учреждение (slug)',
    )
    tag_id = django_filters.ModelMultipleChoiceFilter(
        field_name='tags',
        queryset=Tag.objects.all(),
        label='Tag',
    )
    tag = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
        label='Тег (slug)',
    )

    class Meta:
        model = ConfigContext
        fields = ['id', 'name', 'is_active']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(data__icontains=value)
        )


#
# Filter for Local Config Context Data
#

class LocalConfigContextFilterSet(django_filters.FilterSet):
    local_context_data = django_filters.BooleanFilter(
        method='_local_context_data',
        label='Имеет локальные данные контекста конфигурации',
    )

    def _local_context_data(self, queryset, name, value):
        return queryset.exclude(local_context_data__isnull=value)


class ObjectChangeFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Поиск',
    )
    time = django_filters.DateTimeFromToRangeFilter()
    changed_object_type = ContentTypeFilter()
    user_id = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        label='Пользователь (ID)',
    )
    user = django_filters.ModelMultipleChoiceFilter(
        field_name='user__username',
        queryset=User.objects.all(),
        to_field_name='username',
        label='Имя пользователя',
    )

    class Meta:
        model = ObjectChange
        fields = [
            'id', 'user', 'user_name', 'request_id', 'action', 'changed_object_type_id', 'changed_object_id',
            'object_repr',
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(user_name__icontains=value) |
            Q(object_repr__icontains=value)
        )


#
# Job Results
#

class JobResultFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Поиск',
    )
    created = django_filters.DateTimeFilter()
    completed = django_filters.DateTimeFilter()
    status = django_filters.MultipleChoiceFilter(
        choices=JobResultStatusChoices,
        null_value=None
    )

    class Meta:
        model = JobResult
        fields = [
            'id', 'created', 'completed', 'status', 'user', 'obj_type', 'name'
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(user__username__icontains=value)
        )


#
# ContentTypes
#

class ContentTypeFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Поиск',
    )

    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(app_label__icontains=value) |
            Q(model__icontains=value)
        )
