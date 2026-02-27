from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)


def get_all_cards():
    """Fetch all active cards with their reward rates joined."""
    return (
        supabase.table("cards")
        .select("*, reward_rates(*)")
        .eq("is_active", True)
        .execute()
        .data
    )


def get_strategy_result(session_id: str):
    return (
        supabase.table("strategy_results")
        .select("*")
        .eq("session_id", session_id)
        .maybe_single()
        .execute()
        .data
    )


def get_simulation_result(session_id: str):
    try:
        return (
            supabase.table("simulation_results")
            .select("*")
            .eq("session_id", session_id)
            .maybe_single()
            .execute()
            .data
        )
    except Exception:
        # If anything goes wrong fetching simulation, fall back to None so
        # callers can safely treat simulation as unavailable.
        return None


def update_session_status(session_id: str, status: str):
    (
        supabase.table("sessions")
        .update({"status": status})
        .eq("id", session_id)
        .execute()
    )

