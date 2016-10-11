import sys
if sys.version_info.major == 2:
    from urllib2 import urlopen
else:
    from urllib.request import urlopen
import os
import shutil
import zipfile
from tempfile import NamedTemporaryFile
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.bdist_egg import bdist_egg

from os.path import join

here = os.path.dirname(os.path.abspath(__file__))

CHROMEDRIVER_VERSION = None  # replace it after to appropriate module import
CHROMEDRIVER_URL_BASE = "http://chromedriver.storage.googleapis.com/%s/"
DOWNLOAD_LINKS = {
    'Linux64': "chromedriver_linux64.zip",
    'Linux32': "chromedriver_linux32.zip",
    'Windows': "chromedriver_win32.zip",
    'Darwin': "chromedriver_mac%s.zip",
}
BASE_DEST_FILE_NAME = 'chromedriver'


class RequestProgressWrapper():
    """ Simple helper for displaying file download progress;
    if works with file-like objects"""
    def __init__(self, obj):
        self.obj = obj
        self.total_size = float(obj.headers['content-length'].strip())
        self.url = obj.url
        self.bytes_so_far = 0

    def read(self, length):
        self.bytes_so_far += length
        percent = self.bytes_so_far / self.total_size
        percent = round(percent * 100, 2)
        sys.stdout.write(
            "%s: downloaded %d of %d bytes (%0.f%%)\r" %
            (self.url, self.bytes_so_far, self.total_size, percent))
        sys.stdout.flush()
        return self.obj.read(length)

    def __del__(self):
        sys.stdout.write('\n')


def download_ziped_resource(path, url, name, unzip=False):
    """ files download helper """
    full_path = join(path, name)
    if os.path.exists(full_path):
        return
    req = urlopen(url)
    data_destination = NamedTemporaryFile() if unzip else open(full_path, 'wb')
    with data_destination as f:
        shutil.copyfileobj(RequestProgressWrapper(req), f)
        if unzip:
            f.file.seek(0)
            zfile = zipfile.ZipFile(f.name)
            zfile.extractall(path)
            os.rename(os.path.join(path, zfile.namelist()[0]), full_path)
    sys.stdout.write("chromedriver downloaded and can be reached by following path '%s'. " % full_path)
    os.chmod(full_path, 0o755)


def data_loader(command_subclass):
    """A decorator for classes subclassing one of the setuptools commands.

    It modifies the run() method so that it prints a friendly greeting.
    """
    orig_run = command_subclass.run

    def modified_run(self):
        # base_dir = getattr(self, 'install_lib', None) or getattr(self, 'egg_output', None) or here
        binaries_loaction = join(here, 'chromedriver', 'bin')
        self.distribution.data_files = self.distribution.data_files or []
        for platform, link_platform in DOWNLOAD_LINKS.items():
            if platform == 'Darwin':
                link_platform = link_platform % ('64' if CHROMEDRIVER_VERSION >= '2.23' else '32')
            url = (CHROMEDRIVER_URL_BASE % CHROMEDRIVER_VERSION) + link_platform
            sys.stdout.write("Target link: %s;   " % url)
            dest_file_name = '-'.join((BASE_DEST_FILE_NAME, platform))
            self.execute(
                download_ziped_resource,
                (binaries_loaction,
                 url,
                 dest_file_name,
                 True),
                msg="Downloading %s" % dest_file_name)
            self.distribution.data_files.append(join(binaries_loaction, dest_file_name))
        orig_run(self)

    command_subclass.run = modified_run
    return command_subclass


@data_loader
class DevelopCommand(develop):
    pass


@data_loader
class InstallCommand(install):
    pass


@data_loader
class BdistEggCommand(bdist_egg):
    pass
