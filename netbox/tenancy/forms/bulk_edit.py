from django import forms

from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import *
from utilities.forms import DynamicModelChoiceField

__all__ = (
    'ContactBulkEditForm',
    'ContactGroupBulkEditForm',
    'ContactRoleBulkEditForm',
    'TenantBulkEditForm',
    'TenantGroupBulkEditForm',
)


#
# Tenants
#

class TenantGroupBulkEditForm(NetBoxModelBulkEditForm):
    parent = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        label='Описание',
        max_length=200,
        required=False
    )

    model = TenantGroup
    nullable_fields = ('parent', 'description')


class TenantBulkEditForm(NetBoxModelBulkEditForm):
    group = DynamicModelChoiceField(
        label='Группа',
        queryset=TenantGroup.objects.all(),
        required=False
    )

    model = Tenant
    fieldsets = (
        (None, ('group',)),
    )
    nullable_fields = ('group',)


#
# Contacts
#

class ContactGroupBulkEditForm(NetBoxModelBulkEditForm):
    parent = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        label='Описание',
        max_length=200,
        required=False
    )

    model = ContactGroup
    fieldsets = (
        (None, ('parent', 'description')),
    )
    nullable_fields = ('parent', 'description')


class ContactRoleBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        label='Описание',
        max_length=200,
        required=False
    )

    model = ContactRole
    fieldsets = (
        (None, ('description',)),
    )
    nullable_fields = ('description',)


class ContactBulkEditForm(NetBoxModelBulkEditForm):
    group = DynamicModelChoiceField(
        label='Группа',
        queryset=ContactGroup.objects.all(),
        required=False
    )
    title = forms.CharField(
        label='Название',
        max_length=100,
        required=False
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=50,
        required=False
    )
    email = forms.EmailField(
        label='email',
        required=False
    )
    address = forms.CharField(
        label='Адрес',
        max_length=200,
        required=False
    )
    link = forms.URLField(
        label='Ссылка',
        required=False
    )

    model = Contact
    fieldsets = (
        (None, ('group', 'title', 'phone', 'email', 'address', 'link')),
    )
    nullable_fields = ('group', 'title', 'phone', 'email', 'address', 'link', 'comments')
