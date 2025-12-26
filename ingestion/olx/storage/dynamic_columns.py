import json, datetime
from sqlalchemy import text, inspect


def flatten_json(y):
    out = {}

    def flatten(x, name=""):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + "_")
        elif isinstance(x, list):
            if x:
                out[name[:-1]] = x[0]
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def save_dynamic_listing(session, data: dict):
    flat_data = flatten_json(data)

    if not hasattr(save_dynamic_listing, "known_columns"):
        inspector = inspect(session.get_bind())
        save_dynamic_listing.known_columns = {
            col["name"] for col in inspector.get_columns("listings")
        }

    sanitized = {}
    new_cols = []

    for k, v in flat_data.items():
        safe = "".join(c if c.isalnum() else "_" for c in k).lower() or "unknown_field"
        sanitized[safe] = v
        if safe not in save_dynamic_listing.known_columns:
            new_cols.append(safe)
            save_dynamic_listing.known_columns.add(safe)

    for col in new_cols:
        session.execute(
            text(f'ALTER TABLE listings ADD COLUMN IF NOT EXISTS "{col}" TEXT')
        )

    session.commit()

    res = session.execute(
        text("SELECT id FROM listings WHERE url = :url"),
        {"url": sanitized.get("url")},
    ).fetchone()

    values = {"raw_data": json.dumps(data), "created_at": datetime.datetime.utcnow()}
    for k, v in sanitized.items():
        values[k] = json.dumps(v) if isinstance(v, (dict, list)) else str(v)

    if res:
        values["id"] = res[0]
        set_clause = ", ".join(f'"{k}" = :{k}' for k in sanitized)
        session.execute(
            text(f"UPDATE listings SET raw_data=:raw_data, {set_clause} WHERE id=:id"),
            values,
        )
    else:
        cols = ", ".join(f'"{c}"' for c in values)
        vals = ", ".join(f":{c}" for c in values)
        session.execute(text(f"INSERT INTO listings ({cols}) VALUES ({vals})"), values)

    session.commit()
