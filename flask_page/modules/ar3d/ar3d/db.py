import json
import sqlite3
from pathlib import Path

import click
from flask import current_app, g

QUESTION_LEVELS = ("ASAS", "SEDERHANA", "APLIKASI", "ANALISIS", "CABARAN")


def get_db():
    if "ar3d_db" not in g:
        g.ar3d_db = sqlite3.connect(
            current_app.config["AR3D_DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.ar3d_db.row_factory = sqlite3.Row
        g.ar3d_db.execute("PRAGMA foreign_keys = ON")
    return g.ar3d_db


def close_db(_error=None):
    db = g.pop("ar3d_db", None)
    if db is not None:
        db.close()


def init_db():
    schema_path = Path(__file__).with_name("schema.sql")
    db = get_db()
    db.executescript(schema_path.read_text(encoding="utf-8"))
    _migrate_questions_to_typed_answers(db)
    _migrate_questions_add_level(db)
    db.commit()


def _migrate_questions_to_typed_answers(db):
    columns = {
        row["name"] for row in db.execute("PRAGMA table_info(questions)").fetchall()
    }
    if "correct_answer" not in columns:
        db.execute("ALTER TABLE questions ADD COLUMN correct_answer TEXT")
    if "accepted_answers_json" not in columns:
        db.execute("ALTER TABLE questions ADD COLUMN accepted_answers_json TEXT")
    if "options_json" not in columns or "correct_index" not in columns:
        return

    legacy_rows = db.execute(
        """
        SELECT id, options_json, correct_index
        FROM questions
        WHERE correct_answer IS NULL OR accepted_answers_json IS NULL
        """
    ).fetchall()
    for row in legacy_rows:
        options = json.loads(row["options_json"]) if row["options_json"] else []
        index = row["correct_index"] or 0
        answer = str(options[index]).strip() if 0 <= index < len(options) else ""
        db.execute(
            """
            UPDATE questions
            SET correct_answer = ?, accepted_answers_json = ?
            WHERE id = ?
            """,
            (answer, json.dumps([answer] if answer else []), row["id"]),
        )


def _migrate_questions_add_level(db):
    columns = {
        row["name"] for row in db.execute("PRAGMA table_info(questions)").fetchall()
    }
    if "level" not in columns:
        db.execute("ALTER TABLE questions ADD COLUMN level TEXT")

    # Backfill: prompts saved as "[LEVEL] question" get their level column set
    # and the prefix stripped from the prompt.
    rows = db.execute(
        "SELECT id, prompt FROM questions WHERE level IS NULL AND prompt LIKE '[%'"
    ).fetchall()
    for row in rows:
        prompt = row["prompt"] or ""
        for level in QUESTION_LEVELS:
            prefix = f"[{level}]"
            if prompt.startswith(prefix):
                db.execute(
                    "UPDATE questions SET level = ?, prompt = ? WHERE id = ?",
                    (level, prompt[len(prefix):].strip(), row["id"]),
                )
                break


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized the AR3D database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    with app.app_context():
        init_db()
