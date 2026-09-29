// Export du document : PDF cherchable ou texte brut, partagé via la feuille de partage d'iOS.
import { useState } from 'preact/hooks';
import type { OcrResult } from '../shared/types';
import { buildPdf } from '../export/pdf';
import { buildTxt, fileName } from '../export/txt';
import { api } from './api';
import { Sheet } from './components';
import type { DocState } from './doc';
import { IconShare } from './icons';
import { runOcr } from './TextPanel';
import { toast } from './ui';

interface Props {
  doc: DocState;
  setOcr: (pageId: string, ocr: OcrResult, forUrl?: string) => void;
  onClose: () => void;
}

export function download(file: File) {
  const url = URL.createObjectURL(file);
  const a = document.createElement('a');
  a.href = url;
  a.download = file.name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

export async function shareOrDownload(file: File, title: string) {
  if (navigator.canShare?.({ files: [file] })) {
    try {
      await navigator.share({ files: [file], title });
      return;
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') return; // partage annulé
    }
  }
  download(file);
}

export function ExportSheet({ doc, setOcr, onClose }: Props) {
  const [status, setStatus] = useState<{ msg: string; p: number } | null>(null);
  const [ready, setReady] = useState<File | null>(null);

  /** OCR des pages qui n'en ont pas encore (le PDF n'est cherchable que sur les pages reconnues). */
  async function ensureOcr(): Promise<(OcrResult | null)[]> {
    const out: (OcrResult | null)[] = [];
    const missing = doc.pages.filter((p) => !p.ocr).length;
    let n = 0;
    for (const p of doc.pages) {
      if (p.ocr) {
        out.push(p.ocr);
        continue;
      }
      n++;
      const r = await runOcr(doc.id, p, (x, s) => setStatus({ msg: `${s} (page ${n}/${missing})`, p: x }));
      setOcr(p.id, r, p.processedUrl);
      out.push(r);
    }
    return out;
  }

  async function makePdf() {
    try {
      const missing = doc.pages.filter((p) => !p.ocr).length;
      const withOcr = missing === 0 || confirm(`${missing} page${missing > 1 ? 's n’ont' : ' n’a'} pas encore de texte reconnu. Lancer l’OCR pour que le PDF soit cherchable ?\n(Annuler : PDF image seule pour ces pages.)`);
      const ocrs = withOcr ? await ensureOcr() : doc.pages.map((p) => p.ocr);
      const inputs = [];
      for (const [i, p] of doc.pages.entries()) {
        setStatus({ msg: `Préparation de la page ${i + 1}/${doc.pages.length}…`, p: i / doc.pages.length });
        const blob = p.processed ?? (await api.getFile(doc.id!, p.id, 'processed'));
        inputs.push({ image: new Uint8Array(await blob.arrayBuffer()), type: p.processedType, width: p.width, height: p.height, ocr: ocrs[i] ?? null });
      }
      setStatus({ msg: 'Création du PDF…', p: 1 });
      const bytes = await buildPdf(inputs, doc.title);
      setReady(new File([bytes as BlobPart], fileName(doc.title, 'pdf'), { type: 'application/pdf' }));
    } catch (err) {
      console.error(err);
      toast(`Export impossible : ${err instanceof Error ? err.message : err}`);
    } finally {
      setStatus(null);
    }
  }

  async function makeTxt() {
    try {
      const ocrs = await ensureOcr();
      setReady(new File([buildTxt(doc.title, ocrs)], fileName(doc.title, 'txt'), { type: 'text/plain;charset=utf-8' }));
    } catch (err) {
      toast(`Export impossible : ${err instanceof Error ? err.message : err}`);
    } finally {
      setStatus(null);
    }
  }

  return (
    <Sheet title="Exporter" onClose={onClose}>
      {status ? (
        <div class="ocr-progress">
          <p>{status.msg}</p>
          <div class="progress">
            <div style={{ width: `${Math.round(status.p * 100)}%` }} />
          </div>
        </div>
      ) : ready ? (
        <>
          <p class="small">
            {ready.name} — {(ready.size / 1024 / 1024).toFixed(1)} Mo
          </p>
          {/* Deuxième toucher volontaire : iOS n'autorise le partage qu'en réponse directe à un geste. */}
          <button class="btn primary" onClick={() => shareOrDownload(ready, doc.title)}>
            <IconShare /> Partager / Enregistrer
          </button>
        </>
      ) : (
        <>
          <button class="btn primary" onClick={makePdf}>
            PDF (texte cherchable)
          </button>
          <button class="btn" onClick={makeTxt}>
            Texte (.txt)
          </button>
          <button class="btn" disabled>
            Word (.docx) — V2
          </button>
        </>
      )}
    </Sheet>
  );
}
