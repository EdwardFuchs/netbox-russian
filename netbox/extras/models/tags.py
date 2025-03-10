from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from taggit.models import TagBase, GenericTaggedItemBase

from netbox.models import ChangeLoggedModel
from netbox.models.features import ExportTemplatesMixin, WebhooksMixin
from utilities.choices import ColorChoices
from utilities.fields import ColorField


#
# Tags
#

class Tag(ExportTemplatesMixin, WebhooksMixin, ChangeLoggedModel, TagBase):
    id = models.BigAutoField(
        primary_key=True
    )
    color = ColorField(
        default=ColorChoices.COLOR_GREY
    )
    description = models.CharField(
        verbose_name = "Описание",
        max_length=200,
        blank=True,
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Теги"
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('extras:tag', args=[self.pk])

    def slugify(self, tag, i=None):
        # Allow Unicode in Tag slugs (avoids empty slugs for Tags with all-Unicode names)
        slug = slugify(tag, allow_unicode=True)
        if i is not None:
            slug += "_%d" % i
        return slug


class TaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(
        to=Tag,
        related_name="%(app_label)s_%(class)s_items",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Tagged Item"
        verbose_name_plural = "Tagged Items"
        index_together = (
            ("content_type", "object_id")
        )
