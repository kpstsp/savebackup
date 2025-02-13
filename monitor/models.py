from django.db import models

# Create your models here.
class Site(models.Model):
    name = models.CharField(max_length=100, unique=True)
    has_db = models.BooleanField(default=False)
    files_arch_template = models.CharField(max_length=100, default='{name}_{date}.tar.gz')
    db_arch_template = models.CharField(max_length=100, default='{name}_{date}.sql')
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