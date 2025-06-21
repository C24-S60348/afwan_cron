#sudo nano /etc/systemd/system/quartapp.service


from quart import Quart

app = Quart(__name__)

if __name__ == "__main__":
    app.run()

@app.route("/")
async def home():
    return {"message": "Hello from Quart + Webdock!!!"}

@app.route("/sara")
async def sara():
    return {"dari afwan":"HAI SARAAAA SAYANGGGGG"}
