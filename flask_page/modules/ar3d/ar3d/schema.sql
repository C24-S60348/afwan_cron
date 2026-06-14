CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    image_filename TEXT,
    correct_answer TEXT NOT NULL,
    accepted_answers_json TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics (id)
);

CREATE TABLE IF NOT EXISTS answer_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER,
    player_name TEXT NOT NULL,
    topic_name TEXT NOT NULL,
    question_text TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    selected_answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL,
    detected_image_name TEXT,
    device_id TEXT,
    answered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emoji TEXT NOT NULL DEFAULT '📚',
    title TEXT NOT NULL,
    points_json TEXT NOT NULL DEFAULT '[]',
    external_url TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions (topic_id);
CREATE INDEX IF NOT EXISTS idx_attempts_question ON answer_attempts (question_id);
CREATE INDEX IF NOT EXISTS idx_attempts_answered_at ON answer_attempts (answered_at);
CREATE INDEX IF NOT EXISTS idx_notes_order ON notes (sort_order, id);

INSERT INTO topics (name, description)
SELECT 'Maths for Primary Students', 'Primary-level learning questions'
WHERE NOT EXISTS (
    SELECT 1 FROM topics WHERE name = 'Maths for Primary Students'
);

INSERT INTO topics (name, description)
SELECT 'Maths for Secondary Students', 'Secondary-level learning questions'
WHERE NOT EXISTS (
    SELECT 1 FROM topics WHERE name = 'Maths for Secondary Students'
);

INSERT INTO topics (name, description)
SELECT 'Maths for Higher Education', 'Higher education learning questions'
WHERE NOT EXISTS (
    SELECT 1 FROM topics WHERE name = 'Maths for Higher Education'
);

INSERT INTO topics (name, description)
SELECT 'Tourism Melaka', 'Questions about Melaka tourism and heritage'
WHERE NOT EXISTS (
    SELECT 1 FROM topics WHERE name = 'Tourism Melaka'
);

INSERT INTO notes (emoji, title, points_json, external_url, sort_order)
SELECT
    '📚',
    'Nota Permainan',
    '["Open the learning notes using the link below."]',
    'https://drive.google.com/file/d/1sy4XubeiHPjBC1fboPRl7OMrdg7TDrDB/view?usp=sharing',
    0
WHERE NOT EXISTS (SELECT 1 FROM notes);
