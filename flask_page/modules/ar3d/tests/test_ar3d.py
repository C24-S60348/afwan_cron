import io
import tempfile
import unittest
from pathlib import Path

from app import create_app
from ar3d.db import get_db, init_db


class Ar3dApiTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-secret",
                "AR3D_DATABASE": str(root / "test.sqlite3"),
                "AR3D_UPLOAD_FOLDER": str(root / "uploads"),
                "AR3D_ADMIN_PASSWORD": "lecturer-password",
                "AR3D_ADMIN_API_KEY": "test-api-key",
            }
        )
        self.client = self.app.test_client()
        self.headers = {"X-Admin-Key": "test-api-key"}

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_question(self, include_image=False):
        data = {
            "topic_id": "1",
            "prompt": "Write one half as a number.",
            "accepted_answers": '["0.5"]',
            "is_active": "1",
        }
        if include_image:
            data["image"] = (io.BytesIO(b"fake-image"), "question.png")
        return self.client.post(
            "/api/ar3d/admin/questions",
            data=data,
            headers=self.headers,
            content_type="multipart/form-data",
        )

    def test_health_and_topics(self):
        self.assertEqual(self.client.get("/api/ar3d/health").status_code, 200)
        response = self.client.get("/api/ar3d/topics")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()["topics"]), 4)
        asset_response = self.client.get("/ar3d-static/admin.css")
        self.assertEqual(asset_response.status_code, 200)
        asset_response.close()

    def test_database_initialization_is_idempotent(self):
        with self.app.app_context():
            before = get_db().execute(
                "SELECT seq FROM sqlite_sequence WHERE name = 'topics'"
            ).fetchone()["seq"]
            init_db()
            after = get_db().execute(
                "SELECT seq FROM sqlite_sequence WHERE name = 'topics'"
            ).fetchone()["seq"]
        self.assertEqual(after, before)

    def test_admin_write_requires_authentication(self):
        response = self.client.post("/api/ar3d/admin/questions", json={})
        self.assertEqual(response.status_code, 401)

    def test_mobile_admin_login_and_listing_apis(self):
        self._create_question()
        login = self.client.post(
            "/api/ar3d/admin/login",
            json={"password": "lecturer-password"},
        )
        self.assertEqual(login.status_code, 200)

        password_headers = {"X-Admin-Password": "lecturer-password"}
        questions = self.client.get(
            "/api/ar3d/admin/questions",
            headers=password_headers,
        )
        self.assertEqual(questions.status_code, 200)
        self.assertEqual(
            questions.get_json()["questions"][0]["accepted_answers"],
            ["0.5"],
        )
        responses = self.client.get(
            "/api/ar3d/admin/responses",
            headers=password_headers,
        )
        self.assertEqual(responses.status_code, 200)
        self.assertEqual(responses.get_json()["responses"], [])

    def test_question_crud_and_image_upload(self):
        created = self._create_question(include_image=True)
        self.assertEqual(created.status_code, 201)
        question = created.get_json()["question"]
        self.assertIsNotNone(question["image_url"])

        listed = self.client.get("/api/ar3d/questions").get_json()["questions"]
        self.assertEqual(len(listed), 1)
        self.assertNotIn("accepted_answers", listed[0])
        self.assertNotIn("correct_answer", listed[0])

        deleted = self.client.delete(
            f"/api/ar3d/admin/questions/{question['id']}", headers=self.headers
        )
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(
            self.client.get("/api/ar3d/questions").get_json()["questions"], []
        )

    def test_note_crud_and_seeded_drive_link(self):
        public_notes = self.client.get("/api/ar3d/notes")
        self.assertEqual(public_notes.status_code, 200)
        seeded = public_notes.get_json()["notes"][0]
        self.assertIn("drive.google.com", seeded["external_url"])

        created = self.client.post(
            "/api/ar3d/admin/notes",
            headers=self.headers,
            json={
                "emoji": "🧮",
                "title": "Fractions",
                "points": ["One half equals 0.5.", "Two quarters equal one half."],
                "external_url": "https://example.com/fractions",
                "sort_order": 2,
                "is_active": True,
            },
        )
        self.assertEqual(created.status_code, 201)
        note = created.get_json()["note"]
        self.assertEqual(note["points"][0], "One half equals 0.5.")

        updated = self.client.put(
            f"/api/ar3d/admin/notes/{note['id']}",
            headers=self.headers,
            json={
                "emoji": "🔢",
                "title": "Updated fractions",
                "points": ["1/2 = 0.5"],
                "external_url": "",
                "sort_order": 1,
                "is_active": True,
            },
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.get_json()["note"]["title"], "Updated fractions")

        archived = self.client.delete(
            f"/api/ar3d/admin/notes/{note['id']}", headers=self.headers
        )
        self.assertEqual(archived.status_code, 204)
        titles = [
            item["title"]
            for item in self.client.get("/api/ar3d/notes").get_json()["notes"]
        ]
        self.assertNotIn("Updated fractions", titles)

    def test_answer_submission_accepts_case_insensitive_text(self):
        question = self.client.post(
            "/api/ar3d/admin/questions",
            data={
                "topic_id": "1",
                "prompt": "Name the city.",
                "accepted_answers": "Melaka",
                "is_active": "1",
            },
            headers=self.headers,
        ).get_json()["question"]
        response = self.client.post(
            "/api/ar3d/answers",
            json={
                "player_name": "Aina",
                "question_id": question["id"],
                "answer": "  meLAKa  ",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.get_json()["is_correct"])

    def test_answer_submission_accepts_equivalent_fraction_and_decimal(self):
        question = self._create_question().get_json()["question"]
        for answer in ("0.5", "0.50", "1/2"):
            response = self.client.post(
                "/api/ar3d/answers",
                json={
                    "player_name": "Aina",
                    "question_id": question["id"],
                    "answer": answer,
                    "detected_image_name": "afamosa",
                    "device_id": "phone-1",
                },
            )
            self.assertEqual(response.status_code, 201)
            result = response.get_json()
            self.assertTrue(result["is_correct"])
            self.assertEqual(result["correct_answer"], "0.5")

        with self.client.session_transaction() as session:
            session["ar3d_admin"] = True
        page = self.client.get("/admin/ar3d/responses")
        self.assertIn(b"Aina", page.data)
        self.assertIn(b"Write one half as a number.", page.data)

    def test_lecturer_login(self):
        response = self.client.post(
            "/admin/ar3d/login",
            data={"password": "lecturer-password"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Question Management", response.data)

    def test_lecturer_can_create_question_from_form(self):
        with self.client.session_transaction() as session:
            session["ar3d_admin"] = True
        response = self.client.post(
            "/admin/ar3d/questions/new",
            data={
                "topic_id": "1",
                "prompt": "Write one half.",
                "accepted_answers": "0.5\none half",
                "is_active": "1",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Question created.", response.data)


if __name__ == "__main__":
    unittest.main()
