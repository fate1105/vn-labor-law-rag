import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

conn = sqlite3.connect("data/graph/legal_graph.db")
conn.row_factory = sqlite3.Row

# Tìm doc_id của BLLĐ 45/2019
cur = conn.execute(
    "SELECT doc_id, title, effect_status FROM documents WHERE title LIKE '%45/2019%' LIMIT 5"
)
docs = cur.fetchall()
print("=== BLLĐ 45/2019 docs ===")
for d in docs:
    print(f"  doc_id={d['doc_id']} | status={d['effect_status']} | {d['title'][:70]}")

if docs:
    doc_id = str(docs[0]["doc_id"])
    print(f"\n=== Quan hệ INCOMING tác động lên doc_id={doc_id} ===")
    cur2 = conn.execute(
        """
        SELECT * FROM relationships
        WHERE other_doc_id = ? AND direction = 'OUTGOING'
          AND rel_type IN ('THAY_THE', 'BAI_BO', 'SUA_DOI')
        ORDER BY importance DESC LIMIT 10
        """,
        (doc_id,),
    )
    rels = cur2.fetchall()
    if not rels:
        print("  (không có quan hệ incoming)")
    for r in rels:
        cur3 = conn.execute("SELECT title FROM documents WHERE doc_id = ?", (str(r["doc_id"]),))
        row = cur3.fetchone()
        src_title = row["title"][:60] if row else "(ngoài scope)"
        print(
            f"  [{r['rel_type']}] importance={r['importance']} | "
            f"from doc_id={r['doc_id']} | {src_title}"
        )

conn.close()
