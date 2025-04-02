from accounts.models import User


def jwt_get_user_id_from_payload_handler(payload):
    """
    Override this function if user_id is formatted differently in payload
    """

    return User.objects.get(id=payload.get("user_id")).username
