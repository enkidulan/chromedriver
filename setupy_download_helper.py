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
import platform

here = os.path.dirname(os.path.abspath(__file__))

CHROMEDRIVER_VERSION = '2.10'
platform_version = '64' if platform.uname()[4] == 'x86_64' else '32'
CHROMEDRIVER_URL_BASE = "http://chromedriver.storage.googleapis.com/%s/" + "chromedriver_linux%s.zip" % platform_version
DEST_FILE_NAME = 'CHROMEDRIVER'


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
    sys.stdout.write("chromedriver downloaded and can be reached by following path %s" % full_path)
    os.chmod(full_path, 0o755)


def data_loader(command_subclass):
    """A decorator for classes subclassing one of the setuptools commands.

    It modifies the run() method so that it prints a friendly greeting.
    """
    orig_run = command_subclass.run

    def modified_run(self):
        # base_dir = getattr(self, 'install_lib', None) or getattr(self, 'egg_output', None) or here
        base_path = join(here, 'chromedriver')
        self.execute(
            download_ziped_resource,
            (base_path,
             CHROMEDRIVER_URL_BASE % CHROMEDRIVER_VERSION,
             DEST_FILE_NAME,
             True),
            msg="Downloading %s" % DEST_FILE_NAME)
        self.distribution.data_files = [join(base_path, DEST_FILE_NAME)]
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
