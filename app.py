from flask import Flask, render_template, request, send_file
from api_handler import get_asset_data
from google_logger import log_scan
from iso_export import generate_iso_xml
import io
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    result = {}
    if request.method == 'POST':
        user_input = request.form['asset'].strip()
        result = get_asset_data(user_input)
        log_scan(user_input, result.get("type", "Unknown"))
    return render_template('index.html', result=result)

@app.route('/export-iso')
def export_iso():
    asset = request.args.get("asset")
    xml_data = generate_iso_xml(asset)
    return send_file(io.BytesIO(xml_data.encode()), mimetype='application/xml',
                     as_attachment=True, download_name=f'{asset}_iso20022.xml')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 1000))
    app.run(host='0.0.0.0', port=port)
