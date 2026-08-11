import json
import sqlite3
from pathlib import Path

import click
from flask import current_app, g

QUESTION_LEVELS = (
    # Secondary-school difficulty buckets.
    "ASAS",
    "SEDERHANA",
    "APLIKASI",
    "ANALISIS",
    "CABARAN",
    # Primary-school card colours, from "primary school questions.docx".
    "HIJAU",
    "BIRU",
    "UNGU",
    "EMAS",
)

# The 14 AR checkpoints on the printed 100-square board, keyed by square number.
# Each of the 7 landmarks appears twice, once early and once late, so the square
# number — not the landmark — is what decides difficulty. The tier follows the
# card ranges in the primary question document: 1-25 HIJAU, 26-50 BIRU,
# 51-75 UNGU, 76-100 EMAS.
CHECKPOINTS = {
    8: {"place": "muzium-samudera", "name": "Muzium Samudera", "tier": "HIJAU"},
    18: {"place": "menara-taming-sari", "name": "Menara Taming Sari", "tier": "HIJAU"},
    25: {"place": "pantai-klebang", "name": "Pantai Klebang", "tier": "HIJAU"},
    35: {"place": "masjid-cina", "name": "Masjid Cina Melaka", "tier": "BIRU"},
    39: {"place": "kota-a-famosa", "name": "Kota A'Famosa", "tier": "BIRU"},
    49: {"place": "masjid-selat", "name": "Masjid Selat Melaka", "tier": "BIRU"},
    55: {"place": "menara-taming-sari", "name": "Menara Taming Sari", "tier": "UNGU"},
    67: {"place": "kota-a-famosa", "name": "Kota A'Famosa", "tier": "UNGU"},
    71: {"place": "stadium-hang-jebat", "name": "Stadium Hang Jebat", "tier": "UNGU"},
    79: {"place": "muzium-samudera", "name": "Muzium Samudera", "tier": "EMAS"},
    81: {"place": "masjid-selat", "name": "Masjid Selat Melaka", "tier": "EMAS"},
    85: {"place": "masjid-cina", "name": "Masjid Cina Melaka", "tier": "EMAS"},
    93: {"place": "pantai-klebang", "name": "Pantai Klebang", "tier": "EMAS"},
    98: {"place": "stadium-hang-jebat", "name": "Stadium Hang Jebat", "tier": "EMAS"},
}


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
    _migrate_questions_add_place_and_choices(db)
    _migrate_questions_add_checkpoint(db)
    _migrate_notes_add_image(db)
    _migrate_survey_to_tam(db)
    db.commit()


def _migrate_notes_add_image(db):
    columns = {row["name"] for row in db.execute("PRAGMA table_info(notes)").fetchall()}
    if "image_filename" not in columns:
        db.execute("ALTER TABLE notes ADD COLUMN image_filename TEXT")


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


def _migrate_questions_add_place_and_choices(db):
    columns = {
        row["name"] for row in db.execute("PRAGMA table_info(questions)").fetchall()
    }
    if "place" not in columns:
        db.execute("ALTER TABLE questions ADD COLUMN place TEXT")
    # Deliberately not options_json: legacy databases reused that column to hold
    # accepted answers, so multiple-choice options get their own column.
    if "choices_json" not in columns:
        db.execute(
            "ALTER TABLE questions ADD COLUMN choices_json TEXT NOT NULL DEFAULT '[]'"
        )
    db.execute("CREATE INDEX IF NOT EXISTS idx_questions_place ON questions (place)")


def _migrate_questions_add_checkpoint(db):
    columns = {
        row["name"] for row in db.execute("PRAGMA table_info(questions)").fetchall()
    }
    if "checkpoint" not in columns:
        db.execute("ALTER TABLE questions ADD COLUMN checkpoint INTEGER")
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_questions_checkpoint ON questions (checkpoint)"
    )


# The Soal Selidik follows "BORANG SOAL SELIDIK IGB": four TAM constructs asked
# once about the printed board (B) and again about the app (C). Every item is
# scored 1-4 — Sangat tidak setuju, Tidak setuju, Setuju, Sangat setuju.
#
# The document also asks for "Pengalaman mengajar", which i-GB deliberately
# leaves out: its respondents are mostly students, for whom it means nothing.
SURVEY_ITEM_CODES = (
    "B-PEOU-1", "B-PEOU-2", "B-PEOU-3", "B-PEOU-4",
    "B-PU-1", "B-PU-2", "B-PU-3", "B-PU-4",
    "B-ATU-1", "B-ATU-2", "B-ATU-3",
    "B-BI-1", "B-BI-2", "B-BI-3",
    "C-PEOU-1", "C-PEOU-2", "C-PEOU-3", "C-PEOU-4",
    "C-PU-1", "C-PU-2", "C-PU-3", "C-PU-4",
    "C-ATU-1", "C-ATU-2", "C-ATU-3",
    "C-BI-1", "C-BI-2", "C-BI-3",
)

SURVEY_GENDERS = ("Lelaki", "Perempuan")
SURVEY_AGE_GROUPS = ("18 – 23 tahun", "24 tahun ke atas")
SURVEY_STATUSES = ("Pensyarah", "Pentadbir", "Pelajar")


def _migrate_survey_to_tam(db):
    """Add the columns the TAM questionnaire needs.

    The original three opinion columns (easiness, ar_experience, question_fit)
    are NOT NULL and hold real answers from earlier respondents, so they stay
    where they are; new rows simply write an empty string into them.
    """
    columns = {
        row["name"] for row in db.execute("PRAGMA table_info(survey_responses)").fetchall()
    }
    if "gender" not in columns:
        db.execute("ALTER TABLE survey_responses ADD COLUMN gender TEXT")
    if "ratings_json" not in columns:
        db.execute("ALTER TABLE survey_responses ADD COLUMN ratings_json TEXT")


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized the AR3D database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    with app.app_context():
        init_db()
