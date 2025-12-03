import logging
from app.database.supabase_client import get_supabase
from app.services.design_paste_from_sweet import design_paste_for_sweet_id
from app.paste_core.base_profiles import white_base_profile
from app.paste_core.gelato_infusion import recommend_paste_in_gelato


def main():
    supabase = get_supabase()
    resp = (
        supabase.table("sweet_compositions")
        .select("id, sweet_name, category")
        .limit(30)
        .execute()
    )
    rows = resp.data or []
    base = white_base_profile()
    for row in rows:
        sid = row["id"]
        name = row.get("sweet_name") or row.get("name")
        category = row.get("category")
        try:
            designed = design_paste_for_sweet_id(sweet_id=sid, batch_weight_g=1000.0)
        except Exception as e:
            logging.exception(f"[SKIP] {name} (id={sid}) – error in paste design: {e}")
            continue
        v = designed.validation
        print(f"\n=== {name} (id={sid}, cat={category}) ===")
        print("Paste overall:", v.overall_status)
        try:
            rec = recommend_paste_in_gelato(
                paste_metrics=designed.metrics,
                base_profile=base,
                sweet_profile=designed.sweet_profile,
            )
            print(
                f"→ White base: science_max={rec.p_science_max * 100:.1f}%, reco_max={rec.p_recommended_max * 100:.1f}%, default={rec.p_recommended_default * 100:.1f}%"
            )
        except Exception as e:
            logging.exception(f"→ Infusion calc error: {e}")


if __name__ == "__main__":
    main()