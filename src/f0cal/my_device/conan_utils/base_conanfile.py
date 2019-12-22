import lzma
import os
import hashlib
import shutil
import types

import yaml
from conans import tools
from conans import ConanFile as _ConanFile
from conans.errors import ConanException

BUF_SIZE = 65536  # 64kb chunks (arbitrary size)
retries = 5


# TODO: Handle different hashes, per self._conan_data(self.index).hash_type
def assert_file_sha1(hash_filename, hash_value):
    # Assert file hash
    # TODO: Consider using Conan's tools.sha1sum()
    hasher = hashlib.sha1()
    with open(hash_filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            hasher.update(data)
    if not hasher.hexdigest() == hash_value:
        raise AssertionError(
            f"Hash mismatch on file {hash_filename}. Expected sha1 {hash_value}. Found {hasher.hexdigest()}. Hash may mismatch due to mounting and modification of filesystem, or use of different extraction application."
        )
    else:
        print("Hash matches")
        return True


def get_file_from_path(base_directory, base_filename, base_sha1_sum):
    base_file_path = os.path.join(base_directory, base_filename)
    print(f'Looking for file at path: {base_file_path}')
    found_base = False
    if os.path.isfile(base_file_path):
        try:
            assert_file_sha1(base_file_path, base_sha1_sum)
            shutil.copy2(base_file_path, '.', follow_symlinks=True)
            found_base = True
        except AssertionError as e:
            print(f'Found base at path {base_file_path} hash mismatch: {e}')
    return found_base



class ConanFile(_ConanFile):
    _DEFAULT_INDEX = 'No Index Specified'
    _SPECIAL_PLACE = "img"
    _FIELD_TO_INDEX = "history"  # Note 1
    _INDEX_VAR = "F0CAL_INDEX"  # Note 2
    settings = []
    options = []
    def __init__(self, output, runner, display_name, user, channel, **kwargs):
        super().__init__(output, runner, display_name, user, channel)
        # Conan loader.py requires name and version to be mutable, even though they aren't modified.
        self.name = self.conan_data["name"]
        self.index = tools.get_env(
            self._INDEX_VAR,
            default=self.conan_data["__default__"]
        )
        self.version = self.index

    def _conan_data(self):
        _ = self.conan_data
        _.update(self.conan_data["history"][self.index])
        return types.SimpleNamespace(**_)

    @property
    def author(self):
        return self.conan_data["author"]

    @property
    def license(self):
        return self.conan_data["license"]

    @property
    def description(self):
        return self.conan_data["description"]

    @property
    def topics(self):
        return self.conan_data["topics"]

    @property
    def url(self):
        """
        Original URL for the base image. Keep this URL as a record of the source, even if the link becomes broken.
        :return: URL
        """
        return self._conan_data().url

    @property
    def additional_urls(self):
        """
        Additional paths to the identical base image archive from mirrors and caches of the original URL.
        :return: URL
        """
        return self._conan_data().additional_urls

    @property
    def download_filename(self):
        return os.path.basename(self.url)

    @property
    def output_filename(self):
        return os.path.splitext(os.path.basename(self.url))[0]

    def base_from_paths(self) -> bool:
        # Optionally, pull file from local director(ies), using ':' delimited IMAGE_PATH environmental variable.
        # NOTE: Supporting only files in IMAGE_PATH directories themselves, not their respective sub-directories.
        # NOTE: Image paths must be absolute
        base_path = tools.get_env("IMAGE_PATH")

        found_base = False
        print(f'base_from_paths: {base_path}')
        if base_path:
            base_paths = base_path.split(':')
            for base_directory in base_paths:
                if get_file_from_path(base_directory, self.output_filename, self._conan_data().output_hash):
                    found_base = True
                    break
                if (
                        (self.output_filename is not self.download_filename)
                        and
                        get_file_from_path(base_directory, self.download_filename,
                                           self._conan_data().download_hash)
                ):
                    found_base = True
        return found_base

    def download_from_url(self, url) -> bool:
        """
        Download file from URL using wget with resume, with retries only on certain wget errors.
        :return: success (bool). If the download reported success after all retries
        """
        success = False
        for retry in range(retries):

            print(f"Download attempt {retry + 1} from URL {url}")
            # Download with resume
            # TODO: Consider replacing 'wget -c' with platform-agnostic method that supports resume on retries.
            #       wget is available for OSX, Windows, but does not come standard.
            #       Try Conan tools.download(), if it supports resume retries. Hard to trace Conan implementation.
            try:
                self.run(f'wget -c {url} -O {self.download_filename}.part')
                print("Download complete")
                success = True
                break
            except ConanException as e:
                wget_retval = int(str(e).split(" ")[1])
                    # Conan returns the error as the second word in the error string.
                if wget_retval not in {1, 3, 4, 130}:
                    # From `man wget`
                    # Continue on errors:
                    #   1   Generic error code. -> Not sure what triggers this, so retry.
                    #   3   File I/O error.
                    #   4   Network failure.
                    #   130 Interrupted by ctrl-c
                    # Don't continue on any other error, such as:
                    #   2   Parse error---for instance, when parsing command-line options, the .wgetrc or .netrc...
                    #   5   SSL verification failure.
                    #   6   Username/password authentication failure.
                    #   7   Protocol errors.
                    #   8   Server issued an error response. (inc. 404 File not found)
                    print(f'Download failed to complete with wget error {wget_retval}. Aborting download from URL...')
                    break
                print(f'Download failed to complete with wget error {wget_retval}. Resuming...')
        return success

    def download_base(self):
        # TODO: Consider this alternative from Brian, although:
        #       Doesn't support .xz archives such as for RasPi. Doesn't support download without decompress,
        #       so would need to rework this module, since we want to support use of local image or archive.
        # _d = self._conan_data()
        # dargs = dict([(_d.hash_type, _d.hash)])
        # tools.get(_d.url, destination="img", **dargs)

        success = False
        for url in [self.url, *self.additional_urls]:
            # TODO: Remove file on hash mismatch, before next URL.
            if (
                    self.download_from_url(url)
                    and
                    assert_file_sha1(f'{self.download_filename}.part', self._conan_data().download_hash)
            ):
                success = True
                break
        if not success:
            print('ERROR: Download of base image from all URLs failed.')
            exit(1)

        os.rename(f'{self.download_filename}.part', self.download_filename)

    def source(self):
        if not self.base_from_paths():
            self.download_base()

    def build(self):
        # If archive, extract it
        # TODO: Would be nice not to copy the archive in the first place. If left in-place, don't need to remove it.
        # TODO: Handle different archive types.
        if (self.output_filename is not self.download_filename) and os.path.isfile(self.download_filename):
            print(f'Extracting file {self.download_filename}')
            with lzma.open(self.download_filename) as f, open(self.output_filename, 'wb') as fout:
                file_content = f.read()
                fout.write(file_content)
                os.remove(self.download_filename)
        assert_file_sha1(self.output_filename, self._conan_data().output_hash)

        with open('conandata.yml') as f:
            base_data = yaml.safe_load(f)
        with open('f0cal_base.yml', 'w') as f:
            yaml.dump({**base_data, 'index': self.index}, f)

    def package(self):
        if 'move' in dir(self):
            # Requires enhanced conan with move(): https://github.com/JeffreyUrban/conan
            move_fn = self.move
        else:
            print('**********************************************************************************')
            print('* ALERT: It appears that you are using the standard Conan project, which copies  *')
            print('* files multiple times. To improve speed and reduce storage usage, when working  *')
            print('* with large device base images, install a fork of Conan supporting move() from: *')
            print('* https://github.com/JeffreyUrban/conan                                          *')
            print('**********************************************************************************')
            move_fn = self.copy

        self.copy('f0cal_base.yml', dst='.', keep_path=False)
        move_fn(self.output_filename, dst='bin', keep_path=False)

    def package_info(self):
        pass
