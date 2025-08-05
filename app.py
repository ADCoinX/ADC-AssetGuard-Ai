from flask import Flask, render_template, request, send_file
from api_handler import get_asset_data
from iso_export import generate_iso_xml
from utils import get_usage_stats
import io
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = {}
    total = get_usage_stats()
    if request.method == "POST":
        asset = request.form["wallet"].strip()
        result = get_asset_data(asset)
    return render_template("index.html", result=result, total=total)

@app.route("/export-iso")
def export_iso():
    asset = request.args.get("asset")
    xml_data = generate_iso_xml(asset)
    return send_file(io.BytesIO(xml_data.encode()),
                     mimetype="application/xml",
                     as_attachment=True,
                     download_name=f"{asset}_iso20022.xml")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 1000))
    app.run(host="0.0.0.0", port=port)
