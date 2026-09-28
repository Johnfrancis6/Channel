// Écran d'accueil : liste des documents, recherche plein texte, renommer, supprimer.
import { useEffect, useState } from 'preact/hooks';
import type { DocumentSummary } from '../shared/types';
import { api, SessionExpiredError } from './api';
import { PromptSheet, Sheet } from './components';
import { docFromDetail, type DocState } from './doc';
import { IconCamera, IconImport, IconMore, IconTrash } from './icons';
import { toast, withBusy } from './ui';

interface Props {
  onScan: (mode: 'camera' | 'library') => void;
  onOpen: (doc: DocState) => void;
}

function formatDate(ms: number): string {
  const d = new Date(ms);
  const today = new Date();
  if (d.toDateString() === today.toDateString()) return `aujourd’hui, ${d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}`;
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: d.getFullYear() === today.getFullYear() ? undefined : 'numeric' });
}

export function Home({ onScan, onOpen }: Props) {
  const [q, setQ] = useState('');
  const [docs, setDocs] = useState<DocumentSummary[] | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [menu, setMenu] = useState<DocumentSummary | null>(null);
  const [renaming, setRenaming] = useState<DocumentSummary | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let alive = true;
    const t = setTimeout(
      () => {
        api.list(q.trim()).then(
          (r) => alive && (setDocs(r.documents), setError(null)),
          (e: Error) => alive && setError(e),
        );
      },
      q ? 250 : 0,
    );
    return () => {
      alive = false;
      clearTimeout(t);
    };
  }, [q, tick]);

  async function open(d: DocumentSummary) {
    const detail = await withBusy('Ouverture…', () => api.get(d.id));
    if (detail) onOpen(docFromDetail(detail));
  }

  async function remove(d: DocumentSummary) {
    setMenu(null);
    if (!confirm(`Supprimer « ${d.title} » ? C’est définitif.`)) return;
    await withBusy('Suppression…', () => api.remove(d.id));
    toast('Document supprimé');
    setTick((n) => n + 1);
  }

  async function rename(d: DocumentSummary, title: string) {
    setRenaming(null);
    await withBusy('Renommage…', () => api.rename(d.id, title));
    setTick((n) => n + 1);
  }

  return (
    <div class="screen">
      <header class="topbar">
        <h1>Documents</h1>
      </header>
      <div class="search">
        <input type="search" placeholder="Rechercher dans les titres et les textes" value={q} onInput={(e) => setQ((e.target as HTMLInputElement).value)} enterKeyHint="search" />
      </div>
      <main class="content">
        {error ? (
          <div class="empty">
            <p>{error.message}</p>
            {error instanceof SessionExpiredError ? (
              <button class="btn primary" onClick={() => location.reload()}>
                Se reconnecter
              </button>
            ) : (
              <button class="btn" onClick={() => setTick((n) => n + 1)}>
                Réessayer
              </button>
            )}
          </div>
        ) : docs === null ? (
          <p class="empty">Chargement…</p>
        ) : docs.length === 0 ? (
          <p class="empty">{q ? 'Aucun résultat.' : 'Aucun document. Touche « Scanner » pour commencer.'}</p>
        ) : (
          <ul class="doc-list">
            {docs.map((d) => (
              <li key={d.id} class="doc-item">
                <button class="open" onClick={() => open(d)}>
                  {d.coverPageId ? <img class="thumb" src={api.fileUrl(d.id, d.coverPageId, 'thumb')} alt="" loading="lazy" /> : <span class="thumb" />}
                  <span class="meta">
                    <span class="title">{d.title}</span>
                    <span class="sub">
                      {formatDate(d.updatedAt)} · {d.pageCount} page{d.pageCount > 1 ? 's' : ''}
                    </span>
                    {/* Extrait échappé côté serveur ; seules les balises <mark> sont ajoutées. */}
                    {d.snippet && <span class="snippet" dangerouslySetInnerHTML={{ __html: d.snippet }} />}
                  </span>
                </button>
                <button class="icon-btn" aria-label={`Actions pour ${d.title}`} onClick={() => setMenu(d)}>
                  <IconMore />
                </button>
              </li>
            ))}
          </ul>
        )}
      </main>
      <div class="fab-row">
        <button class="btn big" onClick={() => onScan('library')}>
          <IconImport /> Importer
        </button>
        <button class="btn big primary" onClick={() => onScan('camera')}>
          <IconCamera /> Scanner
        </button>
      </div>

      {menu && (
        <Sheet title={menu.title} onClose={() => setMenu(null)}>
          <button
            class="btn"
            onClick={() => {
              setRenaming(menu);
              setMenu(null);
            }}
          >
            Renommer
          </button>
          <button class="btn danger" onClick={() => remove(menu)}>
            <IconTrash /> Supprimer
          </button>
        </Sheet>
      )}
      {renaming && <PromptSheet title="Renommer" value={renaming.title} onClose={() => setRenaming(null)} onSubmit={(t) => rename(renaming, t)} />}
    </div>
  );
}
