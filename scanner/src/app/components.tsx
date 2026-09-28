import type { ComponentChildren } from 'preact';
import { useEffect, useRef, useState } from 'preact/hooks';

/** Feuille d'actions qui monte du bas de l'écran ; un toucher à côté la ferme. */
export function Sheet({ title, onClose, children }: { title?: string; onClose: () => void; children: ComponentChildren }) {
  return (
    <div class="sheet-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div class="sheet" role="dialog" aria-label={title}>
        {title && <h2>{title}</h2>}
        {children}
        <button class="btn" onClick={onClose}>
          Annuler
        </button>
      </div>
    </div>
  );
}

/** Feuille avec un champ texte (renommer). */
export function PromptSheet({ title, value, onSubmit, onClose }: { title: string; value: string; onSubmit: (v: string) => void; onClose: () => void }) {
  const [v, setV] = useState(value);
  const input = useRef<HTMLInputElement>(null);
  useEffect(() => {
    input.current?.focus();
    input.current?.select();
  }, []);
  const submit = () => {
    const t = v.trim();
    if (t) onSubmit(t);
  };
  return (
    <Sheet title={title} onClose={onClose}>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
      >
        <input ref={input} value={v} onInput={(e) => setV((e.target as HTMLInputElement).value)} enterKeyHint="done" />
      </form>
      <button class="btn primary" onClick={submit} disabled={!v.trim()}>
        OK
      </button>
    </Sheet>
  );
}

/** Demande une ou plusieurs photos : appareil photo (capture) ou photothèque. */
export function pickImages(mode: 'camera' | 'library'): Promise<File[]> {
  return new Promise((resolve) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.className = 'hidden-input';
    if (mode === 'camera') input.setAttribute('capture', 'environment');
    else input.multiple = true;
    const done = (files: File[]) => {
      input.remove();
      resolve(files);
    };
    input.addEventListener('change', () => done([...(input.files ?? [])]));
    input.addEventListener('cancel', () => done([]));
    document.body.appendChild(input);
    input.click();
  });
}
