from django.core.management.base import BaseCommand
from monitor.models import Backup, Site
from django.conf import settings
from pathlib import Path
import datetime
from collections import defaultdict

class Command(BaseCommand):
    help = 'Scan backups and update the database'

    def collect_backups(self, directory, is_db=False):
        backups = []
        directory = Path(directory)
        if directory.exists() and directory.is_dir():
            for date_dir in directory.iterdir():
                if date_dir.is_dir():
                    try:
                        date = datetime.datetime.strptime(date_dir.name, '%Y-%m-%d').date()
                        backup_dir = date_dir / 'backups' / ('db' if is_db else 'www')
                        for file_path in backup_dir.glob('*'):
                            filename = file_path.name
                            site_name = filename.split('_')[0]
                            backups.append({
                                'site_name': site_name,
                                'date': date,
                                'has_db': is_db,
                                'has_www': not is_db
                            })
                    except ValueError:
                        continue
        return backups

    def merge_backups(self, db_backups, www_backups):
        all_backups = defaultdict(dict)
        for backup in db_backups + www_backups:
            key = (backup['site_name'], backup['date'])
            all_backups[key].update(backup)
        return all_backups

    def handle(self, *args, **kwargs):
        base_backup_dir = Path(settings.BASE_BACKUP_DIR)

        db_backups = self.collect_backups(base_backup_dir / 'db', is_db=True)
        www_backups = self.collect_backups(base_backup_dir / 'www', is_db=False)

        all_backups = self.merge_backups(db_backups, www_backups)

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

        self.stdout.write(self.style.SUCCESS('Successfully scanned backups'))