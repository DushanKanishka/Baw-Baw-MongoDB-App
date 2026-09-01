
# 🐾 Baw-Baw.com — Pet Owner Registration System

A registration form for pet owners, built with **ReactPy** for the interface,
served through **FastAPI**, and backed by **MongoDB Atlas** for storage.
Built as a first-year NoSQL assignment demonstrating a Python web app
connected to a cloud NoSQL database.

## Demo



Uploading Demo2.mp4…



*Video link goes here once recorded.*

## Overview

Baw-Baw.com is a small full-stack demo built around one workflow: a pet
owner fills in their name, their pet's name, an email, and a password, and
that submission is validated, hashed, and written to a MongoDB Atlas
collection.

It exists to demonstrate three things together:
- A Python web UI (ReactPy) with no separate frontend build step
- A REST-capable backend (FastAPI) hosting that UI
- A NoSQL document database (MongoDB Atlas) as the persistence layer

**Features**
- Client-side-feeling form built entirely in Python (no HTML/JS files)
- Server-side validation (required fields, email shape, password length)
- Passwords hashed with `bcrypt` before storage — never stored in plaintext
- Duplicate email addresses rejected via a unique MongoDB index
- Connection credentials kept out of source control via `.env`

## Project Structure

```
files/
├── main.py            # FastAPI app + ReactPy form + MongoDB writes
├── test_db.py          # Standalone script to verify the Atlas connection
├── requirements.txt    # Pinned Python dependencies
├── .env.example         # Template for required environment variables
├── .env                 # Your real credentials (git-ignored, not in repo)
├── .gitignore
└── README.md
```

| File | Responsibility |
| --- | --- |
| `main.py` | Defines the `signup_form` ReactPy component, form validation and submit logic (`register_user`), the MongoDB connection, and mounts everything onto a FastAPI `app` object via `configure()`. |
| `test_db.py` | Connects to Atlas, inserts a throwaway document, counts the collection, then deletes it. Used to isolate database problems from application problems. |
| `.env` | Holds `MONGODB_URI`, `DB_NAME`, `COLLECTION_NAME` — read at runtime with `os.getenv()`, never hardcoded in the Python files. |

## Architecture

![Architecture](assets/architecture-tb.png)

**Request flow for a submission:**
1. ReactPy tracks each input's value in component state (`use_state`).
2. On submit, `handle_submit` collects that state into a dict and calls
   `register_user()`.
3. `register_user()` validates the fields, hashes the password with bcrypt,
   and calls `collection.insert_one()`.
4. PyMongo sends the write to Atlas over the `mongodb+srv://` connection
   established once at startup.
5. The result (success or a specific error message) is pushed back into
   component state, which re-renders the message line under the form —
   no page reload, since ReactPy diffs and patches the DOM over a
   websocket connection FastAPI manages for it.

**Why FastAPI is needed even though the logic is simple:** ReactPy is a
UI library, not a server. `reactpy.backend.fastapi.configure()` is what
turns the component into servable HTML/JS and opens the websocket FastAPI
uses to keep the UI in sync with server-side state changes.

## Setup

### 1. MongoDB Atlas

1. Sign in at [cloud.mongodb.com](https://cloud.mongodb.com).
2. Create a free **M0** cluster (labelled "Free" in the newer UI). AWS,
   Mumbai or Singapore region.
3. **Database Access** -> Add New Database User -> password auth -> "Read
   and write to any database." Copy the password immediately.
4. **Network Access** -> Add IP Address -> Add Current IP Address.
5. **Connect** -> Drivers -> Python. Copy the connection string.

The `SignUp` database and `users` collection don't need to be created by
hand — PyMongo creates both on the first insert.

### 2. Project setup

```powershell
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and paste in your real connection string:

```powershell
copy .env.example .env
```

If your database password contains `@ : / ? # %`, choose a different one —
those characters break the connection string.

### 3. Test the connection

```powershell
python test_db.py
```

Confirms the database independently of the web app.

### 4. Run the app

```powershell
uvicorn main:app --reload
```

Open <http://127.0.0.1:8000>. `python main.py` will not work — the file
defines a FastAPI app object rather than starting a server itself.

## Common errors

| Message | Cause |
| --- | --- |
| `dns.resolver.NXDOMAIN` | Cluster hostname doesn't exist — free clusters get deleted after long inactivity. Create a new one and update `.env`. |
| `ServerSelectionTimeoutError` | IP not whitelisted in Network Access, or the cluster is paused. |
| `Authentication failed` | Wrong username/password, the `<db_password>` placeholder left in, or a special character in the password. |
| `dnspython module must be installed` | Install with `pymongo[srv]`, not plain `pymongo`. |
| `ModuleNotFoundError` after installing | The venv isn't activated, or `pip` installed into a different Python than the one running the script. |

## Security notes

- Passwords are hashed with bcrypt (`password_hash` field) — never stored
  or logged in plaintext.
- `.env` is excluded via `.gitignore`; only `.env.example` (a template with
  no real values) is committed.
- A unique index on `gmail` prevents duplicate registrations.
- This is a coursework demo, not a production auth system — there's no
  session management, rate limiting, or CSRF protection.

## Tech stack

- [ReactPy](https://reactpy.dev/) — component-based UI in pure Python
- [FastAPI](https://fastapi.tiangolo.com/) — ASGI web framework
- [MongoDB Atlas](https://www.mongodb.com/atlas) — managed NoSQL database
- [PyMongo](https://pymongo.readthedocs.io/) — MongoDB driver
- [bcrypt](https://pypi.org/project/bcrypt/) — password hashing
