# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound
import os
from f0cal import core
try:
    # Change here if project is renamed and does not equal the package name
    dist_name = 'my-device'
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound


def configure_conan():
    os.system("conan remote add f0cal-images https://api.bintray.com/conan/f0cal/images")


@core.plugin(name="my-device", sets="ini")
def ini(user_home, hook_name):
    configure_conan()
