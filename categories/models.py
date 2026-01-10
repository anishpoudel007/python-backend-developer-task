import uuid
from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    image_url = models.URLField(blank=True, null=True)
    active = models.IntegerField(default=1)  # 1=active, 0=inactive
    delete_status = models.IntegerField(default=0)  # 0=not deleted, 1=deleted
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name
