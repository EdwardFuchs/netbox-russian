from django import forms

from netbox.forms import NetBoxModelForm
from tenancy.models import *
from utilities.forms import (
    BootstrapMixin, CommentField, DynamicModelChoiceField, SlugField, SmallTextarea, StaticSelect,
)

__all__ = (
    'ContactAssignmentForm',
    'ContactForm',
    'ContactGroupForm',
    'ContactRoleForm',
    'TenantForm',
    'TenantGroupForm',
)


#
# Tenants
#

class TenantGroupForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )
    slug = SlugField()

    class Meta:
        verbose_name = "Tenant Group Form"
        verbose_name_plural = "Tenant Group Forms"
        model = TenantGroup
        fields = [
            'parent', 'name', 'slug', 'description', 'tags',
        ]


class TenantForm(NetBoxModelForm):
    slug = SlugField()
    group = DynamicModelChoiceField(
        label='Группа',
        queryset=TenantGroup.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        ('Учреждение', ('name', 'slug', 'group', 'description', 'tags')),
    )

    class Meta:
        verbose_name = "Tenant Form"
        verbose_name_plural = "Tenant Forms"
        model = Tenant
        fields = (
            'name', 'slug', 'group', 'description', 'comments', 'tags',
        )


#
# Contacts
#

class ContactGroupForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False
    )
    slug = SlugField()

    class Meta:
        verbose_name = "Contact Group Form"
        verbose_name_plural = "Contact Group Forms"
        model = ContactGroup
        fields = ('parent', 'name', 'slug', 'description', 'tags')


class ContactRoleForm(NetBoxModelForm):
    slug = SlugField()

    class Meta:
        verbose_name = "Contact Role Form"
        verbose_name_plural = "Contact Role Forms"
        model = ContactRole
        fields = ('name', 'slug', 'description', 'tags')


class ContactForm(NetBoxModelForm):
    group = DynamicModelChoiceField(
        label='Группа',
        queryset=ContactGroup.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        ('Контакт', ('group', 'name', 'title', 'phone', 'email', 'address', 'link', 'tags')),
    )

    class Meta:
        verbose_name = "Contact Form"
        verbose_name_plural = "Contact Forms"
        model = Contact
        fields = (
            'group', 'name', 'title', 'phone', 'email', 'address', 'link', 'comments', 'tags',
        )
        widgets = {
            'address': SmallTextarea(attrs={'rows': 3}),
        }


class ContactAssignmentForm(BootstrapMixin, forms.ModelForm):
    group = DynamicModelChoiceField(
        label='Группа',
        queryset=ContactGroup.objects.all(),
        required=False,
        initial_params={
            'contacts': '$contact'
        }
    )
    contact = DynamicModelChoiceField(
        label='Контакт',
        queryset=Contact.objects.all(),
        query_params={
            'group_id': '$group'
        }
    )
    role = DynamicModelChoiceField(
        label='Роль',
        queryset=ContactRole.objects.all()
    )

    class Meta:
        verbose_name = "Contact Assignment Form"
        verbose_name_plural = "Contact Assignment Forms"
        model = ContactAssignment
        fields = (
            'group', 'contact', 'role', 'priority',
        )
        widgets = {
            'priority': StaticSelect(),
        }
