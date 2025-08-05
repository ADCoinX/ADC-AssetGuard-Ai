from iso_export import generate_iso_xml
from api_handler import get_asset_data

@app.route("/export-iso")
def export_iso():
    asset = request.args.get("asset", "asset")
    result = get_asset_data(asset)
    xml_data = generate_iso_xml(
        asset=asset,
        asset_type=result.get("type", "Unknown"),
        risk_score=result.get("risk_score", 0),
        note="Validated via ADC AssetGuard"
    )
    return send_file(
        io.BytesIO(xml_data.encode()),
        mimetype="application/xml",
        as_attachment=True,
        download_name=f"{asset}_iso.xml"
    )
