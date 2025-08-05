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
        print(f"[ERROR] User count update failed: {e}")

@app.route("/", methods=["GET", "POST"])
def home():
    result = {}
    if request.method == "POST":
        try:
            asset_input = request.form.get("input", "").strip()
            print(f"[DEBUG] Input received: {asset_input}")
            if asset_input:
                result = get_asset_data(asset_input)
                print(f"[DEBUG] Result from handler: {result}")
                update_user_count()
        except Exception as e:
            print(f"[ERROR] Exception during POST: {e}")
            result = {
                "input": asset_input if 'asset_input' in locals() else "",
                "type": "Error",
                "network": "Unknown",
                "info": f"❌ Internal error: {str(e)}",
                "risk_score": 0,
                "iso": "",
                "usage": {}
            }
    return render_template("index.html", result=result)

@app.route("/export-iso")
def export_iso():
    try:
        xml_content = request.args.get("xml", "")
        asset = request.args.get("asset", "asset")
        return send_file(
            io.BytesIO(xml_content.encode()),
            mimetype="application/xml",
            as_attachment=True,
            download_name=f"{asset}_iso.xml"
        )
    except Exception as e:
        print(f"[ERROR] Failed to export ISO: {e}")
        return "❌ Failed to export ISO", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 1000))
    app.run(host="0.0.0.0", port=port)
