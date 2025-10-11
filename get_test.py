import os, json, time
from dotenv import load_dotenv
import couchdb
from cloudant.client import CouchDB as CloudantCouchDB

load_dotenv()

COUCHDB_URL  = os.getenv("COUCHDB_URL", "http://127.0.0.1:5984")
COUCHDB_USER = os.getenv("COUCHDB_USER", "admin")
COUCHDB_PASS = os.getenv("COUCHDB_PASS", "password")
COUCHDB_DB   = os.getenv("COUCHDB_DB", "movies")

# --- Client 1: couchdb ---
def test_couchdb_client():
    print("\n[Client: couchdb]")
    # supply credentials inside constructor instead of setting .resource
    server = couchdb.Server(f"http://{COUCHDB_USER}:{COUCHDB_PASS}@127.0.0.1:5984/")
    db = server[COUCHDB_DB]

    rows = list(db.view("_all_docs", limit=1))
    if not rows:
        print("No docs found.")
        return
    doc_id = rows[0].id

    t0 = time.perf_counter()
    doc = db.get(doc_id)
    t1 = (time.perf_counter() - t0) * 1000
    print(f"GET {doc_id} -> {'OK' if doc else 'MISS'} in {t1:.2f} ms")
    print(json.dumps(doc, indent=2, ensure_ascii=False)[:400], "...\n")

# --- Client 2: cloudant ---
def test_cloudant_client():
    print("\n[Client: cloudant]")
    client = CloudantCouchDB(
        COUCHDB_USER, COUCHDB_PASS,
        url=COUCHDB_URL,
        connect=True
    )
    db = client[COUCHDB_DB]
    rows = db.all_docs(limit=1).get("rows", [])
    if not rows:
        print("No docs found.")
        return
    doc_id = rows[0]["id"]

    t0 = time.perf_counter()
    doc = db[doc_id]
    t1 = (time.perf_counter() - t0) * 1000
    print(f"GET {doc_id} -> {'OK' if doc else 'MISS'} in {t1:.2f} ms")
    print(json.dumps(dict(doc), indent=2, ensure_ascii=False)[:400], "...\n")

if __name__ == "__main__":
    test_couchdb_client()
    test_cloudant_client()