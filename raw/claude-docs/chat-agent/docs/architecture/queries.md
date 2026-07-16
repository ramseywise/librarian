● Exactly. The embeddings live in PostgreSQL now — the vector_store_data_gemini/ folder (.npz
  and documents.json) is no longer used at all. You can delete it safely.

> how to do a query for vector db in pg admin?

● In pgAdmin's Query Tool on the agentic_rag database, run:

  SELECT id, metadata->>'category' AS category, metadata->>'title' AS title, score
  FROM (
      SELECT id, metadata, 1 - (embedding <=> (SELECT embedding FROM documents LIMIT 1)) AS
  score
      FROM documents
  ) sub
  ORDER BY score DESC
  LIMIT 5;

  But a more useful query — search by text similarity using a real query embedding isn't
  possible directly in pgAdmin (it needs Python to call Gemini first).

  What you can do in pgAdmin:

  -- Count documents
  SELECT COUNT(*) FROM documents;

  -- See what's stored
  SELECT id, metadata->>'title' AS title, metadata->>'category' AS category
  FROM documents
  LIMIT 10;

  -- Filter by category
  SELECT metadata->>'title' AS title
  FROM documents
  WHERE metadata->>'category' = 'INTERCOM';

  -- Check embedding dimension
  SELECT id, vector_dims(embedding) AS dims FROM documents LIMIT 1;
