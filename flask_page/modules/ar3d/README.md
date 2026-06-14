# i.-GB AR3D Flask API

This server stores lecturer-managed questions, optional question images, and
every learner answer. The Flask controller is the `ar3d` Blueprint.

## Run locally

```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export FLASK_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
export AR3D_ADMIN_PASSWORD="choose-a-strong-password"
export AR3D_ADMIN_API_KEY="choose-a-long-random-api-key"

flask --app app run --host 0.0.0.0 --port 5000
```

Open `http://127.0.0.1:5000/admin/ar3d` for the lecturer interface.
The SQLite database is created automatically in `server/instance/`.

For an Android emulator, the host machine is normally available at
`http://10.0.2.2:5000`. A physical phone must use the computer's LAN IP address.

Run the Flutter app against the server with:

```bash
flutter run \
  --dart-define=AR3D_API_BASE_URL=http://YOUR_COMPUTER_IP:5000
```

Use HTTPS for deployed builds. If no URL is configured or the server cannot be
reached, the scanner falls back to the questions bundled inside the app.
Android debug builds allow local HTTP traffic; release builds do not enable
that exception.

## Public mobile API

### List topics

`GET /api/ar3d/topics`

### List active questions

`GET /api/ar3d/questions`

Filter by exact topic name:

`GET /api/ar3d/questions?topic=Maths%20for%20Primary%20Students`

### List active game notes

`GET /api/ar3d/notes`

Each note contains an emoji, title, bullet points, optional external URL, and
display order.

### Submit an answer

`POST /api/ar3d/answers`

```json
{
  "player_name": "Aina",
  "question_id": 12,
  "answer": "1/2",
  "detected_image_name": "afamosa",
  "device_id": "optional-installation-id"
}
```

The server calculates correctness. Text matching ignores letter case and extra
spaces. Numeric equivalents such as `0.5`, `0.50`, and `1/2` match exactly. It
stores snapshots of the topic, question, submitted answer, and correct answer,
so historical reports remain accurate even after a lecturer edits the question.

## Admin API

The in-app lecturer area first verifies the password:

- `POST /api/ar3d/admin/login`

It then sends the password in the `X-Admin-Password` header for the current
screen session. Server integrations may instead use the configured
`X-Admin-Key`.

- `GET /api/ar3d/admin/questions`
- `GET /api/ar3d/admin/notes`
- `GET /api/ar3d/admin/responses`
- `POST /api/ar3d/admin/questions`
- `POST /api/ar3d/admin/notes`
- `PUT /api/ar3d/admin/questions/<id>`
- `PUT /api/ar3d/admin/notes/<id>`
- `PATCH /api/ar3d/admin/questions/<id>`
- `PATCH /api/ar3d/admin/notes/<id>`
- `DELETE /api/ar3d/admin/questions/<id>` (archives the question)
- `DELETE /api/ar3d/admin/notes/<id>` (archives the note)

Create and update requests accept `multipart/form-data`:

- `topic_id`: integer
- `prompt`: question text
- `accepted_answers`: JSON array or one accepted answer per line; the first is
  the canonical answer shown in reports
- `is_active`: `1` or `0`
- `image`: optional PNG, JPG, JPEG, GIF, or WEBP file, maximum 5 MB

## In-app lecturer area

Run Flutter with `AR3D_API_BASE_URL`, then select **Lecturer Admin** on the home
screen. The lecturer can:

- log in with `AR3D_ADMIN_PASSWORD`
- list active and archived questions
- create or edit a question and its accepted typed answers
- archive a question
- view learner names, submitted answers, correct answers, and results

Question image upload remains available in the browser lecturer page.

## Tests

```bash
cd server
python3 -m unittest discover -s tests -v
```
