import datetime
import os

import attr
from slugify import slugify

from mars.objects import BaseObject


@attr.s(slots=True)
class File(BaseObject):
    path = attr.ib()

    folder = attr.ib(default=None)
    name = attr.ib(default=None)
    raw_name = attr.ib(default=None)
    extension = attr.ib(default=None)

    meta = attr.ib(default=None)

    _content = attr.ib(init=False, default=None)

    @property
    def content(self):
        if not self._content:
            with open(self.name, "r", encoding="utf-8") as raw:
                self._content = list(raw.readlines())

        return self._content

    @property
    def first_line(self):
        return self.content[0]

    @property
    def meta_data(self):
        get_key = lambda key: getattr(os.path, key)(self.path)
        from_t = lambda t: datetime.datetime.fromtimestamp(t)

        return dict(
            ctime=from_t(get_key("getctime")),
            mtime=from_t(get_key("getmtime")),
            size=get_key("getsize")
        )

    def from_path(self):
        file_folder = os.path.split(self.path)[0]
        file_name = os.path.split(self.path)[1]

        raw_name = file_name.split('.')[0]
        extension = file_name.split('.')[1]

        return attr.evolve(self, **dict(
            path=self.path,
            name=file_name,
            folder=file_folder,
            raw_name=raw_name,
            extension=extension,
            meta=self.meta_data
        ))

    def rename_if_different(self, new_name):
        if self.name == new_name:
            return False

        at = 0
        while True:
            at += 1

            if not os.path.isfile(new_name):
                os.rename(self.name, new_name)
                break

            parts = new_name.split(".")
            raw_name = parts[0].split("@")[0]

            new_name = "{name}@{at}.{ext}".format(
                name=raw_name, at=at, ext=parts[1]
            )

        new_path = os.path.join(os.path.split(self.path)[0], new_name)

        self.name = new_name
        self.path = new_path

        return True


def reformat_file(f):
    return reformat_content(f.content)


def reformat_string(txt):
    return reformat_content(txt.split("\n"))


def handle_name(f):
    """
    Loads the file and changes its filename to very first line of its content

    :param f: File object
    :return: Modified file objects
    """

    first_line = f.first_line
    new_name = slugify(first_line, separator="_") + "." + f.extension

    is_changed = f.rename_if_different(new_name)

    return f, is_changed


def dir_for_extension(dir_path, extension=None):
    """
    Returns an iterator which yields File objects from an directory.

    :param dir_path: Directory path for os.listdir method
    :param extension: File extension that determines lookup filter
    :return: Generator of File object
    """

    for file_name in os.listdir(dir_path):
        if extension and not file_name.endswith(extension):
            continue

        file_path = os.path.join(dir_path, file_name)

        yield File(file_path).from_path()


def run():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    extension = ".md"

    for f in dir_for_extension(current_dir, extension):
        f, is_changed = handle_name(f)
        print(f.name, is_changed)

        # reformat = reformat_file(f)
        # print(reformat)


if __name__ == '__main__':
    run()