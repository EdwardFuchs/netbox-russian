from django import forms
from django.contrib.contenttypes.models import ContentType

from extras.choices import *
from extras.models import *
from extras.utils import FeatureQuery
from utilities.forms import (
    add_blank_choice, BulkEditForm, BulkEditNullBooleanSelect, ColorField, ContentTypeChoiceField, StaticSelect,
)

__all__ = (
    'ConfigContextBulkEditForm',
    'CustomFieldBulkEditForm',
    'CustomLinkBulkEditForm',
    'ExportTemplateBulkEditForm',
    'JournalEntryBulkEditForm',
    'TagBulkEditForm',
    'WebhookBulkEditForm',
)


class CustomFieldBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=CustomField.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(
        label='Описание',
        required=False
    )
    required = forms.NullBooleanField(
        label='Обязательный',
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    weight = forms.IntegerField(
        label='Вес',
        required=False
    )

    nullable_fields = ('description',)


class CustomLinkBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=CustomLink.objects.all(),
        widget=forms.MultipleHiddenInput
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
        widget=BulkEditNullBooleanSelect()
    )
    new_window = forms.NullBooleanField(
        label='Новое окно',
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    weight = forms.IntegerField(
        label='Вес',
        required=False
    )
    button_class = forms.ChoiceField(
        label='Класс кнопки',
        choices=add_blank_choice(CustomLinkButtonClassChoices),
        required=False,
        widget=StaticSelect()
    )


class ExportTemplateBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ExportTemplate.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    content_type = ContentTypeChoiceField(
        label='Тип данных',
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('export_templates'),
        required=False
    )
    description = forms.CharField(
        label='Описание',
        max_length=200,
        required=False
    )
    mime_type = forms.CharField(
        label='Тип',
        max_length=50,
        required=False
    )
    file_extension = forms.CharField(
        label='Расширение',
        max_length=15,
        required=False
    )
    as_attachment = forms.NullBooleanField(
        label='Как вложение',
        required=False,
        widget=BulkEditNullBooleanSelect()
    )

    nullable_fields = ('description', 'mime_type', 'file_extension')


class WebhookBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Webhook.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    enabled = forms.NullBooleanField(
        label='Включен',
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    type_create = forms.NullBooleanField(
        label='Тип создать',
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    type_update = forms.NullBooleanField(
        label='Тип редактировать',
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    type_delete = forms.NullBooleanField(
        label='Тип удалить',
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    http_method = forms.ChoiceField(
        choices=add_blank_choice(WebhookHttpMethodChoices),
        required=False,
        label='Метод HTTP'
    )
    payload_url = forms.CharField(
        required=False,
        label='Payload URL'
    )
    ssl_verification = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label='SSL проверка'
    )
    secret = forms.CharField(
        label='Ключ',
        required=False
    )
    ca_file_path = forms.CharField(
        required=False,
        label='CA file path'
    )

    nullable_fields = ('secret', 'conditions', 'ca_file_path')


class TagBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    color = ColorField(
        label='Цвет',
        required=False
    )
    description = forms.CharField(
        label='Описание',
        max_length=200,
        required=False
    )

    nullable_fields = ('description',)


class ConfigContextBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConfigContext.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    weight = forms.IntegerField(
        label='Вес',
        required=False,
        min_value=0
    )
    is_active = forms.NullBooleanField(
        label='Активно',
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    description = forms.CharField(
        label='Описание',
        required=False,
        max_length=100
    )

    nullable_fields = ('description',)


class JournalEntryBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=JournalEntry.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    kind = forms.ChoiceField(
        label='Вид',
        choices=add_blank_choice(JournalEntryKindChoices),
        required=False
    )
    comments = forms.CharField(
        label='Комментарии',
        required=False,
        widget=forms.Textarea()
    )
