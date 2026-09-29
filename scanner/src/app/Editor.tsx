// Éditeur d'un document : onglets Image | Texte, vignettes des pages, outils en bas.
import { useEffect, useRef, useState } from 'preact/hooks';
import type { FilterName, OcrResult, Quad } from '../shared/types';
import { FILTERS } from '../shared/types';
import { nextRotation } from '../scan/geometry';
import { PromptSheet, Sheet } from './components';
import { renderInto, revokePage, sourceCanvas, type DocState, type PageState, type Source } from './doc';
import { IconBack, IconCamera, IconCrop, IconFilter, IconImport, IconLeft, IconMore, IconPlus, IconRight, IconRotate, IconShare, IconText, IconImage, IconTrash } from './icons';
import { withBusy } from './ui';
import { TextPanel } from './TextPanel';
import { ExportSheet } from './ExportSheet';

export const FILTER_LABELS: Record<FilterName, string> = {
  original: 'Original',
  gray: 'Niveaux de gris',
  bw: 'Noir et blanc',
  enhanced: 'Couleur améliorée',
};

export interface EditorProps {
  doc: DocState;
  onChange: (d: DocState) => void;
  onClose: () => void;
  addPages: (mode: 'camera' | 'library') => Promise<PageState[]>;
  askCorners: (src: Source, quad: Quad, found: boolean) => Promise<Quad | null>;
  saveState: 'saved' | 'dirty' | 'saving' | 'error';
  onSave: () => void;
}

type Sheets = null | 'filter' | 'page' | 'rename' | 'add' | 'export';

