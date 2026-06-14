import os
from pathlib import Path

from .ar3d import ar3d as ar3d_bp
from .ar3d.db import init_app as init_ar3d_database

_MODULE_DIR = Path(__file__).resolve().parent


def init_ar3d(app):
    app.config.setdefault(
        "AR3D_DATABASE",
        os.environ.get(
            "AR3D_DATABASE",
            str(_MODULE_DIR / "instance" / "ar3d.sqlite3"),
        ),
    )
    app.config.setdefault(
        "AR3D_UPLOAD_FOLDER",
        os.environ.get("AR3D_UPLOAD_FOLDER", str(_MODULE_DIR / "uploads")),
    )
    app.config.setdefault(
        "AR3D_ADMIN_PASSWORD",
        os.environ.get("AR3D_ADMIN_PASSWORD", "change-me"),
    )
    app.config.setdefault(
        "AR3D_ADMIN_API_KEY",
        os.environ.get("AR3D_ADMIN_API_KEY", "change-me"),
    )

    Path(app.config["AR3D_DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    Path(app.config["AR3D_UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    if "change-me" in {
        app.config["AR3D_ADMIN_PASSWORD"],
        app.config["AR3D_ADMIN_API_KEY"],
    }:
        app.logger.warning(
            "AR3D admin credentials are using defaults. Set AR3D_ADMIN_PASSWORD "
            "and AR3D_ADMIN_API_KEY before exposing the server."
        )
    init_ar3d_database(app)


__all__ = ["ar3d_bp", "init_ar3d"]
