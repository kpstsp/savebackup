from django.db import models

# Create your models here.
class Site(models.Model):
    name = models.CharField(max_length=100)
    # url = models.URLField()
    # last_backup = models.DateTimeField(null=True, blank=True)
    # backup_frequency = models.DurationField()
    # backup_location = models.CharField(max_length=100)
    # backup_user = models.CharField(max_length=100)
    # backup_password = models.CharField(max_length=100)
    # backup_status = models.CharField(max_length=100)
    # backup_notes = models.TextField(blank=True)

    def __str__(self):
        return self.name
    

class Backup(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    date = models.DateField()
    has_db = models.BooleanField()
    has_www = models.BooleanField()
    # date = models.DateTimeField(auto_now_add=True)
    # status = models.CharField(max_length=100)
    # notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['site', 'date']

    def __str__(self):
        return f'{self.site.name} - {self.date}'    