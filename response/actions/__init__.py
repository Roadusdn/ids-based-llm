from response.actions.firewall import block_ip, throttle_ip, quarantine_ip
from response.actions.zeekctl import terminate_session
from response.actions.notifier import send_webhook
from response.actions.audit import mark_for_review, open_ticket


ACTION_MAP = {
    "block_ip": block_ip,
    "throttle_ip": throttle_ip,
    "terminate_session": terminate_session,
    "notify": send_webhook,
    "quarantine_ip": quarantine_ip,
    "mark_for_review": mark_for_review,
    "open_ticket": open_ticket,
}


def execute(action_name, **kwargs):
    if action_name not in ACTION_MAP:
        raise ValueError(f"Unknown action: {action_name}")
    return ACTION_MAP[action_name](**kwargs)
