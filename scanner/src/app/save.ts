// Enregistrement d'un document dans le cloud : fichiers modifiés d'abord, métadonnées ensuite.
// Ainsi, une coupure en cours de route ne laisse jamais une page pointer vers une image absente.
import { api } from './api';
import { pageMeta, type DocState } from './doc';

export async function saveDocument(doc: DocState, progress: (p: number) => void = () => {}): Promise<DocState> {
  let id = doc.id;
  if (!id) id = (await api.create(doc.title)).id;
  else await api.rename(id, doc.title);

  const uploads = doc.pages.flatMap((p) => p.dirty.map((kind) => ({ p, kind })));
  let done = 0;
  progress(0);
  for (const { p, kind } of uploads) {
    const blob = p[kind];
    if (!blob) throw new Error(`Fichier « ${kind} » manquant pour une page`);
    await api.putFile(id, p.id, kind, blob);
    progress(++done / (uploads.length + 1));
  }
  await api.putPages(id, doc.pages.map(pageMeta));
  progress(1);
  return { ...doc, id, dirty: false, pages: doc.pages.map((p) => ({ ...p, dirty: [] })) };
}