export function Editor({ doc, onChange, onClose, addPages, askCorners, saveState, onSave }: EditorProps) {
  const [index, setIndex] = useState(0);
  const [tab, setTab] = useState<'image' | 'text'>('image');
  const [sheet, setSheet] = useState<Sheets>(null);
  const stripRef = useRef<HTMLDivElement>(null);
  const page = doc.pages[Math.min(index, doc.pages.length - 1)];

  useEffect(() => {
    if (index >= doc.pages.length && doc.pages.length > 0) setIndex(doc.pages.length - 1);
  }, [doc.pages.length]);

  useEffect(() => {
    stripRef.current?.querySelector('.current')?.scrollIntoView({ inline: 'center', block: 'nearest', behavior: 'smooth' });
  }, [index]);

  const replacePage = (p: PageState) => onChange({ ...doc, dirty: true, pages: doc.pages.map((q) => (q.id === p.id ? p : q)) });

  // L'OCR se termine après coup : on repart de l'état le plus récent, pas de celui capturé au lancement.
  const latest = useRef(doc);
  latest.current = doc;
  const setOcr = (pageId: string, ocr: OcrResult, forUrl?: string) => {
    const d = latest.current;
    const target = d.pages.find((p) => p.id === pageId);
    // Page supprimée, ou image recalculée (filtre, rotation…) pendant l'OCR : résultat périmé.
    if (!target || (forUrl !== undefined && target.processedUrl !== forUrl)) return;
    const next = { ...d, dirty: true, pages: d.pages.map((p) => (p.id === pageId ? { ...p, ocr } : p)) };
    latest.current = next;
    onChange(next);
  };

  async function rerender(p: PageState, changes: Partial<PageState>, message: string) {
    if (p.ocr && p.ocr.lines.length && !confirm('Le texte reconnu (et tes corrections) de cette page sera effacé. Continuer ?')) return;
    await withBusy(message, async () => {
      const { canvas, blob } = await sourceCanvas(doc.id, p);
      replacePage(await renderInto({ ...p, original: blob, ...changes }, canvas));
    });
  }

  async function recrop() {
    if (!page) return;
    const src = await withBusy('Chargement de la photo…', () => sourceCanvas(doc.id, page));
    if (!src) return;
    const q = await askCorners(src, page.corners, true);
    if (q) await rerender(page, { corners: q }, 'Redressement…');
  }

  async function add(mode: 'camera' | 'library') {
    setSheet(null);
    const pages = await addPages(mode);
    if (!pages.length) return;
    const at = doc.pages.length;
    onChange({ ...doc, dirty: true, pages: [...doc.pages, ...pages] });
    setIndex(at);
  }

  function move(delta: number) {
    const j = index + delta;
    if (!page || j < 0 || j >= doc.pages.length) return;
    const pages = [...doc.pages];
    [pages[index], pages[j]] = [pages[j]!, pages[index]!];
    onChange({ ...doc, dirty: true, pages });
    setIndex(j);
  }

  function removePage() {
    if (!page || !confirm('Supprimer cette page ?')) return;
    revokePage(page);
    onChange({ ...doc, dirty: true, pages: doc.pages.filter((p) => p.id !== page.id) });
    setSheet(null);
  }

  const saveLabel = { saved: 'Enregistré', dirty: 'Enregistrer', saving: 'Envoi…', error: 'Réessayer' }[saveState];

  return (
    <div class="screen editor">
      <header class="topbar">
        <button class="icon-btn" aria-label="Retour à la liste" onClick={onClose}>
          <IconBack />
        </button>
        <button class="title-button" onClick={() => setSheet('rename')}>
          {doc.title}
        </button>
        <button class={`btn save ${saveState}`} disabled={saveState === 'saving' || saveState === 'saved'} onClick={onSave}>
          {saveLabel}
        </button>
        <button class="icon-btn" aria-label="Exporter" disabled={!doc.pages.length} onClick={() => setSheet('export')}>
          <IconShare />
        </button>
      </header>

      <div class="tabs" role="tablist">
        <button role="tab" aria-selected={tab === 'image'} onClick={() => setTab('image')}>
          <IconImage /> Image
        </button>
        <button role="tab" aria-selected={tab === 'text'} onClick={() => setTab('text')}>
          <IconText /> Texte
        </button>
      </div>

      {!page ? (
        <main class="content">
          <p class="empty">Aucune page. Ajoute une photo avec le bouton +.</p>
        </main>
      ) : tab === 'image' ? (
        <main class="stage page-view">
          <img key={page.processedUrl} src={page.processedUrl} alt={`Page ${index + 1}`} />
        </main>
      ) : (
        <TextPanel key={page.id} doc={doc} page={page} setOcr={setOcr} />
      )}

      <div class="strip" ref={stripRef}>
        {doc.pages.map((p, i) => (
          <button key={p.id} class={i === index ? 'thumb current' : 'thumb'} onClick={() => (i === index ? setSheet('page') : setIndex(i))} aria-label={`Page ${i + 1}`}>
            <img src={p.thumbUrl} alt="" />
            <span>{i + 1}</span>
          </button>
        ))}
        <button class="thumb add" aria-label="Ajouter une page" onClick={() => setSheet('add')}>
          <IconPlus />
        </button>
      </div>

      {tab === 'image' && (
        <nav class="bottombar">
          <button class="tool" disabled={!page} onClick={recrop}>
            <IconCrop />
            Recadrer
          </button>
          <button class="tool" disabled={!page} onClick={() => page && rerender(page, { rotation: nextRotation(page.rotation) }, 'Rotation…')}>
            <IconRotate />
            Pivoter
          </button>
          <button class="tool" disabled={!page} onClick={() => setSheet('filter')}>
            <IconFilter />
            Filtre
          </button>
          <button class="tool" disabled={!page} onClick={() => setSheet('page')}>
            <IconMore />
            Page
          </button>
        </nav>
      )}

      {sheet === 'filter' && page && (
        <Sheet title="Filtre" onClose={() => setSheet(null)}>
          {FILTERS.map((f) => (
            <button
              key={f}
              class={f === page.filter ? 'btn primary' : 'btn'}
              onClick={() => {
                setSheet(null);
                if (f !== page.filter) rerender(page, { filter: f }, 'Filtre…');
              }}
            >
              {FILTER_LABELS[f]}
            </button>
          ))}
        </Sheet>
      )}

      {sheet === 'page' && page && (
        <Sheet title={`Page ${index + 1} sur ${doc.pages.length}`} onClose={() => setSheet(null)}>
          <div class="row">
            <button class="btn" disabled={index === 0} onClick={() => move(-1)}>
              <IconLeft /> Avancer
            </button>
            <button class="btn" disabled={index === doc.pages.length - 1} onClick={() => move(1)}>
              Reculer <IconRight />
            </button>
          </div>
          <button class="btn danger" onClick={removePage}>
            <IconTrash /> Supprimer la page
          </button>
        </Sheet>
      )}

      {sheet === 'add' && (
        <Sheet title="Ajouter une page" onClose={() => setSheet(null)}>
          <button class="btn primary" onClick={() => add('camera')}>
            <IconCamera /> Appareil photo
          </button>
          <button class="btn" onClick={() => add('library')}>
            <IconImport /> Photothèque
          </button>
        </Sheet>
      )}

      {sheet === 'rename' && (
        <PromptSheet
          title="Renommer"
          value={doc.title}
          onClose={() => setSheet(null)}
          onSubmit={(title) => {
            setSheet(null);
            onChange({ ...doc, title, dirty: true });
          }}
        />
      )}

      {sheet === 'export' && <ExportSheet doc={doc} setOcr={setOcr} onClose={() => setSheet(null)} />}
    </div>
  );
}
