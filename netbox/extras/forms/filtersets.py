from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

from dcim.models import DeviceRole, DeviceType, Platform, Region, Site, SiteGroup
from extras.choices import *
from extras.models import *
from extras.utils import FeatureQuery
from netbox.forms.base import NetBoxModelFilterSetForm
from tenancy.models import Tenant, TenantGroup
from utilities.forms import (
    add_blank_choice, APISelectMultiple, BOOLEAN_WITH_BLANK_CHOICES, ContentTypeChoiceField,
    ContentTypeMultipleChoiceField, DateTimePicker, DynamicModelMultipleChoiceField, FilterForm, MultipleChoiceField,
    StaticSelect, TagFilterField,
)
from virtualization.models import Cluster, ClusterGroup, ClusterType

__all__ = (
    'ConfigContextFilterForm',
    'CustomFieldFilterForm',
    'CustomLinkFilterForm',
    'ExportTemplateFilterForm',
    'JournalEntryFilterForm',
    'LocalConfigContextFilterForm',
    'ObjectChangeFilterForm',
    'TagFilterForm',
    'WebhookFilterForm',
)


class CustomFieldFilterForm(FilterForm):
    fieldsets = (
        (None, ('q',)),
        ('Атрибуты', ('type', 'content_type_id', 'weight', 'required')),
    )
    content_type_id = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields'),
        required=False,
        label='Object type'
    )
    type = MultipleChoiceField(
        choices=CustomFieldTypeChoices,
        required=False,
        label='Тип поля'
    )
    weight = forms.IntegerField(
        label='Вес',
        required=False
    )
    required = forms.NullBooleanField(
        label='Обязательный',
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class CustomLinkFilterForm(FilterForm):
    fieldsets = (
        (None, ('q',)),
        ('Атрибуты', ('content_type', 'enabled', 'new_window', 'weight')),
    )
    content_type = ContentTypeChoiceField(
        label='Тип данных',
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_links'),
        required=False
    )
    enabled = forms.NullBooleanField(
        label='Включен',
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    new_window = forms.NullBooleanField(
        label='Новое окно',
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    weight = forms.IntegerField(
        label='Вес',
        required=False
    )


class ExportTemplateFilterForm(FilterForm):
    fieldsets = (
        (None, ('q',)),
        ('Атрибуты', ('content_type', 'mime_type', 'file_extension', 'as_attachment')),
    )
    content_type = ContentTypeChoiceField(
        label='Тип данных',
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('export_templates'),
        required=False
    )
    mime_type = forms.CharField(
        required=False,
        label='MIME тип'
    )
    file_extension = forms.CharField(
        label='Расширение',
        required=False
    )
    as_attachment = forms.NullBooleanField(
        label='Как вложение',
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class WebhookFilterForm(FilterForm):
    fieldsets = (
        (None, ('q',)),
        ('Атрибуты', ('content_type_id', 'http_method', 'enabled')),
        ('Events', ('type_create', 'type_update', 'type_delete')),
    )
    content_type_id = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('webhooks'),
        required=False,
        label='Object type'
    )
    http_method = MultipleChoiceField(
        choices=WebhookHttpMethodChoices,
        required=False,
        label='Метод HTTP'
    )
    enabled = forms.NullBooleanField(
        label='Включен',
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    type_create = forms.NullBooleanField(
        label='Тип создать',
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    type_update = forms.NullBooleanField(
        label='Тип редактировать',
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    type_delete = forms.NullBooleanField(
        label='Тип удалить',
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class TagFilterForm(FilterForm):
    model = Tag
    content_type_id = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.filter(FeatureQuery('tags').get_query()),
        required=False,
        label='Тип объекта с тегами'
    )


class ConfigContextFilterForm(FilterForm):
    fieldsets = (
        (None, ('q', 'tag_id')),
        ('Метоположение', ('region_id', 'site_group_id', 'site_id')),
        ('Устройство', ('device_type_id', 'platform_id', 'role_id')),
        ('Кластер', ('cluster_type_id', 'cluster_group_id', 'cluster_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id'))
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label='Регионы'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label='Группы адресов'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Адреса'
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        label='Типы устройств'
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label='Роли'
    )
    platform_id = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        label='Платформы'
    )
    cluster_type_id = DynamicModelMultipleChoiceField(
        queryset=ClusterType.objects.all(),
        required=False,
        label='Типы кластеров',
        fetch_trigger='open'
    )
    cluster_group_id = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        label='Группы кластеров'
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label='Кластеры'
    )
    tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label='Группы учреждений'
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label='Учреждение'
    )
    tag_id = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label='Теги'
    )


class LocalConfigContextFilterForm(forms.Form):
    local_context_data = forms.NullBooleanField(
        required=False,
        label='Имеет локальные данные контекста конфигурации',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class JournalEntryFilterForm(NetBoxModelFilterSetForm):
    model = JournalEntry
    fieldsets = (
        (None, ('q', 'tag')),
        ('Creation', ('created_before', 'created_after', 'created_by_id')),
        ('Attributes', ('assigned_object_type_id', 'kind'))
    )
    created_after = forms.DateTimeField(
        required=False,
        label='После',
        widget=DateTimePicker()
    )
    created_before = forms.DateTimeField(
        required=False,
        label='До',
        widget=DateTimePicker()
    )
    created_by_id = DynamicModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label='Пользователь',
        widget=APISelectMultiple(
            api_url='/api/users/users/',
        )
    )
    assigned_object_type_id = DynamicModelMultipleChoiceField(
        queryset=ContentType.objects.all(),
        required=False,
        label='Тип объекта',
        widget=APISelectMultiple(
            api_url='/api/extras/content-types/',
        )
    )
    kind = forms.ChoiceField(
        label='Вид',
        choices=add_blank_choice(JournalEntryKindChoices),
        required=False,
        widget=StaticSelect()
    )
    tag = TagFilterField(model)


class ObjectChangeFilterForm(FilterForm):
    model = ObjectChange
    fieldsets = (
        (None, ('q',)),
        ('Time', ('time_before', 'time_after')),
        ('Атрибуты', ('action', 'user_id', 'changed_object_type_id')),
    )
    time_after = forms.DateTimeField(
        required=False,
        label='После',
        widget=DateTimePicker()
    )
    time_before = forms.DateTimeField(
        required=False,
        label='До',
        widget=DateTimePicker()
    )
    action = forms.ChoiceField(
        label='Действие',
        choices=add_blank_choice(ObjectChangeActionChoices),
        required=False,
        widget=StaticSelect()
    )
    user_id = DynamicModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label='Пользователь',
        widget=APISelectMultiple(
            api_url='/api/users/users/',
        )
    )
    changed_object_type_id = DynamicModelMultipleChoiceField(
        queryset=ContentType.objects.all(),
        required=False,
        label='Тип объекта',
        widget=APISelectMultiple(
            api_url='/api/extras/content-types/',
        )
    )
