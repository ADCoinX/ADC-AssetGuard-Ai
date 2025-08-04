def generate_iso_xml(data):
    asset_type = data.get("type", "Unknown")
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<AssetAuditReport>
  <AssetType>{asset_type}</AssetType>
  <Input>{data.get("input")}</Input>
  <Network>{data.get("network")}</Network>
  <Details>{data.get("info")}</Details>
  <RiskScore>{data.get("risk_score")}</RiskScore>
  <ComplianceStandard>ISO 20022-Inspired + ISO/TC 307</ComplianceStandard>
  <GeneratedBy>ADC AssetGuard + AI</GeneratedBy>
</AssetAuditReport>'''
    return xml
