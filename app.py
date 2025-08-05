from flask import Flask, render_template, request, send_file
from get_asset_data import get_asset_data
from iso_export import generate_iso_xml
from google_logger import log_scan
import io
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    try:
        if request.method == 'POST':
            user_input = request.form.get('asset', '').strip()
            print(f"[DEBUG] Input: {user_input}")

            result = get_asset_data(user_input)

            if not isinstance(result, dict):
                raise Exception("get_asset_data() did not return dict")

            result["input"] = user_input

            try:
                log_scan(user_input, result.get("type", "Unknown"))
            except Exception as log_err:
                print(f"[LOG ERROR] {log_err}")

    except Exception as main_err:
        print(f"[MAIN ERROR] {main_err}")
        result = {
            "type": "Error",
            "network": "Unknown",
            "balance": f"❌ Internal Error: {str(main_err)}",
            "risk_score": 0,
            "input": "N/A"
        }

    return render_template('index.html', result=result)


@app.route('/export-iso')
def export_iso():
    try:
        asset = request.args.get("asset", "")
        result = get_asset_data(asset)

        if not isinstance(result, dict):
            raise Exception("get_asset_data() failed during export")

        xml = generate_iso_xml(result)

        return send_file(
            io.BytesIO(xml.encode()),
            mimetype='application/xml',
            as_attachment=True,
            download_name=f'{asset}_iso.xml'
        )

    except Exception as e:
        print(f"[EXPORT ERROR] {e}")
        return "❌ Failed to generate ISO report", 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 1000))
    app.run(host='0.0.0.0', port=port, debug=True)
