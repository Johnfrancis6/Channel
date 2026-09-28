// Fabrique de vrais JWT RS256 signés par une clé de test, et un faux JWKS.
import { env } from 'cloudflare:test';
import { createApp, type Env } from '../../src/worker/index';
import type { Jwk, KeyFetcher } from '../../src/worker/access';

export const ISSUER = 'https://equipe-test.cloudflareaccess.com';
export const AUD = 'aud-test';

const enc = (o: unknown) => b64url(new TextEncoder().encode(JSON.stringify(o)));
function b64url(bytes: Uint8Array): string {
  let s = '';
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

export async function makeSigner(kid = 'cle-1') {
  const pair = (await crypto.subtle.generateKey(
    { name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' },
    true,
    ['sign', 'verify'],
  )) as CryptoKeyPair;
  const pub = (await crypto.subtle.exportKey('jwk', pair.publicKey)) as Jwk;
  const jwk: Jwk = { ...pub, kid };
  async function sign(payload: Record<string, unknown>, header: Record<string, unknown> = {}) {
    const h = enc({ alg: 'RS256', typ: 'JWT', kid, ...header });
    const p = enc(payload);
    const sig = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', pair.privateKey, new TextEncoder().encode(`${h}.${p}`));
    return `${h}.${p}.${b64url(new Uint8Array(sig))}`;
  }
  return { jwk, sign };
}

export function validClaims(over: Record<string, unknown> = {}) {
  const now = Math.floor(Date.now() / 1000);
  return { iss: ISSUER, aud: [AUD], email: 'moi@example.com', sub: 'u1', iat: now, nbf: now, exp: now + 3600, ...over };
}

/** App + fonction `api()` authentifiée par défaut. */
export async function setup(envOver: Partial<Env> = {}) {
  const signer = await makeSigner();
  const keys: KeyFetcher = async () => [signer.jwk];
  const app = createApp({ getKeys: keys });
  const token = await signer.sign(validClaims());
  const testEnv = { ...env, ...envOver } as Env;
  async function api(path: string, init: RequestInit & { auth?: string | null } = {}) {
    const headers = new Headers(init.headers);
    const auth = init.auth === undefined ? token : init.auth;
    if (auth) headers.set('Cf-Access-Jwt-Assertion', auth);
    return app.request(`https://scanner.example.workers.dev/api${path}`, { ...init, headers }, testEnv);
  }
  return { app, api, signer, token };
}
