import requests

def send_discord_alert(webhook_url, machine_id, probability, sensors):
    if not webhook_url:
        return

    payload = {
        "content": "⚠️ **High Failure Risk Detected!**",
        "embeds": [
            {
                "title": f"Machine Alert: {machine_id}",
                "color": 16711680,  # Red
                "fields": [
                    {"name": "Failure Probability", "value": f"{probability:.2%}", "inline": True},
                    {"name": "Tool Wear", "value": f"{sensors['Tool wear min']} min", "inline": True},
                    {"name": "Torque", "value": f"{sensors['Torque Nm']} Nm", "inline": True},
                    {"name": "Rotational Speed", "value": f"{sensors['Rotational speed rpm']} rpm", "inline": True}
                ],
                "footer": {"text": "PdM Dashboard Notification"}
            }
        ]
    }

    try:
        requests.post(webhook_url, json=payload)
    except Exception as e:
        print(f"Error sending alert: {e}")
