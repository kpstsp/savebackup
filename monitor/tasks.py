from celery import shared_task
from .models import Backup
from django.conf import settings
from pathlib import Path
import datetime

from collections import defaultdict


def collect_backups(directory, is_db=False):
    backups =[]
    directory = Path(directory)
    if directory.exists() and directory.is_dir():
        for file_path in directory.glob('*tar.gz'):
            filename = file_path.name
            try:
                if is_db:
                    site_name, date_str = filename.rstrip('.tar.gz').split('_', 1)
                else:
                    #Expected format: www_<site_name>_YYYY-MM-DD.tar.gz
                    site_name, date_str = filename.rstrip('.tar.gz').split('_', 1)
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                backups.append({'site_name': site_name,
                                'date': date, 
                                'has_db': is_db,
                                'has_www': not is_db})
            except ValueError:
                continue
    return backups

def merge_backups(db_backups, www_backups):
    all_backups = defaultdict(dict)
    for backup in db_backups + www_backups:
        key = (backup['site_name'], backup['date'])
        all_backups[key].update(backup)
    return all_backups


@shared_task
def scan_backups():
    db_dir = settings.DB_BACKUP_DIR
    www_dir = settings.WWW_BACKUP_DIR

    db_backups = collect_backups(db_dir, is_db=True)
    www_backups = collect_backups(www_dir, is_db=False)

    all_backups = merge_backups(db_backups, www_backups)

    for key, data in all_backups.items():
        site_name = data['site_name']
        date = data['date']

        # Get or create the site
        site, created = Site.objects.get_or_create(name=site_name)

        # Get or create the backup record
        backup, created = Backup.objects.get_or_create(site=site, date=date)

        # Update the backup record
        backup.has_db = backup.has_db or data.get('has_db', False)
        backup.has_www = backup.has_www or data.get('has_www', False)
        backup.save()

        


