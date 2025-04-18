# monitor/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.conf import settings
from pathlib import Path
import datetime
import calendar
from .forms import SiteForm
from .models import Site

@cache_page(60 * 5)  # Cache the view for 5 minutes
@login_required
def calendar_view(request, year=None, month=None):
    # Get the current date
    today = datetime.date.today()
    
    # Determine the year and month to display
    if year and month:
        year = int(year)
        month = int(month)
    else:
        year = today.year
        month = today.month

    # Path to the base backup directory from settings.py
    base_backup_dir = Path(settings.BASE_BACKUP_DIR)

    # Create a calendar object
    cal = calendar.Calendar(firstweekday=0)  # Week starts on Monday (0)
    month_cal = cal.monthdatescalendar(year, month)  # List of weeks in the month
    
    #DDEBUG
    # for i in month_cal:
    #     print(i)
    #     print("\n")

    
    

    # Function to get backup dates from a directory
    def get_backup_dates(directory):
        print("Check backup dates")
        print(directory)
        backup_dates = set()
        if directory.exists() and directory.is_dir():

            for date_dir in directory.iterdir():
                print("Check date dir")
                print(date_dir)
                if date_dir.is_dir():
                    try:
                        date = datetime.datetime.strptime(date_dir.name, '%Y-%m-%d').date()
                        backup_dates.add(date)
                    except ValueError:
                        continue
        return backup_dates

    # Get the backup dates for db and www
    backup_dates = get_backup_dates(base_backup_dir) 
    

    # print(month_cal)
    # Create a dictionary to hold information about each date
    date_info = {}

    for week in month_cal:
        for date in week:
            date_str = date.isoformat()
            date_info[date_str] = {
                'full_backup': date in backup_dates,
                # 'partial': date in backup_dates,
            }

    # List of day names to display in the calendar header
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    # Calculate previous and next month for navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1

    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    # Get all sites
    all_sites = Site.objects.all()

    # Context data to pass to the template
    context = {
        'month_name': calendar.month_name[month],
        'year': year,
        'month': month,
        'month_cal': month_cal,
        'date_info': date_info,
        'day_names': day_names,
        'today': today,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'all_sites': all_sites,
    }

    return render(request, 'monitor/calendar.html', context)

@login_required
def site_create_view(request):
    if request.method == 'POST':
        form = SiteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('calendar')  # Redirect to the calendar view
    else:
        form = SiteForm()
    return render(request, 'monitor/site_form.html', {'form': form})

@login_required
def site_update_view(request, pk):
    site_obj = get_object_or_404(Site, pk=pk)
    if request.method == 'POST':
        form = SiteForm(request.POST, instance=site_obj)
        if form.is_valid():
            form.save()
            return redirect('site_list')  # Update to your preferred redirect
    else:
        form = SiteForm(instance=site_obj)
    return render(request, 'monitor/site_form.html', {'form': form})

@login_required
def site_list_view(request):
    sites = Site.objects.all()
    return render(request, 'monitor/site_list.html', {'sites': sites})

from django.shortcuts import render
from django.conf import settings
from pathlib import Path

def backup_info_view(request, date):
    print("Debug of DATE:")
    print(date)
    backup_data = get_backup_data(date)
    return render(request, 'monitor/backup_info.html', {'backup_data': backup_data})

def get_backup_data(date):
    backup_dir = Path(settings.BASE_BACKUP_DIR) / date / 'backups'
    backup_data = {
        'date': date,
        'databases': [],
        'sites': [],
        'other_files': [],
        'total_size': 0
    }

    if backup_dir.exists() and backup_dir.is_dir():
        # Check database backups
        db_dir = backup_dir / 'db'
        if db_dir.exists() and db_dir.is_dir():
            for file_path in db_dir.iterdir():
                if file_path.is_file() and file_path.suffix == '.sql':
                    file_stats = file_path.stat()
                    file_info = {
                        'name': file_path.name,
                        'size': file_stats.st_size,
                        'size_mb': round(file_stats.st_size / (1024 * 1024), 2),
                        'modified_time': datetime.datetime.fromtimestamp(file_stats.st_mtime),
                        'path': str(file_path.relative_to(backup_dir))
                    }
                    backup_data['total_size'] += file_stats.st_size
                    backup_data['databases'].append(file_info)

        # Check website backups
        www_dir = backup_dir / 'www'
        if www_dir.exists() and www_dir.is_dir():
            for file_path in www_dir.iterdir():
                if file_path.is_file() and file_path.suffix in ['.gz', '.zip', '.tar']:
                    file_stats = file_path.stat()
                    file_info = {
                        'name': file_path.name,
                        'size': file_stats.st_size,
                        'size_mb': round(file_stats.st_size / (1024 * 1024), 2),
                        'modified_time': datetime.datetime.fromtimestamp(file_stats.st_mtime),
                        'path': str(file_path.relative_to(backup_dir))
                    }
                    backup_data['total_size'] += file_stats.st_size
                    backup_data['sites'].append(file_info)

        # Check for any other files in the backup directory
        for file_path in backup_dir.glob('**/*'):
            if file_path.is_file() and file_path.parent not in [db_dir, www_dir]:
                file_stats = file_path.stat()
                file_info = {
                    'name': file_path.name,
                    'size': file_stats.st_size,
                    'size_mb': round(file_stats.st_size / (1024 * 1024), 2),
                    'modified_time': datetime.datetime.fromtimestamp(file_stats.st_mtime),
                    'path': str(file_path.relative_to(backup_dir))
                }
                backup_data['total_size'] += file_stats.st_size
                backup_data['other_files'].append(file_info)

    # Convert total size to MB
    backup_data['total_size_mb'] = round(backup_data['total_size'] / (1024 * 1024), 2)
    
    return backup_data
