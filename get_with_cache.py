import os, json, time
from dotenv import load_dotenv
import couchdb, redis

# Load environment variables
load_dotenv()

COUCHDB_URL  = os.getenv("COUCHDB_URL", "http://127.0.0.1:5984")
COUCHDB_USER = os.getenv("COUCHDB_USER", "admin")
COUCHDB_PASS = os.getenv("COUCHDB_PASS", "password")
COUCHDB_DB   = os.getenv("COUCHDB_DB", "movies")

# Connect to Redis
r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

# Connect to CouchDB
server = couchdb.Server(f"http://{COUCHDB_USER}:{COUCHDB_PASS}@127.0.0.1:5984/")
db = server[COUCHDB_DB]

def get_doc_cached(doc_id: str, ttl: int = 60):
    """Fetch document from Redis if cached, otherwise from CouchDB."""
    key = f"movies:{doc_id}"
    cached = r.get(key)
    if cached:
        return "CACHE", json.loads(cached)

    # fetch from CouchDB and cache it
    doc = db.get(doc_id)
    if doc:
        r.setex(key, ttl, json.dumps(doc, ensure_ascii=False))
    return "LIVE", doc

if __name__ == "__main__":
    # Pick one existing id
    rows = list(db.view("_all_docs", limit=1))
    if not rows:
        print("No documents found.")
        exit()

    doc_id = rows[0].id
    print(f"Testing caching for doc_id = {doc_id}")

    # 1st fetch (should hit CouchDB)
    t0 = time.perf_counter()
    src, doc = get_doc_cached(doc_id)
    t1 = (time.perf_counter() - t0) * 1000
    print(f"First fetch: {src} in {t1:.2f} ms")

    # 2nd fetch (should hit Redis cache)
    t0 = time.perf_counter()
    src, doc = get_doc_cached(doc_id)
    t2 = (time.perf_counter() - t0) * 1000
    print(f"Second fetch: {src} in {t2:.2f} ms")
