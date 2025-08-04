from flask import Flask, render_template, request, send_file
from get_asset_data import get_asset_data
from iso_export import generate_iso_xml
from google_logger import log_scan
import io
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = {}
    if request.method == 'POST':
        user_input = request.form['wallet']
        result = get_asset_data(user_input)
        log_scan(user_input, result.get("type", "Unknown"))
    return render_template('index.html', result=result)

@app.route('/export-iso')
def export_iso():
    user_input = request.args.get("wallet")
    result = get_asset_data(user_input)
    xml = generate_iso_xml(result)
    return send_file(io.BytesIO(xml.encode()), mimetype='application/xml',
                     as_attachment=True, download_name=f'{user_input}_iso.xml')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 1000))
    app.run(host='0.0.0.0', port=port)
