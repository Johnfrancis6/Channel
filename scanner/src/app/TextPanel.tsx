// Onglet Texte : OCR de la page, cadres des lignes sur l'image, texte modifiable ligne par ligne.
// Toucher un cadre sélectionne la ligne ; toucher une ligne met son cadre en évidence.
import { useEffect, useRef, useState } from 'preact/hooks';
import type { OcrLine, OcrResult } from '../shared/types';
import { lineAt, ocrToText } from '../ocr/text';
import { recognize } from '../ocr/ocr';
import { api } from './api';
import type { DocState, PageState } from './doc';
import { IconCopy, IconWand } from './icons';
import { toast } from './ui';

interface Props {
  doc: DocState;
  page: PageState;
  /**
   * Remplace l'OCR de la page `pageId` dans l'état le plus récent du document.
   * `forUrl` : image sur laquelle l'OCR a tourné ; ignoré si la page a été recalculée depuis.
   */
  setOcr: (pageId: string, ocr: OcrResult, forUrl?: string) => void;
}

export async function runOcr(docId: string | null, page: PageState, onProgress?: (p: number, s: string) => void): Promise<OcrResult> {
  const blob = page.processed ?? (docId ? await api.getFile(docId, page.id, 'processed') : null);
  if (!blob) throw new Error('Image de la page introuvable');
  return recognize(blob, page.width, page.height, onProgress);
}

function AutoTextarea({ value, onInput, onFocus, selected, low }: { value: string; onInput: (v: string) => void; onFocus: () => void; selected: boolean; low: boolean }) {
  const ref = useRef<HTMLTextAreaElement>(null);
  useEffect(() => {
    const t = ref.current!;
    t.style.height = 'auto';
    t.style.height = `${t.scrollHeight}px`;
  }, [value]);
  return (
    <textarea
      ref={ref}
      rows={1}
      class={`line${selected ? ' selected' : ''}${low ? ' low' : ''}`}
      value={value}
      spellcheck
      lang="fr"
      onInput={(e) => onInput((e.target as HTMLTextAreaElement).value)}
      onFocus={onFocus}
    />
  );
}

export function TextPanel({ doc, page, setOcr }: Props) {
  const [progress, setProgress] = useState<{ p: number; s: string } | null>(null);
  const [error, setError] = useState('');
  const [sel, setSel] = useState(-1);
  const listRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const alive = useRef(true);
  const ocr = page.ocr;

  async function run() {
    setError('');
    setProgress({ p: 0, s: 'Préparation…' });
    try {
      const result = await runOcr(doc.id, page, (p, s) => alive.current && setProgress({ p, s }));
      setOcr(page.id, result, page.processedUrl);
      if (alive.current && !result.lines.length) toast('Aucun texte trouvé sur cette page.');
    } catch (err) {
      console.error(err);
      if (alive.current) setError(err instanceof Error ? err.message : String(err));
    } finally {
      if (alive.current) setProgress(null);
    }
  }

  useEffect(() => {
    alive.current = true;
    if (!page.ocr) run();
    return () => {
      alive.current = false;
    };
  }, [page.id]);

  function select(i: number, scroll: boolean) {
    setSel(i);
    if (scroll) listRef.current?.querySelectorAll('textarea')[i]?.scrollIntoView({ block: 'center', behavior: 'smooth' });
  }

  function onTapImage(e: MouseEvent) {
    if (!ocr || !svgRef.current) return;
    const svg = svgRef.current;
    const pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    const p = pt.matrixTransform(svg.getScreenCTM()!.inverse());
    const i = lineAt(ocr.lines, p.x, p.y);
    if (i >= 0) select(i, true);
  }

  function editLine(i: number, text: string) {
    if (!ocr) return;
    const lines: OcrLine[] = ocr.lines.map((l, j) => (j === i ? { ...l, text } : l));
    setOcr(page.id, { ...ocr, lines });
  }

  async function copyAll() {
    try {
      await navigator.clipboard.writeText(ocrToText(ocr));
      toast('Texte copié');
    } catch {
      toast('Copie impossible');
    }
  }

  return (
    <main class="text-panel">
      <div class="text-image">
        <img src={page.processedUrl} alt={`Page`} />
        {ocr && (
          <svg ref={svgRef} viewBox={`0 0 ${ocr.width} ${ocr.height}`} preserveAspectRatio="xMidYMid meet" onClick={onTapImage}>
            {ocr.lines.map((l, i) => (
              <rect key={i} x={l.bbox[0]} y={l.bbox[1]} width={l.bbox[2] - l.bbox[0]} height={l.bbox[3] - l.bbox[1]} class={i === sel ? 'sel' : l.confidence < 60 ? 'low' : ''} />
            ))}
          </svg>
        )}
      </div>

      <div class="text-lines" ref={listRef}>
        {progress ? (
          <div class="ocr-progress">
            <p>{progress.s}</p>
            <div class="progress">
              <div style={{ width: `${Math.round(progress.p * 100)}%` }} />
            </div>
            <p class="small">La première fois, le modèle français (~1 Mo) et le moteur OCR (~4 Mo) se téléchargent.</p>
          </div>
        ) : error ? (
          <div class="empty">
            <p>OCR impossible : {error}</p>
            <button class="btn" onClick={run}>
              Réessayer
            </button>
          </div>
        ) : ocr && !ocr.lines.length ? (
          <p class="empty">Aucun texte reconnu sur cette page.</p>
        ) : (
          ocr?.lines.map((l, i) => (
            <AutoTextarea key={i} value={l.text} selected={i === sel} low={l.confidence < 60} onFocus={() => select(i, false)} onInput={(v) => editLine(i, v)} />
          ))
        )}
      </div>

      <nav class="bottombar">
        <button class="tool" disabled={!ocr?.lines.length} onClick={copyAll}>
          <IconCopy />
          Copier le texte
        </button>
        <button
          class="tool"
          disabled={!!progress}
          onClick={() => (!ocr?.lines.length || confirm('Relancer la reconnaissance ? Tes corrections sur cette page seront perdues.')) && run()}
        >
          <IconWand />
          Refaire l’OCR
        </button>
      </nav>
    </main>
  );
}
