from django.db import models
from django.contrib.auth.models import User


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.username, filename)


class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to=user_directory_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.document.name


class Experiment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="experiments")
    doc = models.ForeignKey(Document, on_delete=models.CASCADE)
    param = models.IntegerField(default=0)

