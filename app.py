from flask import Flask, render_template, request, send_file
from api_handler import get_asset_data
import io
import os

app = Flask(__name__)

def update_user_count():
    count_file = os.path.join('static', 'user_count.txt')
    try:
        if os.path.exists(count_file):
            with open(count_file, 'r') as f:
                count = int(f.read().strip())
        else:
            count = 0
        count += 1
        with open(count_file, 'w') as f:
            f.write(str(count))
    except Exception as e:
        print(f"User count update failed: {e}")

@app.route("/", methods=["GET", "POST"])
def home():
    result = {}
    if request.method == "POST":
        asset_input = request.form.get("input", "").strip()
        if asset_input:
            result = get_asset_data(asset_input)
            update_user_count()
    return render_template("index.html", result=result)

@app.route("/export-iso")
def export_iso():
    xml_content = request.args.get("xml", "")
    asset = request.args.get("asset", "asset")
    return send_file(
        io.BytesIO(xml_content.encode()),
        mimetype="application/xml",
        as_attachment=True,
        download_name=f"{asset}_iso.xml"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 1000))
    app.run(host="0.0.0.0", port=port)
