from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from mptt.models import TreeForeignKey

from netbox.models import ChangeLoggedModel, NestedGroupModel, OrganizationalModel, NetBoxModel
from netbox.models.features import WebhooksMixin
from tenancy.choices import *

__all__ = (
    'ContactAssignment',
    'Contact',
    'ContactGroup',
    'ContactRole',
)


class ContactGroup(NestedGroupModel):
    """
    An arbitrary collection of Contacts.
    """
    name = models.CharField(
        verbose_name = "название",
        max_length=100
    )
    slug = models.SlugField(
        verbose_name = "короткий URL",
        max_length=100
    )
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        db_index=True
    )
    description = models.CharField(
        verbose_name = "Описание",
        max_length=200,
        blank=True
    )

    class Meta:
        verbose_name = "Группа контакта"
        verbose_name_plural = "Группы контактов"
        ordering = ['name']
        unique_together = (
            ('parent', 'name')
        )

    def get_absolute_url(self):
        return reverse('tenancy:contactgroup', args=[self.pk])


class ContactRole(OrganizationalModel):
    """
    Functional role for a Contact assigned to an object.
    """
    name = models.CharField(
        verbose_name = "название",
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        verbose_name = "короткий URL",
        max_length=100,
        unique=True
    )
    description = models.CharField(
        verbose_name = "Описание",
        max_length=200,
        blank=True,
    )

    class Meta:
        verbose_name = "Роль контакта"
        verbose_name_plural = "Роли контактов"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tenancy:contactrole', args=[self.pk])


class Contact(NetBoxModel):
    """
    Contact information for a particular object(s) in NetBox.
    """
    group = models.ForeignKey(
        verbose_name = "Группа",
        to='tenancy.ContactGroup',
        on_delete=models.SET_NULL,
        related_name='contacts',
        blank=True,
        null=True
    )
    name = models.CharField(
        verbose_name = "ФИО",
        max_length=100
    )
    title = models.CharField(
        verbose_name = "Описание",
        max_length=100,
        blank=True
    )
    phone = models.CharField(
        verbose_name = "Телефон",
        max_length=50,
        blank=True
    )
    email = models.EmailField(
        blank=True
    )
    address = models.CharField(
        verbose_name = "Адрес",
        max_length=200,
        blank=True
    )
    link = models.URLField(
        verbose_name = "Ссылка",
        blank=True
    )
    comments = models.TextField(
        verbose_name = "комментарий",
        blank=True
    )

    clone_fields = [
        'group',
    ]

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"
        ordering = ['name']
        unique_together = (
            ('group', 'name')
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tenancy:contact', args=[self.pk])


class ContactAssignment(WebhooksMixin, ChangeLoggedModel):
    content_type = models.ForeignKey(
        verbose_name = "ип данных",
        to=ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveBigIntegerField()
    object = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id'
    )
    contact = models.ForeignKey(
        verbose_name = "Контакты",
        to='tenancy.Contact',
        on_delete=models.PROTECT,
        related_name='assignments'
    )
    role = models.ForeignKey(
        verbose_name = "Роль",
        to='tenancy.ContactRole',
        on_delete=models.PROTECT,
        related_name='assignments'
    )
    priority = models.CharField(
        verbose_name = "Приоритет",
        max_length=50,
        choices=ContactPriorityChoices,
        blank=True
    )

    clone_fields = ('content_type', 'object_id')

    class Meta:
        verbose_name = "Привязать контакт"
        verbose_name_plural = "Привязать контакты"
        ordering = ('priority', 'contact')
        unique_together = ('content_type', 'object_id', 'contact', 'role', 'priority')

    def __str__(self):
        if self.priority:
            return f"{self.contact} ({self.get_priority_display()})"
        return str(self.contact)

    def get_absolute_url(self):
        return reverse('tenancy:contact', args=[self.contact.pk])
