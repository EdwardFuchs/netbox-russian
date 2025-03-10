import binascii
import os

from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from netbox.config import get_config
from utilities.querysets import RestrictedQuerySet
from utilities.utils import flatten_dict
from .constants import *


__all__ = (
    'ObjectPermission',
    'Token',
    'UserConfig',
)


#
# Proxy models for admin
#

class AdminGroup(Group):
    """
    Proxy contrib.auth.models.Group for the admin UI
    """
    class Meta:
        verbose_name_plural = "Группы"
        verbose_name = 'Группа'
        proxy = True


class AdminUser(User):
    """
    Proxy contrib.auth.models.User for the admin UI
    """
    class Meta:
        verbose_name_plural = "Пользователи"
        verbose_name = 'Пользователь'
        proxy = True


#
# User preferences
#

class UserConfig(models.Model):
    """
    This model stores arbitrary user-specific preferences in a JSON data structure.
    """
    user = models.OneToOneField(
        verbose_name = "пользователь",
        to=User,
        on_delete=models.CASCADE,
        related_name='config'
    )
    data = models.JSONField(
        verbose_name = "данные",
        default=dict
    )

    class Meta:
        ordering = ['user']
        verbose_name = verbose_name_plural = 'Пользовательские настройки'

    def get(self, path, default=None):
        """
        Retrieve a configuration parameter specified by its dotted path. Example:

            userconfig.get('foo.bar.baz')

        :param path: Dotted path to the configuration key. For example, 'foo.bar' returns self.data['foo']['bar'].
        :param default: Default value to return for a nonexistent key (default: None).
        """
        d = self.data
        keys = path.split('.')

        # Iterate down the hierarchy, returning the default value if any invalid key is encountered
        try:
            for key in keys:
                d = d[key]
            return d
        except (TypeError, KeyError):
            pass

        # If the key is not found in the user's config, check for an application-wide default
        config = get_config()
        d = config.DEFAULT_USER_PREFERENCES
        try:
            for key in keys:
                d = d[key]
            return d
        except (TypeError, KeyError):
            pass

        # Finally, return the specified default value (if any)
        return default

    def all(self):
        """
        Return a dictionary of all defined keys and their values.
        """
        return flatten_dict(self.data)

    def set(self, path, value, commit=False):
        """
        Define or overwrite a configuration parameter. Example:

            userconfig.set('foo.bar.baz', 123)

        Leaf nodes (those which are not dictionaries of other nodes) cannot be overwritten as dictionaries. Similarly,
        branch nodes (dictionaries) cannot be overwritten as single values. (A TypeError exception will be raised.) In
        both cases, the existing key must first be cleared. This safeguard is in place to help avoid inadvertently
        overwriting the wrong key.

        :param path: Dotted path to the configuration key. For example, 'foo.bar' sets self.data['foo']['bar'].
        :param value: The value to be written. This can be any type supported by JSON.
        :param commit: If true, the UserConfig instance will be saved once the new value has been applied.
        """
        d = self.data
        keys = path.split('.')

        # Iterate through the hierarchy to find the key we're setting. Raise TypeError if we encounter any
        # interim leaf nodes (keys which do not contain dictionaries).
        for i, key in enumerate(keys[:-1]):
            if key in d and type(d[key]) is dict:
                d = d[key]
            elif key in d:
                err_path = '.'.join(path.split('.')[:i + 1])
                raise TypeError(f"Key '{err_path}' is a leaf node; cannot assign new keys")
            else:
                d = d.setdefault(key, {})

        # Set a key based on the last item in the path. Raise TypeError if attempting to overwrite a non-leaf node.
        key = keys[-1]
        if key in d and type(d[key]) is dict:
            raise TypeError(f"Key '{path}' has child keys; cannot assign a value")
        else:
            d[key] = value

        if commit:
            self.save()

    def clear(self, path, commit=False):
        """
        Delete a configuration parameter specified by its dotted path. The key and any child keys will be deleted.
        Example:

            userconfig.clear('foo.bar.baz')

        Invalid keys will be ignored silently.

        :param path: Dotted path to the configuration key. For example, 'foo.bar' deletes self.data['foo']['bar'].
        :param commit: If true, the UserConfig instance will be saved once the new value has been applied.
        """
        d = self.data
        keys = path.split('.')

        for key in keys[:-1]:
            if key not in d:
                break
            if type(d[key]) is dict:
                d = d[key]

        key = keys[-1]
        d.pop(key, None)  # Avoid a KeyError on invalid keys

        if commit:
            self.save()


