# app/core/alert_engine.py
from app.models.notification_models import AlertType

# Each rule: check if campaign metric breaches the threshold
ALERT_CHECKS = {
    AlertType.CTR_LOW: {
        "field":   "ctr",
        "message": lambda c, t: f"CTR dropped to {c['ctr']}% (threshold: {t}%) on campaign '{c['name']}'",
        "check":   lambda val, threshold: val < threshold,
    },
    AlertType.SPEND_HIGH: {
        "field":   "spend",
        "message": lambda c, t: f"Spend ${c['spend']} exceeds {t}% of budget on campaign '{c['name']}'",
        "check":   lambda val, threshold: val < threshold,   # val = spend/budget * 100
    },
    AlertType.ROAS_LOW: {
        "field":   "roas",
        "message": lambda c, t: f"ROAS dropped to {c['roas']}x (threshold: {t}x) on campaign '{c['name']}'",
        "check":   lambda val, threshold: val < threshold,
    },
    AlertType.BUDGET_EXCEEDED: {
        "field":   "spend",
        "message": lambda c, t: f"Budget exceeded on campaign '{c['name']}' — spent ${c['spend']} of ${c['budget']}",
        "check":   lambda val, threshold: val >= threshold,  # val = spend
    },
    AlertType.CONVERSIONS_LOW: {
        "field":   "conversions",
        "message": lambda c, t: f"Conversions dropped to {c['conversions']} (threshold: {t}) on campaign '{c['name']}'",
        "check":   lambda val, threshold: val < threshold,
    },
}

# app/core/alert_engine.py

def evaluate_campaign(campaign: dict, rules: list) -> list[dict]:
    triggered = []

    for rule in rules:
        # Handle both SQLAlchemy objects and dicts
        is_active   = rule.is_active   if hasattr(rule, "is_active")   else rule.get("is_active", True)
        alert_type  = rule.alert_type  if hasattr(rule, "alert_type")  else rule.get("alert_type")
        threshold   = rule.threshold   if hasattr(rule, "threshold")   else rule.get("threshold")
        user_id     = rule.user_id     if hasattr(rule, "user_id")     else rule.get("user_id")
        campaign_id = rule.campaign_id if hasattr(rule, "campaign_id") else rule.get("campaign_id")

        if not is_active:
            continue

        alert_def = ALERT_CHECKS.get(alert_type)
        if not alert_def:
            continue

        field = alert_def["field"]
        value = campaign.get(field)

        if value is None:
            continue

        if alert_type == AlertType.SPEND_HIGH:
            budget = campaign.get("budget")
            value  = (campaign["spend"] / budget * 100) if budget > 0 else 0

        if alert_def["check"](value, threshold):
            triggered.append({
                "campaign_id": str(campaign_id),
                "alert_type":  alert_type,
                "message":     alert_def["message"](campaign, threshold),
                "user_id":     str(user_id),
            })

    return triggered