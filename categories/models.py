from django.db import models
import uuid


class Categories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name
