-- Schéma initial de Scanner. Dates en millisecondes depuis l'époque Unix.

CREATE TABLE documents (
  id            TEXT PRIMARY KEY,
  title         TEXT NOT NULL,
  created_at    INTEGER NOT NULL,
  updated_at    INTEGER NOT NULL,
  page_count    INTEGER NOT NULL DEFAULT 0,
  cover_page_id TEXT
);

CREATE INDEX documents_updated_at ON documents (updated_at DESC);

CREATE TABLE pages (
  document_id    TEXT NOT NULL REFERENCES documents (id) ON DELETE CASCADE,
  idx            INTEGER NOT NULL,
  id             TEXT NOT NULL,
  width          INTEGER NOT NULL,
  height         INTEGER NOT NULL,
  corners        TEXT,             -- JSON : [[x,y],[x,y],[x,y],[x,y]] dans le repère de l'original
  rotation       INTEGER NOT NULL DEFAULT 0,
  filter         TEXT NOT NULL DEFAULT 'original',
  processed_type TEXT NOT NULL DEFAULT 'image/jpeg',
  ocr_json       TEXT,             -- JSON : { width, height, lines: [{ text, bbox, confidence }] }
  ocr_text       TEXT,             -- texte (éventuellement corrigé à la main)
  PRIMARY KEY (document_id, idx)
);

CREATE UNIQUE INDEX pages_id ON pages (document_id, id);

-- Recherche plein texte, insensible aux accents. Réécrite à chaque enregistrement.
CREATE VIRTUAL TABLE docs_fts USING fts5 (
  document_id UNINDEXED,
  title,
  body,
  tokenize = 'unicode61 remove_diacritics 2'
);
