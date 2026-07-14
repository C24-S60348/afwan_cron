import json
import secrets
import unicodedata
import uuid
from fractions import Fraction
from functools import wraps
from pathlib import Path

from flask import (
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from . import ar3d
from .db import QUESTION_LEVELS, get_db

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _admin_authorized():
    supplied_key = request.headers.get("X-Admin-Key", "")
    supplied_password = request.headers.get("X-Admin-Password", "")
    expected_key = current_app.config["AR3D_ADMIN_API_KEY"]
    expected_password = current_app.config["AR3D_ADMIN_PASSWORD"]
    return session.get("ar3d_admin") is True or (
        bool(supplied_key)
        and bool(expected_key)
        and secrets.compare_digest(supplied_key, expected_key)
    ) or (
        bool(supplied_password)
        and bool(expected_password)
        and secrets.compare_digest(supplied_password, expected_password)
    )


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if _admin_authorized():
            return view(*args, **kwargs)
        if request.path.startswith("/api/"):
            return jsonify({"error": "Admin authentication required"}), 401
        return redirect(url_for("ar3d.admin_login", next=request.full_path))

    return wrapped


def _save_image(file):
    if not file or not file.filename:
        return None
    safe_name = secure_filename(file.filename)
    extension = safe_name.rsplit(".", 1)[-1].lower() if "." in safe_name else ""
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Image must be PNG, JPG, JPEG, GIF, or WEBP")
    filename = f"{uuid.uuid4().hex}.{extension}"
    file.save(Path(current_app.config["AR3D_UPLOAD_FOLDER"]) / filename)
    return filename


def _delete_image(filename):
    if not filename:
        return
    path = Path(current_app.config["AR3D_UPLOAD_FOLDER"]) / filename
    if path.is_file():
        path.unlink()


def _question_to_dict(row):
    data = dict(row)
    data["accepted_answers"] = json.loads(data["accepted_answers_json"])
    data.pop("accepted_answers_json", None)
    data.pop("options_json", None)
    data.pop("correct_index", None)
    data["is_active"] = bool(data["is_active"])
    data["image_url"] = (
        url_for("ar3d.uploaded_image", filename=data["image_filename"], _external=True)
        if data["image_filename"]
        else None
    )
    return data


def _question_to_public_dict(row):
    data = _question_to_dict(row)
    data.pop("accepted_answers", None)
    data.pop("correct_answer", None)
    return data


def _question_query(where="", params=()):
    return get_db().execute(
        f"""
        SELECT q.*, t.name AS topic_name
        FROM questions q
        JOIN topics t ON t.id = q.topic_id
        {where}
        """,
        params,
    )


def _note_to_dict(row):
    data = dict(row)
    data["points"] = json.loads(data.pop("points_json"))
    data["is_active"] = bool(data["is_active"])
    return data


def _parse_note_payload():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    emoji = str(data.get("emoji", "📚")).strip() or "📚"
    raw_points = data.get("points", [])
    if isinstance(raw_points, str):
        raw_points = raw_points.splitlines()
    points = [str(point).strip() for point in raw_points if str(point).strip()]
    external_url = str(data.get("external_url", "")).strip() or None
    try:
        sort_order = int(data.get("sort_order", 0))
    except (TypeError, ValueError):
        raise ValueError("sort_order must be a number") from None
    is_active = str(data.get("is_active", "1")).lower() not in {
        "0",
        "false",
        "off",
    }
    if not title:
        raise ValueError("Note title is required")
    if not points and not external_url:
        raise ValueError("Add at least one note point or an external URL")
    if external_url and not external_url.startswith(("https://", "http://")):
        raise ValueError("External URL must start with http:// or https://")
    return emoji, title, points, external_url, sort_order, is_active


def _parse_question_payload():
    data = request.get_json(silent=True) if request.is_json else request.form
    data = data or {}
    try:
        topic_id = int(data.get("topic_id", ""))
        prompt = str(data.get("prompt", "")).strip()
        raw_answers = data.get("accepted_answers", [])
        if isinstance(raw_answers, str):
            try:
                decoded = json.loads(raw_answers)
                raw_answers = (
                    decoded if isinstance(decoded, list) else raw_answers.splitlines()
                )
            except json.JSONDecodeError:
                raw_answers = raw_answers.splitlines()
        accepted_answers = [
            str(answer).strip() for answer in raw_answers if str(answer).strip()
        ]
        is_active = str(data.get("is_active", "1")).lower() not in {"0", "false", "off"}
    except (TypeError, ValueError):
        raise ValueError("topic_id must be a number") from None

    if not prompt:
        raise ValueError("Question text is required")
    if not accepted_answers:
        raise ValueError("At least one accepted answer is required")
    level = str(data.get("level", "") or "").strip().upper() or None
    if level and level not in QUESTION_LEVELS:
        raise ValueError(
            "level must be one of: " + ", ".join(QUESTION_LEVELS)
        )
    topic = get_db().execute("SELECT id FROM topics WHERE id = ?", (topic_id,)).fetchone()
    if topic is None:
        raise ValueError("Unknown topic_id")
    return topic_id, prompt, accepted_answers, is_active, level


def _normalized_text(value):
    normalized = unicodedata.normalize("NFKC", value)
    return " ".join(normalized.casefold().strip().split())


def _as_number(value):
    compact = _normalized_text(value).replace(" ", "")
    try:
        return Fraction(compact)
    except (ValueError, ZeroDivisionError):
        return None


def answers_match(submitted, accepted):
    submitted_number = _as_number(submitted)
    accepted_number = _as_number(accepted)
    if submitted_number is not None and accepted_number is not None:
        return submitted_number == accepted_number
    return _normalized_text(submitted) == _normalized_text(accepted)


@ar3d.get("/api/ar3d/health")
def health():
    return jsonify({"status": "ok", "service": "ar3d"})


@ar3d.get("/api/ar3d/topics")
def list_topics():
    rows = get_db().execute(
        "SELECT id, name, description FROM topics WHERE is_active = 1 ORDER BY name"
    ).fetchall()
    return jsonify({"topics": [dict(row) for row in rows]})


@ar3d.get("/api/ar3d/questions")
def list_questions():
    topic = request.args.get("topic", "").strip()
    level = request.args.get("level", "").strip().upper()
    where = "WHERE q.is_active = 1 AND t.is_active = 1"
    params = []
    if topic:
        where += " AND t.name = ?"
        params.append(topic)
    if level:
        where += " AND q.level = ?"
        params.append(level)
    order = " ORDER BY q.id" if topic else " ORDER BY t.name, q.id"
    rows = _question_query(where + order, tuple(params)).fetchall()
    return jsonify({"questions": [_question_to_public_dict(row) for row in rows]})


@ar3d.get("/api/ar3d/questions/<int:question_id>")
def get_question(question_id):
    row = _question_query(
        "WHERE q.id = ? AND q.is_active = 1", (question_id,)
    ).fetchone()
    if row is None:
        return jsonify({"error": "Question not found"}), 404
    return jsonify({"question": _question_to_public_dict(row)})


@ar3d.get("/api/ar3d/notes")
def list_notes():
    rows = get_db().execute(
        """
        SELECT * FROM notes
        WHERE is_active = 1
        ORDER BY sort_order, id
        """
    ).fetchall()
    return jsonify({"notes": [_note_to_dict(row) for row in rows]})


@ar3d.post("/api/ar3d/admin/login")
def api_admin_login():
    data = request.get_json(silent=True) or {}
    supplied = str(data.get("password", ""))
    expected = current_app.config["AR3D_ADMIN_PASSWORD"]
    if supplied and secrets.compare_digest(supplied, expected):
        return jsonify({"authenticated": True})
    return jsonify({"error": "Incorrect lecturer password"}), 401


@ar3d.get("/api/ar3d/admin/questions")
@admin_required
def api_admin_questions():
    rows = _question_query("ORDER BY q.is_active DESC, q.id DESC").fetchall()
    return jsonify({"questions": [_question_to_dict(row) for row in rows]})


@ar3d.get("/api/ar3d/admin/notes")
@admin_required
def api_admin_notes():
    rows = get_db().execute(
        "SELECT * FROM notes ORDER BY is_active DESC, sort_order, id"
    ).fetchall()
    return jsonify({"notes": [_note_to_dict(row) for row in rows]})


@ar3d.post("/api/ar3d/admin/notes")
@admin_required
def api_create_note():
    try:
        emoji, title, points, external_url, sort_order, is_active = (
            _parse_note_payload()
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO notes
            (emoji, title, points_json, external_url, sort_order, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            emoji,
            title,
            json.dumps(points),
            external_url,
            sort_order,
            int(is_active),
        ),
    )
    db.commit()
    row = db.execute("SELECT * FROM notes WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify({"note": _note_to_dict(row)}), 201


@ar3d.route("/api/ar3d/admin/notes/<int:note_id>", methods=["PUT", "PATCH"])
@admin_required
def api_update_note(note_id):
    db = get_db()
    if db.execute("SELECT id FROM notes WHERE id = ?", (note_id,)).fetchone() is None:
        return jsonify({"error": "Note not found"}), 404
    try:
        emoji, title, points, external_url, sort_order, is_active = (
            _parse_note_payload()
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    db.execute(
        """
        UPDATE notes SET emoji = ?, title = ?, points_json = ?,
            external_url = ?, sort_order = ?, is_active = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            emoji,
            title,
            json.dumps(points),
            external_url,
            sort_order,
            int(is_active),
            note_id,
        ),
    )
    db.commit()
    row = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    return jsonify({"note": _note_to_dict(row)})


@ar3d.delete("/api/ar3d/admin/notes/<int:note_id>")
@admin_required
def api_delete_note(note_id):
    db = get_db()
    existing = db.execute(
        "SELECT id FROM notes WHERE id = ?", (note_id,)
    ).fetchone()
    if existing is None:
        return jsonify({"error": "Note not found"}), 404
    db.execute(
        "UPDATE notes SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (note_id,),
    )
    db.commit()
    return "", 204


@ar3d.get("/api/ar3d/admin/responses")
@admin_required
def api_admin_responses():
    limit = min(max(request.args.get("limit", 200, type=int), 1), 1000)
    attempts = get_db().execute(
        """
        SELECT id, question_id, player_name, topic_name, question_text,
               correct_answer, selected_answer, is_correct,
               detected_image_name, device_id, answered_at
        FROM answer_attempts
        ORDER BY answered_at DESC, id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return jsonify(
        {
            "responses": [
                {**dict(attempt), "is_correct": bool(attempt["is_correct"])}
                for attempt in attempts
            ]
        }
    )


@ar3d.post("/api/ar3d/answers")
def record_answer():
    data = request.get_json(silent=True) or {}
    player_name = str(data.get("player_name", "")).strip()
    submitted_answer = str(data.get("answer", "")).strip()
    try:
        question_id = int(data.get("question_id", ""))
    except (TypeError, ValueError):
        return jsonify({"error": "question_id must be a number"}), 400

    if not player_name:
        return jsonify({"error": "player_name is required"}), 400
    if not submitted_answer:
        return jsonify({"error": "answer is required"}), 400

    question = _question_query(
        "WHERE q.id = ? AND q.is_active = 1", (question_id,)
    ).fetchone()
    if question is None:
        return jsonify({"error": "Question not found"}), 404

    accepted_answers = json.loads(question["accepted_answers_json"])
    correct_answer = question["correct_answer"]
    is_correct = any(
        answers_match(submitted_answer, accepted) for accepted in accepted_answers
    )
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO answer_attempts (
            question_id, player_name, topic_name, question_text,
            correct_answer, selected_answer, is_correct,
            detected_image_name, device_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            question_id,
            player_name,
            question["topic_name"],
            question["prompt"],
            correct_answer,
            submitted_answer,
            int(is_correct),
            str(data.get("detected_image_name", "")).strip() or None,
            str(data.get("device_id", "")).strip() or None,
        ),
    )
    db.commit()
    return (
        jsonify(
            {
                "attempt_id": cursor.lastrowid,
                "is_correct": is_correct,
                "selected_answer": submitted_answer,
                "correct_answer": correct_answer,
            }
        ),
        201,
    )


@ar3d.post("/api/ar3d/admin/questions")
@admin_required
def api_create_question():
    try:
        topic_id, prompt, accepted_answers, is_active, level = (
            _parse_question_payload()
        )
        image_filename = _save_image(request.files.get("image"))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    db = get_db()
    question_columns = {
        row["name"] for row in db.execute("PRAGMA table_info(questions)").fetchall()
    }
    if {"options_json", "correct_index"} <= question_columns:
        cursor = db.execute(
            """
            INSERT INTO questions
                (topic_id, prompt, level, image_filename, options_json,
                 correct_index, correct_answer, accepted_answers_json, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                topic_id,
                prompt,
                level,
                image_filename,
                json.dumps(accepted_answers),
                0,
                accepted_answers[0],
                json.dumps(accepted_answers),
                int(is_active),
            ),
        )
    else:
        cursor = db.execute(
            """
            INSERT INTO questions
                (topic_id, prompt, level, image_filename, correct_answer,
                 accepted_answers_json, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                topic_id,
                prompt,
                level,
                image_filename,
                accepted_answers[0],
                json.dumps(accepted_answers),
                int(is_active),
            ),
        )
    db.commit()
    row = _question_query("WHERE q.id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify({"question": _question_to_dict(row)}), 201


@ar3d.route("/api/ar3d/admin/questions/<int:question_id>", methods=["PUT", "PATCH"])
@admin_required
def api_update_question(question_id):
    existing = get_db().execute(
        "SELECT * FROM questions WHERE id = ?", (question_id,)
    ).fetchone()
    if existing is None:
        return jsonify({"error": "Question not found"}), 404
    try:
        topic_id, prompt, accepted_answers, is_active, level = (
            _parse_question_payload()
        )
        new_image = _save_image(request.files.get("image"))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    if level is None and "level" in existing.keys():
        level = existing["level"]
    image_filename = new_image or existing["image_filename"]
    if new_image:
        _delete_image(existing["image_filename"])
    db = get_db()
    db.execute(
        """
        UPDATE questions SET topic_id = ?, prompt = ?, level = ?,
            image_filename = ?, correct_answer = ?, accepted_answers_json = ?,
            is_active = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            topic_id,
            prompt,
            level,
            image_filename,
            accepted_answers[0],
            json.dumps(accepted_answers),
            int(is_active),
            question_id,
        ),
    )
    db.commit()
    row = _question_query("WHERE q.id = ?", (question_id,)).fetchone()
    return jsonify({"question": _question_to_dict(row)})


@ar3d.delete("/api/ar3d/admin/questions/<int:question_id>")
@admin_required
def api_delete_question(question_id):
    db = get_db()
    existing = db.execute("SELECT id FROM questions WHERE id = ?", (question_id,)).fetchone()
    if existing is None:
        return jsonify({"error": "Question not found"}), 404
    db.execute(
        "UPDATE questions SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (question_id,),
    )
    db.commit()
    return "", 204


@ar3d.get("/uploads/ar3d/<path:filename>")
def uploaded_image(filename):
    return send_from_directory(current_app.config["AR3D_UPLOAD_FOLDER"], filename)


@ar3d.route("/admin/ar3d/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        supplied = request.form.get("password", "")
        expected = current_app.config["AR3D_ADMIN_PASSWORD"]
        if supplied and secrets.compare_digest(supplied, expected):
            session["ar3d_admin"] = True
            return redirect(url_for("ar3d.admin_dashboard"))
        flash("Incorrect password.", "error")
    return render_template("ar3d/login.html")


@ar3d.post("/admin/ar3d/logout")
def admin_logout():
    session.pop("ar3d_admin", None)
    return redirect(url_for("ar3d.admin_login"))


@ar3d.get("/admin/ar3d")
@admin_required
def admin_dashboard():
    questions = _question_query("ORDER BY q.is_active DESC, q.id DESC").fetchall()
    stats = get_db().execute(
        """
        SELECT COUNT(*) AS total,
               COALESCE(SUM(is_correct), 0) AS correct,
               COUNT(DISTINCT player_name) AS players
        FROM answer_attempts
        """
    ).fetchone()
    return render_template(
        "ar3d/dashboard.html",
        questions=[_question_to_dict(row) for row in questions],
        stats=stats,
    )


def _question_form_context(question=None):
    topics = get_db().execute(
        "SELECT id, name FROM topics WHERE is_active = 1 ORDER BY name"
    ).fetchall()
    return {"topics": topics, "question": question}


@ar3d.route("/admin/ar3d/questions/new", methods=["GET", "POST"])
@admin_required
def admin_new_question():
    if request.method == "POST":
        response, status = api_create_question()
        if status == 201:
            flash("Question created.", "success")
            return redirect(url_for("ar3d.admin_dashboard"))
        flash(response.get_json()["error"], "error")
    return render_template("ar3d/question_form.html", **_question_form_context())


@ar3d.route("/admin/ar3d/questions/<int:question_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_question(question_id):
    row = _question_query("WHERE q.id = ?", (question_id,)).fetchone()
    if row is None:
        abort(404)
    if request.method == "POST":
        response = api_update_question(question_id)
        if not isinstance(response, tuple):
            flash("Question updated.", "success")
            return redirect(url_for("ar3d.admin_dashboard"))
        flash(response[0].get_json()["error"], "error")
    return render_template(
        "ar3d/question_form.html",
        **_question_form_context(_question_to_dict(row)),
    )


@ar3d.post("/admin/ar3d/questions/<int:question_id>/archive")
@admin_required
def admin_archive_question(question_id):
    api_delete_question(question_id)
    flash("Question archived.", "success")
    return redirect(url_for("ar3d.admin_dashboard"))


@ar3d.get("/admin/ar3d/responses")
@admin_required
def admin_responses():
    attempts = get_db().execute(
        "SELECT * FROM answer_attempts ORDER BY answered_at DESC, id DESC"
    ).fetchall()
    return render_template("ar3d/responses.html", attempts=attempts)
