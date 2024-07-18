from django.db import models
import uuid

class Document(models.Model):
    document_type = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.document_type

class DocumentCode(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE)
    unique_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return str(self.unique_code)
