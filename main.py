"""
Baw-Baw.com — pet owner registration form.

A ReactPy front end served by FastAPI, writing submissions to MongoDB Atlas.

Run with:  uvicorn main:app --reload
Then open: http://127.0.0.1:8000
"""

import os
from datetime import datetime, timezone

import bcrypt
from dotenv import load_dotenv
from fastapi import FastAPI
from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi
from reactpy import component, event, html, use_state
from reactpy.backend.fastapi import configure

# --------------------------------------------------------------------------
# Database setup
# --------------------------------------------------------------------------

load_dotenv()  # reads the .env file sitting next to this script

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "SignUp")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "users")

if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI is not set. Copy .env.example to .env and paste your "
        "Atlas connection string into it."
    )

client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi("1"),
    serverSelectionTimeoutMS=10_000,  # fail in 10s instead of hanging for 30
)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


def check_connection() -> bool:
    """Ping the server so connection problems show up at startup, not on submit."""
    try:
        client.admin.command("ping")
        print(f"Connected to MongoDB. Writing to {DB_NAME}.{COLLECTION_NAME}")
        # One account per email address.
        collection.create_index([("gmail", ASCENDING)], unique=True)
        return True
    except PyMongoError as exc:
        print("Could not reach MongoDB:")
        print(f"  {exc}")
        print("  Check your URI, your database password, and Network Access in Atlas.")
        return False


check_connection()


def register_user(form: dict) -> tuple[bool, str]:
    """Validate a submission and insert it. Returns (succeeded, message)."""
    ownername = form["ownername"].strip()
    petname = form["petname"].strip()
    password = form["password"]
    gmail = form["gmail"].strip().lower()

    if not all([ownername, petname, password, gmail]):
        return False, "Fill in all four fields to continue."
    if "@" not in gmail:
        return False, "That email address is missing an @ sign."
    if len(password) < 6:
        return False, "Use a password of at least 6 characters."

    # Store a hash, never the password itself. bcrypt salts each hash for us.
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    document = {
        "ownername": ownername,
        "petname": petname,
        "gmail": gmail,
        "password_hash": password_hash.decode("utf-8"),
        "created_at": datetime.now(timezone.utc),
    }

    try:
        result = collection.insert_one(document)
    except PyMongoError as exc:
        if "duplicate key" in str(exc):
            return False, f"{gmail} is already registered."
        print(f"Insert failed: {exc}")
        return False, "Could not save to the database. Check the terminal."

    print(f"Inserted document {result.inserted_id}")
    return True, f"Welcome, {ownername}. {petname} is registered."


# --------------------------------------------------------------------------
# Interface
# --------------------------------------------------------------------------

FIELD_STYLE = {
    "font_family": "Georgia, serif",
    "font_size": "16px",
    "padding": "10px 12px",
    "border": "2px solid #7399bf",
    "border_radius": "8px",
    "margin": "6px 0",
    "width": "100%",
    "box_sizing": "border-box",
    "outline": "none",
}

BUTTON_STYLE = {
    "font_family": "Georgia, serif",
    "font_size": "16px",
    "padding": "10px 12px",
    "border": "none",
    "border_radius": "8px",
    "background_color": "#7399bf",
    "color": "white",
    "margin_top": "14px",
    "width": "100%",
    "cursor": "pointer",
}

CARD_STYLE = {
    "background_color": "rgba(255, 255, 255, 0.93)",
    "padding": "32px",
    "border_radius": "14px",
    "max_width": "380px",
    "margin": "0 auto",
}

PAGE_STYLE = {
    "padding": "60px 20px",
    "background_image": "url(https://reactpy.neocities.org/photo/bigdogs.jpg)",
    "background_size": "cover",
    "background_position": "center",
    "margin": "0px",
    "min_height": "100vh",
}


@component
def signup_form():
    ownername, set_ownername = use_state("")
    petname, set_petname = use_state("")
    password, set_password = use_state("")
    gmail, set_gmail = use_state("")
    message, set_message = use_state("")
    succeeded, set_succeeded = use_state(False)

    def handle_submit(_event):
        ok, text = register_user(
            {
                "ownername": ownername,
                "petname": petname,
                "password": password,
                "gmail": gmail,
            }
        )
        set_succeeded(ok)
        set_message(text)
        if ok:
            set_ownername("")
            set_petname("")
            set_password("")
            set_gmail("")

    def text_field(placeholder, value, setter, input_type="text"):
        return html.input(
            {
                "type": input_type,
                "placeholder": placeholder,
                "value": value,
                "on_change": lambda e, s=setter: s(e["target"]["value"]),
                "style": FIELD_STYLE,
            }
        )

    return html.div(
        {"style": PAGE_STYLE},
        html.div(
            {"style": CARD_STYLE},
            html.h1(
                {
                    "style": {
                        "font_family": "Georgia, serif",
                        "font_size": "30px",
                        "color": "#3f5f80",
                        "margin_top": "0",
                        "margin_bottom": "4px",
                    }
                },
                "Baw-Baw.com",
            ),
            html.p(
                {
                    "style": {
                        "font_family": "Georgia, serif",
                        "color": "#5a5a5a",
                        "margin_top": "0",
                        "margin_bottom": "20px",
                    }
                },
                "Register you and your pet.",
            ),
            html.form(
                {"on_submit": event(handle_submit, prevent_default=True)},
                text_field("Owner name", ownername, set_ownername),
                text_field("Pet name", petname, set_petname),
                text_field("Email address", gmail, set_gmail, "email"),
                text_field("Password", password, set_password, "password"),
                html.button(
                    {
                        "type": "submit",
                        "on_click": event(handle_submit, prevent_default=True),
                        "style": BUTTON_STYLE,
                    },
                    "Create account",
                ),
            ),
            html.p(
                {
                    "style": {
                        "font_family": "Georgia, serif",
                        "color": "#2e7d4f" if succeeded else "#a33",
                        "min_height": "20px",
                        "margin_bottom": "0",
                    }
                },
                message,
            ),
        ),
    )


app = FastAPI()
configure(app, signup_form)