@receiver(post_save, sender=User)
def create_userconfig(instance, created, raw=False, **kwargs):
    """
    Automatically create a new UserConfig when a new User is created. Skip this if importing a user from a fixture.
    """
    if created and not raw:
        config = get_config()
        UserConfig(user=instance, data=config.DEFAULT_USER_PREFERENCES).save()


#
# REST API
#

class Token(models.Model):
    """
    An API token used for user authentication. This extends the stock model to allow each user to have multiple tokens.
    It also supports setting an expiration time and toggling write ability.
    """
    user = models.ForeignKey(
        verbose_name = "пользователь",
        to=User,
        on_delete=models.CASCADE,
        related_name='tokens'
    )
    created = models.DateTimeField(
        verbose_name = "создано",
        auto_now_add=True
    )
    expires = models.DateTimeField(
        verbose_name = "истекает",
        blank=True,
        null=True
    )
    key = models.CharField(
        verbose_name = "Ключ",
        max_length=40,
        unique=True,
        validators=[MinLengthValidator(40)]
    )
    write_enabled = models.BooleanField(
        verbose_name = "запись разрешена",
        default=True,
        help_text='Permit create/update/delete operations using this key'
    )
    description = models.CharField(
        verbose_name = "Описание",
        max_length=200,
        blank=True
    )

    class Meta:
        verbose_name = "Token"
        verbose_name_plural = "Tokens"
        pass

    def __str__(self):
        # Only display the last 24 bits of the token to avoid accidental exposure.
        return f"{self.key[-6:]} ({self.user})"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key(
        verbose_name = "Ключ",)
        return super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        # Generate a random 160-bit key expressed in hexadecimal.
        return binascii.hexlify(os.urandom(20)).decode()

    @property
    def is_expired(self):
        if self.expires is None or timezone.now() < self.expires:
            return False
        return True


#
# Permissions
#

class ObjectPermission(models.Model):
    """
    A mapping of view, add, change, and/or delete permission for users and/or groups to an arbitrary set of objects
    identified by ORM query parameters.
    """
    name = models.CharField(
        verbose_name = "название",
        max_length=100
    )
    description = models.CharField(
        verbose_name = "Описание",
        max_length=200,
        blank=True
    )
    enabled = models.BooleanField(
        verbose_name = "включен",
        default=True
    )
    object_types = models.ManyToManyField(
        verbose_name = "Типы",
        to=ContentType,
        limit_choices_to=OBJECTPERMISSION_OBJECT_TYPES,
        related_name='object_permissions'
    )
    groups = models.ManyToManyField(
        verbose_name = "группы",
        to=Group,
        blank=True,
        related_name='object_permissions'
    )
    users = models.ManyToManyField(
        verbose_name = "Пользователи",
        to=User,
        blank=True,
        related_name='object_permissions'
    )
    actions = ArrayField(
        base_field=models.CharField(max_length=30),
        help_text="The list of actions granted by this permission"
    )
    constraints = models.JSONField(
        verbose_name = "ограничения",
        blank=True,
        null=True,
        help_text="Queryset filter matching the applicable objects of the selected type(s)"
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        verbose_name_plural = "разрешения"
        ordering = ['name']
        verbose_name = "разрешение"

    def __str__(self):
        return self.name

    def list_constraints(self):
        """
        Return all constraint sets as a list (even if only a single set is defined).
        """
        if type(self.constraints) is not list:
            return [self.constraints]
        return self.constraints
