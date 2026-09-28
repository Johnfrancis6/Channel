// Écran d'ajustement des 4 coins, au doigt, avec loupe.
import { useEffect, useLayoutEffect, useRef, useState } from 'preact/hooks';
import type { Point, Quad } from '../shared/types';
import { clampQuad, fullImageQuad, isUsableQuad } from '../scan/geometry';
import { IconCheck, IconExpand, IconWand } from './icons';

interface Props {
  source: HTMLCanvasElement;
  /** URL de la même image (blob:), plus légère à afficher qu'un export du canvas. */
  imageUrl: string;
  initial: Quad;
  found: boolean;
  title?: string;
  onCancel: () => void;
  onDone: (q: Quad) => void;
  onAuto: () => Promise<{ quad: Quad; found: boolean }>;
}

const LOUPE = 132;
const ZOOM = 2.5;

export function CornerEditor({ source, imageUrl, initial, found, title = 'Ajuster les coins', onCancel, onDone, onAuto }: Props) {
  const stageRef = useRef<HTMLDivElement>(null);
  const loupeRef = useRef<HTMLCanvasElement>(null);
  const [quad, setQuad] = useState<Quad>(initial);
  const [box, setBox] = useState({ scale: 1, left: 0, top: 0 });
  const [active, setActive] = useState<number | null>(null);
  const [notFound, setNotFound] = useState(!found);
  const drag = useRef<{ i: number; start: Point; corner: Point } | null>(null);

  // Ajuste l'image à la zone disponible, avec une marge pour attraper les coins au bord.
  useLayoutEffect(() => {
    const el = stageRef.current!;
    const fit = () => {
      const pad = 28;
      const W = el.clientWidth - pad * 2;
      const H = el.clientHeight - pad * 2;
      const scale = Math.min(W / source.width, H / source.height);
      setBox({ scale, left: (el.clientWidth - source.width * scale) / 2, top: (el.clientHeight - source.height * scale) / 2 });
    };
    fit();
    const ro = new ResizeObserver(fit);
    ro.observe(el);
    return () => ro.disconnect();
  }, [source]);

  const valid = isUsableQuad(quad, source.width, source.height, 0.01);

  function drawLoupe(q: Quad, i: number) {
    const c = loupeRef.current;
    if (!c) return;
    const g = c.getContext('2d')!;
    const p = q[i]!;
    const k = box.scale * ZOOM; // pixels loupe par pixel source
    const half = LOUPE / 2 / k;
    g.fillStyle = '#000';
    g.fillRect(0, 0, LOUPE, LOUPE);
    g.drawImage(source, p.x - half, p.y - half, half * 2, half * 2, 0, 0, LOUPE, LOUPE);
    // Les deux bords qui partent de ce coin.
    g.strokeStyle = '#38bdf8';
    g.lineWidth = 2;
    for (const j of [(i + 1) % 4, (i + 3) % 4]) {
      const n = q[j]!;
      g.beginPath();
      g.moveTo(LOUPE / 2, LOUPE / 2);
      g.lineTo(LOUPE / 2 + (n.x - p.x) * k, LOUPE / 2 + (n.y - p.y) * k);
      g.stroke();
    }
    g.strokeStyle = '#fff';
    g.lineWidth = 1;
    g.beginPath();
    g.moveTo(LOUPE / 2 - 10, LOUPE / 2);
    g.lineTo(LOUPE / 2 + 10, LOUPE / 2);
    g.moveTo(LOUPE / 2, LOUPE / 2 - 10);
    g.lineTo(LOUPE / 2, LOUPE / 2 + 10);
    g.stroke();
  }

  useEffect(() => {
    if (active !== null) drawLoupe(quad, active);
  }, [active, quad]);

  function onDown(i: number, e: PointerEvent) {
    e.preventDefault();
    (e.currentTarget as Element).setPointerCapture(e.pointerId);
    drag.current = { i, start: { x: e.clientX, y: e.clientY }, corner: { ...quad[i]! } };
    setActive(i);
  }

  function onMove(e: PointerEvent) {
    const d = drag.current;
    if (!d) return;
    e.preventDefault();
    // Déplacement relatif : le doigt n'a pas besoin d'être pile sur le coin (il le cacherait).
    const x = d.corner.x + (e.clientX - d.start.x) / box.scale;
    const y = d.corner.y + (e.clientY - d.start.y) / box.scale;
    const next = [...quad] as Quad;
    next[d.i] = { x, y };
    setQuad(clampQuad(next, source.width, source.height));
  }

  function onUp() {
    drag.current = null;
    setActive(null);
  }

  const pts = quad.map((p) => `${p.x * box.scale},${p.y * box.scale}`).join(' ');
  // Loupe du côté opposé au coin déplacé, pour ne pas être sous le doigt.
  const loupeLeft = active !== null && quad[active]!.x * box.scale + box.left < (stageRef.current?.clientWidth ?? 0) / 2;

  return (
    <div class="screen corner-screen">
      <header class="topbar">
        <button class="btn ghost" onClick={onCancel}>
          Annuler
        </button>
        <h1 class="center">{title}</h1>
        <span style={{ width: 80 }} />
      </header>
      <div class="stage" ref={stageRef} onPointerMove={onMove} onPointerUp={onUp} onPointerCancel={onUp}>
        <img src={imageUrl} alt="" draggable={false} style={{ left: box.left, top: box.top, width: source.width * box.scale, height: source.height * box.scale }} />
        <svg class="quad" style={{ left: box.left, top: box.top, width: source.width * box.scale, height: source.height * box.scale }}>
          <polygon points={pts} class={valid ? '' : 'invalid'} />
          {quad.map((p, i) => (
            <g key={i} transform={`translate(${p.x * box.scale} ${p.y * box.scale})`} onPointerDown={(e) => onDown(i, e)}>
              <circle r="30" class="hit" />
              <circle r={active === i ? 6 : 13} class="handle" />
            </g>
          ))}
        </svg>
        <canvas ref={loupeRef} class="loupe" width={LOUPE} height={LOUPE} hidden={active === null} style={loupeLeft ? { right: 12 } : { left: 12 }} />
        {notFound && <p class="hint">Bords non trouvés : place les coins à la main.</p>}
      </div>
      <nav class="bottombar">
        <button class="tool" onClick={() => setQuad(fullImageQuad(source.width, source.height))}>
          <IconExpand />
          Tout
        </button>
        <button
          class="tool"
          onClick={async () => {
            const r = await onAuto();
            setQuad(r.quad);
            setNotFound(!r.found);
          }}
        >
          <IconWand />
          Auto
        </button>
        <button class="btn primary big" disabled={!valid} onClick={() => onDone(quad)}>
          <IconCheck /> Valider
        </button>
      </nav>
    </div>
  );
}
