from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import os
import zipfile

MAX_FLP_SIZE = 256 * 1024 * 1024


def is_project(name):
    name = name.lower()
    return name.endswith('.flp') and 'autosave' not in name and 'overwritten' not in name


@dataclass(frozen=True)
class ProjectSource:
    path: Path
    relative_path: str
    member_index: int | None = None

    @contextmanager
    def open(self):
        if self.member_index is None:
            if self.path.stat().st_size > MAX_FLP_SIZE:
                raise ValueError('FLP exceeds 256 MiB limit')
            with self.path.open('rb') as stream:
                yield stream
        else:
            with zipfile.ZipFile(self.path) as archive:
                member = archive.infolist()[self.member_index]
                if member.file_size > MAX_FLP_SIZE:
                    raise ValueError('FLP exceeds 256 MiB limit')
                with archive.open(member) as stream:
                    yield stream


def discover_projects(folder):
    root = Path(folder).resolve()
    sources, errors = [], []
    def walk_error(exc):
        errors.append(str(exc))
    for directory, dirs, files in os.walk(root, onerror=walk_error):
        dirs.sort()
        for filename in sorted(files):
            path = Path(directory) / filename
            relative = str(Path(root.name) / path.relative_to(root))
            if is_project(filename):
                sources.append(ProjectSource(path, relative))
            elif path.suffix.lower() == '.zip':
                try:
                    with zipfile.ZipFile(path) as archive:
                        found = False
                        for index, member in enumerate(archive.infolist()):
                            if not member.is_dir() and is_project(member.filename):
                                found = True
                                display = member.filename.replace('\\', '/').split('/')
                                sources.append(ProjectSource(path, os.path.join(relative, *display), index))
                        if not found:
                            errors.append(f'{relative}: no FLP projects in archive')
                except (OSError, zipfile.BadZipFile, NotImplementedError) as exc:
                    errors.append(f'{relative}: {exc}')
    return sources, errors
