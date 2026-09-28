// Client de l'API /api/* (même origine ; le cookie Cloudflare Access suit tout seul).
import type { DocumentDetail, DocumentSummary, FileKind, PageMeta } from '../shared/types';

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}
/** La session Access a expiré : il faut recharger la page pour se reconnecter. */
export class SessionExpiredError extends Error {
  constructor() {
    super('Session expirée — recharge l’app pour te reconnecter.');
  }
}
export class OfflineError extends Error {
  constructor() {
    super('Pas de réseau.');
  }
}

async function call(path: string, init: RequestInit = {}): Promise<Response> {
  let res: Response;
  try {
    // redirect: 'manual' : une session Access expirée répond par une redirection vers
    // la page de connexion ; on la détecte au lieu de la suivre (elle échouerait en CORS).
    res = await fetch(`/api${path}`, { credentials: 'same-origin', redirect: 'manual', ...init });
  } catch {
    throw new OfflineError();
  }
  if (res.type === 'opaqueredirect' || res.status === 401 || res.status === 403) {
    throw new SessionExpiredError();
  }
  if (!res.ok) {
    let msg = `Erreur ${res.status}`;
    try {
      msg = ((await res.json()) as { error?: string }).error ?? msg;
    } catch {
      /* corps non JSON */
    }
    throw new ApiError(msg, res.status);
  }
  return res;
}

const json = (body: unknown): RequestInit => ({
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
});

export const api = {
  me: async () => (await (await call('/me')).json()) as { email: string },

  list: async (q = '') =>
    (await (await call(`/documents${q ? `?q=${encodeURIComponent(q)}` : ''}`)).json()) as {
      documents: DocumentSummary[];
    },

  get: async (id: string) => (await (await call(`/documents/${id}`)).json()) as DocumentDetail,

  create: async (title: string) =>
    (await (await call('/documents', { method: 'POST', ...json({ title }) })).json()) as { id: string },

  rename: async (id: string, title: string) => {
    await call(`/documents/${id}`, { method: 'PATCH', ...json({ title }) });
  },

  remove: async (id: string) => {
    await call(`/documents/${id}`, { method: 'DELETE' });
  },

  putPages: async (id: string, pages: PageMeta[]) => {
    await call(`/documents/${id}/pages`, { method: 'PUT', ...json({ pages }) });
  },

  putFile: async (id: string, pageId: string, kind: FileKind, blob: Blob) => {
    await call(`/documents/${id}/pages/${pageId}/${kind}`, {
      method: 'PUT',
      headers: { 'Content-Type': blob.type || 'image/jpeg' },
      body: blob,
    });
  },

  fileUrl: (id: string, pageId: string, kind: FileKind) => `/api/documents/${id}/pages/${pageId}/${kind}`,

  getFile: async (id: string, pageId: string, kind: FileKind) =>
    (await call(`/documents/${id}/pages/${pageId}/${kind}`)).blob(),
};
