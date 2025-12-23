import os
import shutil
import hashlib
from datetime import datetime, timedelta
import re
import locale
import subprocess
try:
    import json
except:
    import simplejson as json
import filecmp

# Setting locale to the 'local' value
locale.setlocale(locale.LC_ALL, '')

exiftool_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Image-ExifTool', 'exiftool')

# -------- convenience methods -------------

def parse_date_exif(date_string):
    """
    extract date info from EXIF data
    YYYY:MM:DD HH:MM:SS
    or YYYY:MM:DD HH:MM:SS+HH:MM
    or YYYY:MM:DD HH:MM:SS-HH:MM
    or YYYY:MM:DD HH:MM:SSZ
    """

    # split into date and time
    elements = str(date_string).strip().split()  # ['YYYY:MM:DD', 'HH:MM:SS']

    if len(elements) < 1:
        return None

    # parse year, month, day
    date_entries = elements[0].split(':')  # ['YYYY', 'MM', 'DD']

    # check if three entries, nonzero data, and no decimal (which occurs for timestamps with only time but no date)
    if len(date_entries) == 3 and date_entries[0] > '0000' and '.' not in ''.join(date_entries):
        year = int(date_entries[0])
        month = int(date_entries[1])
        day = int(date_entries[2])
    else:
        return None

    # parse hour, min, second
    time_zone_adjust = False
    hour = 12  # defaulting to noon if no time data provided
    minute = 0
    second = 0

    if len(elements) > 1:
        time_entries = re.split('(\+|-|Z)', elements[1])  # ['HH:MM:SS', '+', 'HH:MM']
        time = time_entries[0].split(':')  # ['HH', 'MM', 'SS']

        if len(time) == 3:
            hour = int(time[0])
            minute = int(time[1])
            second = int(time[2].split('.')[0])
        elif len(time) == 2:
            hour = int(time[0])
            minute = int(time[1])

        # adjust for time-zone if needed
        if len(time_entries) > 2:
            time_zone = time_entries[2].split(':')  # ['HH', 'MM']

            if len(time_zone) == 2:
                time_zone_hour = int(time_zone[0])
                time_zone_min = int(time_zone[1])

                # check if + or -
                if time_entries[1] == '+':
                    time_zone_hour *= -1

                dateadd = timedelta(hours=time_zone_hour, minutes=time_zone_min)
                time_zone_adjust = True


    # form date object
    try:
        date = datetime(year, month, day, hour, minute, second)
    except ValueError:
        return None  # errors in time format

    # try converting it (some "valid" dates are way before 1900 and cannot be parsed by strtime later)
    try:
        date.strftime('%Y/%m-%b')  # any format with year, month, day, would work here.
    except ValueError:
        return None  # errors in time format

    # adjust for time zone if necessary
    if time_zone_adjust:
        date += dateadd

    return date



def get_oldest_timestamp(data, additional_groups_to_ignore, additional_tags_to_ignore, print_all_tags=False):
    """data as dictionary from json.  Should contain only time stamps except SourceFile"""

    # save only the oldest date
    date_available = False
    oldest_date = datetime.now()
    oldest_keys = []

    # save src file
    src_file = data['SourceFile']

    # ssetup tags to ignore
    ignore_groups = ['ICC_Profile'] + additional_groups_to_ignore
    ignore_tags = ['SourceFile', 'XMP:HistoryWhen'] + additional_tags_to_ignore


    if print_all_tags:
        print('All relevant tags:')

    # run through all keys
    for key in data.keys():

        # check if this key needs to be ignored, or is in the set of tags that must be used
        if (key not in ignore_tags) and (key.split(':')[0] not in ignore_groups) and 'GPS' not in key:

            date = data[key]

            if print_all_tags:
                print(str(key) + ', ' + str(date))

            # (rare) check if multiple dates returned in a list, take the first one which is the oldest
            if isinstance(date, list):
                date = date[0]

            try:
                exifdate = parse_date_exif(date)  # check for poor-formed exif data, but allow continuation
            except Exception as e:
                exifdate = None

            if exifdate and exifdate < oldest_date:
                date_available = True
                oldest_date = exifdate
                oldest_keys = [key]

            elif exifdate and exifdate == oldest_date:
                oldest_keys.append(key)

    if not date_available:
        oldest_date = None

    if print_all_tags:
        print()

    return src_file, oldest_date, oldest_keys



def check_for_early_morning_photos(date, day_begins):
    """check for early hour photos to be grouped with previous day"""

    if date.hour < day_begins:
        print('moving this photo to the previous day for classification purposes (day_begins=' + str(day_begins) + ')')
        date = date - timedelta(hours=date.hour+1)  # push it to the day before for classificiation purposes

    return date


