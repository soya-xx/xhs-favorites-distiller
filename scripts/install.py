#!/usr/bin/env python3
"""Install a standalone skill; back up the previous version on explicit replacement."""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import tempfile


def install(source, destination, replace=False):
    destination = Path(destination).expanduser()
    source = Path(source).resolve()
    if not (source/'SKILL.md').is_file():
        raise ValueError('Source is not a skill')
    if destination.exists() and not replace:
        raise ValueError('Skill already exists; use --replace to back up and replace it')
    destination.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    with tempfile.TemporaryDirectory(prefix='.saved-to-practice-install-', dir=destination.parent) as tmp:
        staged = Path(tmp)/'skill'
        shutil.copytree(source, staged, ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        if destination.exists():
            # Outside the discovery directory, so the backup cannot become a second skill.
            backups = Path(os.environ.get('SAVED_TO_PRACTICE_DATA', str(Path.home()/'.local/share/saved-to-practice')))/'backups'
            backups.mkdir(parents=True, exist_ok=True)
            backup = backups/('saved-to-practice-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
            shutil.move(str(destination), str(backup))
        try:
            shutil.move(str(staged), str(destination))
        except OSError:
            if backup is not None:
                shutil.move(str(backup), str(destination))
            raise
    return destination, backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-dir', type=Path, default=Path(os.environ.get('CODEX_HOME', str(Path.home()/'.codex')))/'skills')
    parser.add_argument('--replace', action='store_true')
    args = parser.parse_args()
    try:
        target, backup = install(Path(__file__).resolve().parents[1]/'skills/xhs-favorites-distiller', args.skills_dir/'xhs-favorites-distiller',args.replace)
    except (ValueError,OSError) as error:
        parser.exit(2,f'error: {error}\n')
    print(f'Installed: {target}')
    if backup: print(f'Backup: {backup}')
    if backup is None:
        print('First installation: complete '+str(Path(__file__).resolve().parents[1]/'docs/first-install.md'))


if __name__ == '__main__':
    main()
