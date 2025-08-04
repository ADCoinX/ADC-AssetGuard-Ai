def calculate_risk_score(balance=0, holders=0, volume=0):
    score = 50
    if balance > 1:
        score += 20
    elif balance == 0:
        score -= 30
    if holders:
        score += min(holders // 1000, 20)
    if volume:
        score += min(int(volume / 10000), 20)
    return max(0, min(score, 100))