#  this class is based on code from Sven Marnach (http://stackoverflow.com/questions/10075115/call-exiftool-from-a-python-script)
class ExifTool(object):
    """used to run ExifTool from Python and keep it open"""

    sentinel = "{ready}"

    def __init__(self, executable=exiftool_location, verbose=False):
        self.executable = executable
        self.verbose = verbose

    def __enter__(self):
        self.process = subprocess.Popen(
            ['perl', self.executable, "-stay_open", "True",  "-@", "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.process.stdin.write(b'-stay_open\nFalse\n')
        self.process.stdin.flush()
        self.process.stdin.close()
        self.process.stdout.close()
        self.process.stderr.close()
        self.process.wait()


    def execute(self, *args):
        args = args + ("-execute\n",)
        self.process.stdin.write(str.join("\n", args).encode('utf-8'))
        self.process.stdin.flush()
        output = ""
        fd = self.process.stdout.fileno()
        while not output.rstrip(' \t\n\r').endswith(self.sentinel):
            increment = os.read(fd, 4096)
            if self.verbose:
                sys.stdout.write(increment.decode('utf-8'))
            output += increment.decode('utf-8')
        return output.rstrip(' \t\n\r')[:-len(self.sentinel)]

    def get_metadata(self, *args):

        try:
            return json.loads(self.execute(*args))
        except ValueError:
            return []

def organize_by_date(src, structure="%Y/%m-%b", progress_cb=None, rename_format=None, recursive=False, copy_files=False, test=False, remove_duplicates=True, day_begins=0, keep_filename=False):
    """Core logic to organize files by date into subfolders."""
    if not os.path.exists(src): return False, "Invalid directory."

    additional_groups_to_ignore=['File']
    additional_tags_to_ignore=[]
    use_only_groups=None
    use_only_tags=None
    verbose=False

    # setup arguments to exiftool
    args = ['-j', '-a', '-G']

    # setup tags to ignore
    if use_only_tags is not None:
        additional_groups_to_ignore = []
        additional_tags_to_ignore = []
        for t in use_only_tags:
            args += ['-' + t]

    elif use_only_groups is not None:
        additional_groups_to_ignore = []
        for g in use_only_groups:
            args += ['-' + g + ':Time:All']

    else:
        args += ['-time:all']


    if recursive:
        args += ['-r']

    args += [src]

    moved_count = 0
    
    try:
        # get all metadata
        with ExifTool(verbose=verbose) as e:
            metadata = e.get_metadata(*args)
    except FileNotFoundError:
        return False, "ExifTool not found. Please make sure the 'Image-ExifTool' directory is in the root of the application."


    total_files = len(metadata)

    # parse output extracting oldest relevant date
    for idx, data in enumerate(metadata):

        # extract timestamp date for photo
        src_file, date, keys = get_oldest_timestamp(data, additional_groups_to_ignore, additional_tags_to_ignore)

        if progress_cb:
            progress_cb(idx + 1, total_files, f"Organizing {os.path.basename(src_file)}")

        # check if no valid date found
        if not date:
            continue

        # ignore hidden files
        if os.path.basename(src_file).startswith('.'):
            continue

        # early morning photos can be grouped with previous day (depending on user setting)
        date = check_for_early_morning_photos(date, day_begins)


        # create folder structure
        dir_structure = date.strftime(structure)
        dirs = dir_structure.split('/')
        dest_file_path = src
        for thedir in dirs:
            dest_file_path = os.path.join(dest_file_path, thedir)
            if not test and not os.path.exists(dest_file_path):
                os.makedirs(dest_file_path)

        # rename file if necessary
        filename = os.path.basename(src_file)

        if rename_format is not None and date is not None:
            _, ext = os.path.splitext(filename)
            filename = date.strftime(rename_format) + ext.lower()

        # setup destination file
        dest_file = os.path.join(dest_file_path, filename)
        root, ext = os.path.splitext(dest_file)


        # check for collisions
        append = 1
        fileIsIdentical = False

        while True:
            if os.path.isfile(dest_file):  # check for existing name
                if remove_duplicates and filecmp.cmp(src_file, dest_file):  # check for identical files
                    fileIsIdentical = True
                    break

                else:  # name is same, but file is different
                    if keep_filename:
                        orig_filename = os.path.splitext(os.path.basename(src_file))[0]
                        dest_file = root + '_' + orig_filename + '_' + str(append) + ext
                    else:
                        dest_file = root + '_' + str(append) + ext
                    append += 1
            else:
                break


        # finally move or copy the file
        if fileIsIdentical:
            continue  # ignore identical files
        else:
            if copy_files:
                shutil.copy2(src_file, dest_file)
            else:
                shutil.move(src_file, dest_file)
            moved_count += 1
        
    return True, f"Organized {moved_count} files into date-based folders."
