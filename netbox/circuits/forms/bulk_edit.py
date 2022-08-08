from django import forms
from django.utils.translation import gettext as _

from circuits.choices import CircuitStatusChoices
from circuits.models import *
from ipam.models import ASN
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import (
    add_blank_choice, CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, SmallTextarea,
    StaticSelect,
)

__all__ = (
    'CircuitBulkEditForm',
    'CircuitTypeBulkEditForm',
    'ProviderBulkEditForm',
    'ProviderNetworkBulkEditForm',
)


class ProviderBulkEditForm(NetBoxModelBulkEditForm):
    asn = forms.IntegerField(
        required=False,
        label='ASN (старый)'
    )
    asns = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        label='ASNы',
        required=False
    )
    account = forms.CharField(
        max_length=30,
        required=False,
        label='Номер счета'
    )
    portal_url = forms.URLField(
        required=False,
        label='Портал'
    )
    noc_contact = forms.CharField(
        required=False,
        widget=SmallTextarea,
        label='Контакты управляющего сетью'
    )
    admin_contact = forms.CharField(
        required=False,
        widget=SmallTextarea,
        label='Контакты администратора'
    )
    comments = CommentField(
        widget=SmallTextarea,
        label='Комментарии'
    )

    model = Provider
    fieldsets = (
        (None, ('asn', 'asns', 'account', 'portal_url', 'noc_contact', 'admin_contact')),
    )
    nullable_fields = (
        'asn', 'asns', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments',
    )


class ProviderNetworkBulkEditForm(NetBoxModelBulkEditForm):
    provider = DynamicModelChoiceField(
        label='Поставщик услуг',
        queryset=Provider.objects.all(),
        required=False
    )
    service_id = forms.CharField(
        max_length=100,
        required=False,
        label='Service ID'
    )
    description = forms.CharField(
        label='Описание',
        max_length=200,
        required=False
    )
    comments = CommentField(
        widget=SmallTextarea,
        label='Комментарии'
    )

    model = ProviderNetwork
    fieldsets = (
        (None, ('provider', 'service_id', 'description')),
    )
    nullable_fields = (
        'service_id', 'description', 'comments',
    )


class CircuitTypeBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        label='Описание',
        max_length=200,
        required=False
    )

    model = CircuitType
    fieldsets = (
        (None, ('description',)),
    )
    nullable_fields = ('description',)


class CircuitBulkEditForm(NetBoxModelBulkEditForm):
    type = DynamicModelChoiceField(
        label='Тип',
        queryset=CircuitType.objects.all(),
        required=False
    )
    provider = DynamicModelChoiceField(
        label='Поставщик услуг',
        queryset=Provider.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        label='Статус',
        choices=add_blank_choice(CircuitStatusChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    tenant = DynamicModelChoiceField(
        label='Учреждение',
        queryset=Tenant.objects.all(),
        required=False
    )
    commit_rate = forms.IntegerField(
        required=False,
        label='Скорость Мбит/с'
    )
    description = forms.CharField(
        label='Описание',
        max_length=100,
        required=False
    )
    comments = CommentField(
        widget=SmallTextarea,
        label='Комментарии'
    )

    model = Circuit
    fieldsets = (
        (None, ('type', 'provider', 'status', 'tenant', 'commit_rate', 'description')),
    )
    nullable_fields = (
        'tenant', 'commit_rate', 'description', 'comments',
    )
