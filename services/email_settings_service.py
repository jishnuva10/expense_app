from services.supabase_client import get_client


def save_email_settings(user_id, data):
    supabase = get_client()

    return (
        supabase
        .table("email_settings")
        .upsert(
            {"user_id": user_id, **data},
            on_conflict="user_id"
        )
        .execute()
    )


def get_email_settings(user_id):
    supabase = get_client()

    res = (
        supabase
        .table("email_settings")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    return res.data[0] if res.data else {}