from flask import Flask, render_template, request, send_file
from api_handler import get_asset_data
import io

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = {}
    if request.method == "POST":
        asset_input = request.form["input"]
        result = get_asset_data(asset_input)
    return render_template("index.html", result=result)

@app.route("/export-iso")
def export_iso():
    xml_content = request.args.get("xml")
    asset = request.args.get("asset", "asset")
    return send_file(io.BytesIO(xml_content.encode()), mimetype="application/xml",
                     as_attachment=True, download_name=f"{asset}_iso.xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1000)
