# home.py
from quart import Blueprint
from afwan_server_page.handle_exceptions import handle_exceptions

home_bp = Blueprint("home_bp", __name__)

@home_bp.route("/")
async def home():
    return """
    <html><body>
    <h1>This is Afwan's server</h1>
    <script>
    document.location.href = "https://c24-s60348.github.io/index3.html";
    </script>   
    </body></html>
    """


#saje -----
@home_bp.route("/sara")
@handle_exceptions("sara")
async def sara():
    return {"dari afwan":"HAI SARAAAA SAYANGGGGGSS"}

@home_bp.route("/afwan")
@handle_exceptions("afwan")
async def afwan():
    return {"dari sara":"HAI AFWAN"}