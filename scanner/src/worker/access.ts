// Vérification du jeton Cloudflare Access (en-tête Cf-Access-Jwt-Assertion).
// https://developers.cloudflare.com/cloudflare-one/identity/authorization-cookie/validating-json/

export interface AccessConfig {
  /** « equipe », « equipe.cloudflareaccess.com » ou l'URL complète. */
  teamDomain: string;
  /** Tag AUD de l'application Access. */
  aud: string;
  /** Si non vide, seuls ces e-mails sont acceptés (en plus de la politique Access). */
  allowedEmails?: string[];
}

export interface AccessIdentity {
  email: string;
  sub: string;
}

export type Jwk = JsonWebKey & { kid?: string };
/** Renvoie les clés publiques de l'équipe. `force` : ignorer le cache (rotation de clés). */
export type KeyFetcher = (issuer: string, force: boolean) => Promise<Jwk[]>;

export class AccessError extends Error {}

const LEEWAY_S = 60;
const KEYS_TTL_MS = 60 * 60 * 1000;

export function normalizeIssuer(teamDomain: string): string {
  let host = teamDomain.trim().replace(/^https?:\/\//, '').replace(/\/.*$/, '');
  if (!host.includes('.')) host = `${host}.cloudflareaccess.com`;
  return `https://${host}`;
}

const keyCache = new Map<string, { keys: Jwk[]; expires: number }>();

/** Récupère le JWKS de l'équipe, avec un cache d'une heure par isolat. */
export const fetchAccessKeys: KeyFetcher = async (issuer, force) => {
  const hit = keyCache.get(issuer);
  if (hit && !force && hit.expires > Date.now()) return hit.keys;
  const res = await fetch(`${issuer}/cdn-cgi/access/certs`);
  if (!res.ok) throw new AccessError(`JWKS indisponible (${res.status})`);
  const body = (await res.json()) as { keys?: Jwk[] };
  const keys = body.keys ?? [];
  keyCache.set(issuer, { keys, expires: Date.now() + KEYS_TTL_MS });
  return keys;
};

function b64urlToBytes(s: string): Uint8Array {
  const b64 = s.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - (s.length % 4)) % 4);
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function decodeJson(part: string): Record<string, unknown> {
  try {
    return JSON.parse(new TextDecoder().decode(b64urlToBytes(part)));
  } catch {
    throw new AccessError('jeton illisible');
  }
}

export async function verifyAccessJwt(
  token: string,
  config: AccessConfig,
  getKeys: KeyFetcher = fetchAccessKeys,
  nowS: number = Math.floor(Date.now() / 1000),
): Promise<AccessIdentity> {
  const parts = token.split('.');
  if (parts.length !== 3) throw new AccessError('jeton mal formé');
  const [h, p, s] = parts as [string, string, string];
  const header = decodeJson(h);
  const payload = decodeJson(p);
  if (header.alg !== 'RS256') throw new AccessError('algorithme refusé');

  const issuer = normalizeIssuer(config.teamDomain);
  let keys = await getKeys(issuer, false);
  let jwk = keys.find((k) => k.kid === header.kid);
  if (!jwk) {
    keys = await getKeys(issuer, true);
    jwk = keys.find((k) => k.kid === header.kid);
  }
  if (!jwk) throw new AccessError('clé inconnue');

  const key = await crypto.subtle.importKey(
    'jwk',
    { kty: jwk.kty, n: jwk.n, e: jwk.e, alg: 'RS256', ext: true },
    { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' },
    false,
    ['verify'],
  );
  const ok = await crypto.subtle.verify(
    'RSASSA-PKCS1-v1_5',
    key,
    b64urlToBytes(s),
    new TextEncoder().encode(`${h}.${p}`),
  );
  if (!ok) throw new AccessError('signature invalide');

  if (payload.iss !== issuer) throw new AccessError('émetteur inattendu');
  const aud = Array.isArray(payload.aud) ? payload.aud : [payload.aud];
  if (!aud.includes(config.aud)) throw new AccessError('audience inattendue');
  if (typeof payload.exp !== 'number' || payload.exp + LEEWAY_S < nowS) {
    throw new AccessError('jeton expiré');
  }
  if (typeof payload.nbf === 'number' && payload.nbf - LEEWAY_S > nowS) {
    throw new AccessError('jeton pas encore valide');
  }

  const email = typeof payload.email === 'string' ? payload.email : '';
  const allowed = (config.allowedEmails ?? []).map((e) => e.toLowerCase());
  if (allowed.length > 0 && !allowed.includes(email.toLowerCase())) {
    throw new AccessError('utilisateur non autorisé');
  }
  return { email, sub: String(payload.sub ?? '') };
}
