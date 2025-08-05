from datetime import datetime

def generate_iso_xml(asset, asset_type="Unknown", risk_score=0, note="Validated via ADC AssetGuard"):
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
    <AssetValidationReport>
        <AssetID>{asset}</AssetID>
        <AssetType>{asset_type}</AssetType>
        <RiskScore>{risk_score}</RiskScore>
        <ValidationNote>{note}</ValidationNote>
        <ValidationDate>{now}</ValidationDate>
        <Standard>ISO 20022-Inspired</Standard>
        <Issuer>ADC AssetGuard + AI</Issuer>
    </AssetValidationReport>
</Document>"""
    return xml_template
