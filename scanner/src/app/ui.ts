// Petits signaux globaux d'interface : indicateur d'activité et messages éphémères.
import { useEffect, useState } from 'preact/hooks';

export interface BusyState {
  message: string;
  progress?: number; // 0–1
}
export interface Toast {
  message: string;
  action?: { label: string; run: () => void };
}

type Listener = () => void;
let busy: BusyState | null = null;
let toastState: Toast | null = null;
let toastTimer: ReturnType<typeof setTimeout> | undefined;
const listeners = new Set<Listener>();
const emit = () => listeners.forEach((l) => l());

export function setBusy(b: BusyState | null) {
  busy = b;
  emit();
}

export function toast(message: string, action?: Toast['action'], ms = 4000) {
  toastState = { message, action };
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toastState = null;
    emit();
  }, ms);
  emit();
}

export function dismissToast() {
  toastState = null;
  emit();
}

/** Exécute `fn` sous l'indicateur d'activité ; affiche l'erreur éventuelle. */
export async function withBusy<T>(message: string, fn: (progress: (p: number, msg?: string) => void) => Promise<T>): Promise<T | undefined> {
  setBusy({ message });
  // Laisse le navigateur peindre l'indicateur avant un calcul qui bloque le fil principal.
  await new Promise((r) => requestAnimationFrame(() => setTimeout(r, 0)));
  try {
    return await fn((p, msg) => setBusy({ message: msg ?? message, progress: p }));
  } catch (err) {
    console.error(err);
    toast(err instanceof Error ? err.message : String(err));
    return undefined;
  } finally {
    setBusy(null);
  }
}

export function useUi() {
  const [, force] = useState(0);
  useEffect(() => {
    const l = () => force((n) => n + 1);
    listeners.add(l);
    return () => listeners.delete(l);
  }, []);
  return { busy, toast: toastState };
}
