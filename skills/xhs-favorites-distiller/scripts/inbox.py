#!/usr/bin/env python3
"""Local saved-reading inbox. No network, scheduler, or semantic decisions."""
import argparse
import json
import os
from pathlib import Path
import sqlite3


def connect(root):
    root = Path(root).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(root / 'inbox.sqlite3', timeout=5)
    db.row_factory = sqlite3.Row
    db.execute('''CREATE TABLE IF NOT EXISTS notes (
        source TEXT NOT NULL, id TEXT NOT NULL, title TEXT NOT NULL,
        url TEXT NOT NULL, content TEXT NOT NULL, complete INTEGER NOT NULL,
        revision INTEGER NOT NULL, assessed_revision INTEGER,
        decision TEXT, reason TEXT,
        PRIMARY KEY(source,id))''')
    return db


def validate_batch(payload):
    if not isinstance(payload, list):
        raise ValueError('Input must be a JSON array of notes')
    rows, seen = [], set()
    for note in payload:
        if not isinstance(note, dict):
            raise ValueError('Every note must be an object')
        for key in ('source', 'id', 'title', 'url', 'content'):
            if not isinstance(note.get(key), str):
                raise ValueError(f'{key} must be a string')
        if not note['source'].strip() or not note['id'].strip():
            raise ValueError('source and id must be nonempty')
        if type(note.get('complete')) is not bool:
            raise ValueError('complete must explicitly be true or false')
        if note['complete'] and not note['content'].strip():
            raise ValueError('A complete note must contain readable content')
        identity = (note['source'], note['id'])
        if identity in seen:
            raise ValueError('Duplicate source/id inside a batch; merge it before importing')
        seen.add(identity)
        rows.append(tuple(note[k] for k in ('source', 'id', 'title', 'url', 'content', 'complete')))
    return rows


def ingest(db, payload):
    rows = validate_batch(payload)
    inserted = updated = unchanged = 0
    with db:
        for row in rows:
            old = db.execute('SELECT * FROM notes WHERE source=? AND id=?', row[:2]).fetchone()
            if old is None:
                db.execute('INSERT INTO notes(source,id,title,url,content,complete,revision) VALUES(?,?,?,?,?,?,1)', row)
                inserted += 1
            elif tuple(old[k] for k in ('title','url','content','complete')) == row[2:]:
                unchanged += 1
            else:
                db.execute('UPDATE notes SET title=?,url=?,content=?,complete=?,revision=revision+1 WHERE source=? AND id=?', row[2:] + row[:2])
                updated += 1
    return dict(inserted=inserted, updated=updated, unchanged=unchanged)


def pending(db, limit):
    if limit < 1:
        raise ValueError('limit must be positive')
    return [dict(x) for x in db.execute('''SELECT source,id,title,url,content,complete,revision
        FROM notes WHERE assessed_revision IS NULL OR assessed_revision != revision
        ORDER BY rowid LIMIT ?''', (limit,))]


def assess(db, source, note_id, revision, decision, reason):
    if decision not in ('skip', 'candidate', 'needs-evidence') or not reason.strip():
        raise ValueError('Provide a supported decision and a nonempty reason')
    with db:
        cursor = db.execute('''UPDATE notes SET assessed_revision=revision, decision=?,reason=?
            WHERE source=? AND id=? AND revision=?''', (decision,reason,source,note_id,revision))
        if cursor.rowcount != 1:
            raise ValueError('Note missing or revised; read its current content before deciding')
    return dict(recorded=True, decision=decision)


def get_note(db, source, note_id):
    row = db.execute('SELECT * FROM notes WHERE source=? AND id=?', (source,note_id)).fetchone()
    if row is None:
        raise ValueError('Note not found')
    return dict(row)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', default=os.environ.get('SAVED_TO_PRACTICE_DATA', str(Path.home()/'.local/share/saved-to-practice')))
    commands = parser.add_subparsers(dest='command', required=True)
    imp = commands.add_parser('ingest'); imp.add_argument('file', type=Path)
    ls = commands.add_parser('pending'); ls.add_argument('--limit', type=int, default=5)
    get = commands.add_parser('get'); get.add_argument('source'); get.add_argument('id')
    dec = commands.add_parser('assess')
    dec.add_argument('source'); dec.add_argument('id'); dec.add_argument('--revision', required=True, type=int)
    dec.add_argument('--decision', required=True, choices=['skip','candidate','needs-evidence']); dec.add_argument('--reason', required=True)
    args = parser.parse_args()
    try:
        # Validate imports before creating or changing the inbox.
        if args.command == 'ingest':
            payload = json.loads(args.file.read_text(encoding='utf-8'))
            validate_batch(payload)
        with connect(args.data_dir) as db:
            if args.command == 'ingest': result = ingest(db, payload)
            elif args.command == 'pending': result = pending(db, args.limit)
            elif args.command == 'get': result = get_note(db,args.source,args.id)
            else: result = assess(db,args.source,args.id,args.revision,args.decision,args.reason)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, sqlite3.Error) as error:
        parser.exit(2, f'error: {error}\n')


if __name__ == '__main__':
    main()
