import { useState } from 'preact/hooks';
import type { Quad } from '../shared/types';
import { pickImages } from './components';
import { CornerEditor } from './CornerEditor';
import { createPage, detect, emptyDoc, prepareSource, type DocState, type PageState, type Source } from './doc';
import { Editor } from './Editor';
import { Home } from './Home';
import { dismissToast, setBusy, toast, useUi, withBusy } from './ui';
import { saveDocument } from './save';

type View = { kind: 'home' } | { kind: 'editor'; doc: DocState };

interface CornerRequest {
  source: Source;
  url: string;
  quad: Quad;
  found: boolean;
  title: string;
  resolve: (q: Quad | null) => void;
}

export function App() {
  const [view, setView] = useState<View>({ kind: 'home' });
  const [corners, setCorners] = useState<CornerRequest | null>(null);
  const [saveState, setSaveState] = useState<'saved' | 'dirty' | 'saving' | 'error'>('dirty');
  const ui = useUi();

  /** Ouvre l'écran des coins et attend la validation (ou l'annulation). */
  function askCorners(source: Source, quad: Quad, found: boolean, title = 'Ajuster les coins'): Promise<Quad | null> {
    return new Promise((resolve) => {
      setCorners({ source, url: URL.createObjectURL(source.blob), quad, found, title, resolve });
    });
  }

  function closeCorners(q: Quad | null) {
    if (!corners) return;
    URL.revokeObjectURL(corners.url);
    corners.resolve(q);
    setCorners(null);
  }

  /** Photo(s) → détection → (coins) → pages traitées. */
  async function scanPages(mode: 'camera' | 'library'): Promise<PageState[]> {
    const files = await pickImages(mode);
    const pages: PageState[] = [];
    for (let i = 0; i < files.length; i++) {
      const label = files.length > 1 ? ` (${i + 1}/${files.length})` : '';
      const prep = await withBusy(`Analyse de la photo${label}…`, async (progress) => {
        const source = await prepareSource(files[i]!);
        progress(0.3, `Détection des bords${label}… (1er scan : chargement d’OpenCV)`);
        return { source, detection: await detect(source.canvas) };
      });
      if (!prep) continue;
      // Photo prise à l'instant : on montre toujours les coins. Import groupé : seulement si la détection a échoué.
      let quad: Quad | null = prep.detection.quad;
      if (mode === 'camera' || !prep.detection.found) {
        quad = await askCorners(prep.source, prep.detection.quad, prep.detection.found, files.length > 1 ? `Coins${label}` : undefined);
        if (!quad) continue;
      }
      const page = await withBusy(`Redressement${label}…`, () => createPage(prep.source, quad));
      if (page) pages.push(page);
    }
    return pages;
  }

  async function startScan(mode: 'camera' | 'library') {
    const pages = await scanPages(mode);
    if (pages.length) {
      setSaveState('dirty');
      setView({ kind: 'editor', doc: { ...emptyDoc(), pages } });
    }
  }

  async function save(doc: DocState): Promise<DocState | null> {
    setSaveState('saving');
    try {
      const saved = await saveDocument(doc, (p) => setBusy(p < 1 ? { message: 'Enregistrement…', progress: p } : null));
      setSaveState('saved');
      return saved;
    } catch (err) {
      setSaveState('error');
      toast(`Non enregistré : ${err instanceof Error ? err.message : err}`);
      return null;
    } finally {
      setBusy(null);
    }
  }

  let screen;
  if (view.kind === 'home') {
    screen = (
      <Home
        onScan={startScan}
        onOpen={(doc) => {
          setSaveState('saved');
          setView({ kind: 'editor', doc });
        }}
      />
    );
  } else {
    const doc = view.doc;
    screen = (
      <Editor
        doc={doc}
        onChange={(d) => {
          if (d.dirty) setSaveState('dirty');
          setView({ kind: 'editor', doc: d });
        }}
        addPages={scanPages}
        askCorners={(src, q, found) => askCorners(src, q, found, 'Recadrer')}
        saveState={saveState}
        onSave={async () => {
          const saved = await save(doc);
          if (saved) setView({ kind: 'editor', doc: saved });
        }}
        onClose={async () => {
          if (doc.dirty && doc.pages.length) {
            const saved = await save(doc);
            if (!saved && !confirm('L’enregistrement a échoué. Quitter quand même et perdre les modifications ?')) return;
          }
          setView({ kind: 'home' });
        }}
      />
    );
  }

  return (
    <>
      <div hidden={!!corners} style={{ height: '100%' }}>
        {screen}
      </div>
      {corners && (
        <CornerEditor
          source={corners.source.canvas}
          imageUrl={corners.url}
          initial={corners.quad}
          found={corners.found}
          title={corners.title}
          onCancel={() => closeCorners(null)}
          onDone={(q) => closeCorners(q)}
          onAuto={async () => (await withBusy('Détection…', () => detect(corners.source.canvas))) ?? { quad: corners.quad, found: false }}
        />
      )}
      {ui.busy && (
        <div class="busy" role="status">
          <div class="box">
            {ui.busy.message}
            {ui.busy.progress !== undefined && (
              <div class="progress">
                <div style={{ width: `${Math.round(ui.busy.progress * 100)}%` }} />
              </div>
            )}
          </div>
        </div>
      )}
      {ui.toast && (
        <div class="toast" role="alert" onClick={dismissToast}>
          <span style={{ flex: 1 }}>{ui.toast.message}</span>
          {ui.toast.action && (
            <button class="btn" onClick={ui.toast.action.run}>
              {ui.toast.action.label}
            </button>
          )}
        </div>
      )}
    </>
  );
}
