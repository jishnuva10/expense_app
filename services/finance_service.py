from services.supabase_client import get_client


def add_transaction(user_id, amount, category, date, description, type, notes, CFO):
    supabase = get_client()

    data = {
        "user_id": user_id,
        "amount": amount,
        "category": category,
        "type": type,
        "date": str(date),
        "description": description,
        "notes": notes,
        "CFO": CFO
    }

    return supabase.table("transactions").insert(data).execute()

    return response.data


def get_transactions(user_id):
    supabase = get_client()

    response = (
        supabase
        .table("transactions")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    return response.data