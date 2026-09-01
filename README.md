# Baw-Baw.com registration form

A ReactPy interface served by FastAPI that stores pet owner registrations in
MongoDB Atlas.

## 1. Set up MongoDB Atlas

1. Sign in at [cloud.mongodb.com](https://cloud.mongodb.com).
2. Create a free **M0** cluster. Choose AWS with the Mumbai or Singapore region.
3. **Database Access** → Add New Database User. Use password authentication and
   the "Read and write to any database" role. Copy the password immediately.
4. **Network Access** → Add IP Address → Add Current IP Address.
5. **Connect** → Drivers → Python. Copy the connection string.

The database and collection do not need to be created by hand. PyMongo creates
`SignUp.users` the first time a document is inserted.

## 2. Set up the project

Open a terminal in this folder.

```powershell
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and paste your connection string into it,
replacing `<db_password>` with your real password:

```powershell
copy .env.example .env
```

If your password contains `@`, `:`, `/`, `?`, `#` or `%`, replace it with one
that doesn't. Those characters have meaning inside a URI and will cause an
authentication error.

## 3. Test the database connection

```powershell
python test_db.py
```

This inserts a document, counts the collection, then deletes the document
again. Get this working before moving on.

## 4. Run the app

```powershell
uvicorn main:app --reload
```

Open <http://127.0.0.1:8000>. Note that `python main.py` will not work — the
file defines a FastAPI app rather than starting a server itself.

Fill in the form and submit. The terminal prints the inserted document ID, and
the record appears under Browse Collections in Atlas.

## Common errors

| Message | Cause |
| --- | --- |
| `dns.resolver.NXDOMAIN` | The cluster hostname does not exist. Free clusters are deleted after long inactivity — create a new one and update `.env`. |
| `ServerSelectionTimeoutError` | Your IP is not whitelisted in Network Access, or the cluster is paused. |
| `Authentication failed` | Wrong username or password, the `<db_password>` placeholder was left in, or a special character in the password. |
| `dnspython module must be installed` | Install with `pymongo[srv]`, not plain `pymongo`. |

## Notes

Passwords are hashed with bcrypt before being stored, so the `password_hash`
field in Atlas is deliberately unreadable. A unique index on `gmail` prevents
the same address registering twice.
