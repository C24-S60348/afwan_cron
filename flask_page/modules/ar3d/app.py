import os
from pathlib import Path

from flask import Flask, jsonify

from ar3d import ar3d
from ar3d.db import init_app as init_database


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    server_dir = Path(__file__).resolve().parent

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "development-only-secret"),
        DATABASE=os.environ.get(
            "AR3D_DATABASE", str(Path(app.instance_path) / "ar3d.sqlite3")
        ),
        UPLOAD_FOLDER=os.environ.get(
            "AR3D_UPLOAD_FOLDER", str(server_dir / "uploads")
        ),
        ADMIN_PASSWORD=os.environ.get("AR3D_ADMIN_PASSWORD", "change-me"),
        ADMIN_API_KEY=os.environ.get("AR3D_ADMIN_API_KEY", "change-me"),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    )

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    init_database(app)
    app.register_blueprint(ar3d)

    @app.get("/")
    def index():
        return jsonify(
            {
                "name": "i.-GB AR3D API",
                "health": "/api/ar3d/health",
                "questions": "/api/ar3d/questions",
                "notes": "/api/ar3d/notes",
                "admin": "/admin/ar3d",
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
