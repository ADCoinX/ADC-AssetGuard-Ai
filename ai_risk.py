def calculate_risk_score(volume=None, mcap=None, holders=None, verified=None):
    try:
        if volume is not None and mcap is not None:
            ratio = volume / mcap if mcap else 0
            if ratio > 1:
                return 20  # Sangat aktif
            elif ratio > 0.1:
                return 40  # Sihat
            elif ratio > 0.01:
                return 60  # Lemah
            else:
                return 80  # Bahaya

        if holders is not None:
            if holders > 10000:
                return 20
            elif holders > 1000:
                return 40
            elif holders > 100:
                return 60
            else:
                return 80

        if verified is not None:
            return 20 if verified else 60

        return 50  # Default neutral
    except:
        return 0
