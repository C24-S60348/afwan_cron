from flask import Blueprint

ar3d = Blueprint(
    "ar3d",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/ar3d-static",
)

from . import routes  # noqa: E402,F401
