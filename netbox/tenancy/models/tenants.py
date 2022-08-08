from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from mptt.models import TreeForeignKey

from netbox.models import NestedGroupModel, NetBoxModel

__all__ = (
    'Tenant',
    'TenantGroup',
)


class TenantGroup(NestedGroupModel):
    """
    An arbitrary collection of Tenants.
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
        verbose_name = "Группа учреждений"
        verbose_name_plural = "Группы учреждений"
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('tenancy:tenantgroup', args=[self.pk])


class Tenant(NetBoxModel):
    """
    A Tenant represents an organization served by the NetBox owner. This is typically a customer or an internal
    department.
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
    group = models.ForeignKey(
        verbose_name = "Группа",
        to='tenancy.TenantGroup',
        on_delete=models.SET_NULL,
        related_name='tenants',
        blank=True,
        null=True
    )
    description = models.CharField(
        verbose_name = "Описание",
        max_length=200,
        blank=True
    )
    comments = models.TextField(
        verbose_name = "комментарий",
        blank=True
    )

    # Generic relations
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    clone_fields = [
        'group', 'description',
    ]

    class Meta:
        verbose_name = "Учреждение"
        verbose_name_plural = "Учреждения"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tenancy:tenant', args=[self.pk])
