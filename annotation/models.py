import uuid
from django.db import models
from django.contrib.auth.models import User



class Annotation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    annotator_schema_version = models.CharField(max_length=8, default="v1.0")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    text = models.TextField()
    quote = models.TextField()
    # TODO: These should not be blank; `django-rest-framework` seems
    #     to require it...
    uri = models.CharField(max_length=4096, blank=False, null=True)
    user_id = models.IntegerField()
    user_username = models.CharField(max_length=128, blank=False, null=True)
    # user = models.CharField(max_length=128, blank=False, null=True)
    consumer = models.CharField(max_length=64, default="thedatashed")

    class Meta:
        ordering = ('created',)

    # def save(self, *args, **kwargs):
    #     print args
    #     if kwargs.has_key('request') and self.user is None:
    #         print("yes!")
    #         self.user= kwargs['request'].user
    #     super(Annotation, self).save(*args, **kwargs)


class Range(models.Model):
    start = models.CharField(max_length=128)
    end = models.CharField(max_length=128)
    startOffset = models.IntegerField()
    endOffset = models.IntegerField()
    annotation = models.ForeignKey(Annotation, related_name="ranges")
