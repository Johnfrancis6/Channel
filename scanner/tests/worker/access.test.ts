import { describe, expect, it } from 'vitest';
import { normalizeIssuer, verifyAccessJwt } from '../../src/worker/access';
import { AUD, makeSigner, setup, validClaims } from './helpers';

describe('normalizeIssuer', () => {
  it('accepte le nom d’équipe, le domaine ou l’URL', () => {
    expect(normalizeIssuer('moi')).toBe('https://moi.cloudflareaccess.com');
    expect(normalizeIssuer('moi.cloudflareaccess.com')).toBe('https://moi.cloudflareaccess.com');
    expect(normalizeIssuer('https://moi.cloudflareaccess.com/')).toBe('https://moi.cloudflareaccess.com');
  });
});

describe('verifyAccessJwt', () => {
  const cfg = { teamDomain: 'equipe-test', aud: AUD };

  it('accepte un jeton valide et renvoie l’e-mail', async () => {
    const s = await makeSigner();
    const id = await verifyAccessJwt(await s.sign(validClaims()), cfg, async () => [s.jwk]);
    expect(id.email).toBe('moi@example.com');
  });

  it('accepte un aud en chaîne simple', async () => {
    const s = await makeSigner();
    await expect(verifyAccessJwt(await s.sign(validClaims({ aud: AUD })), cfg, async () => [s.jwk])).resolves.toBeTruthy();
  });

  const refus: [string, Record<string, unknown>, RegExp][] = [
    ['expiré', { exp: Math.floor(Date.now() / 1000) - 3600 }, /expiré/],
    ['mauvaise audience', { aud: ['autre'] }, /audience/],
    ['mauvais émetteur', { iss: 'https://pirate.cloudflareaccess.com' }, /émetteur/],
    ['pas encore valide', { nbf: Math.floor(Date.now() / 1000) + 3600 }, /pas encore/],
  ];
  for (const [nom, claims, msg] of refus) {
    it(`refuse un jeton ${nom}`, async () => {
      const s = await makeSigner();
      await expect(verifyAccessJwt(await s.sign(validClaims(claims)), cfg, async () => [s.jwk])).rejects.toThrow(msg);
    });
  }

  it('refuse une signature d’une autre clé portant le même kid', async () => {
    const vrai = await makeSigner('k');
    const faux = await makeSigner('k');
    await expect(verifyAccessJwt(await faux.sign(validClaims()), cfg, async () => [vrai.jwk])).rejects.toThrow(/signature/);
  });

  it('refuse alg=none et les jetons mal formés', async () => {
    const s = await makeSigner();
    await expect(verifyAccessJwt(await s.sign(validClaims(), { alg: 'none' }), cfg, async () => [s.jwk])).rejects.toThrow(/algorithme/);
    await expect(verifyAccessJwt('abc', cfg, async () => [s.jwk])).rejects.toThrow(/mal formé/);
  });

  it('recharge les clés quand le kid est inconnu (rotation)', async () => {
    const s = await makeSigner('nouvelle');
    const appels: boolean[] = [];
    const id = await verifyAccessJwt(await s.sign(validClaims()), cfg, async (_iss, force) => {
      appels.push(force);
      return force ? [s.jwk] : [];
    });
    expect(id.email).toBe('moi@example.com');
    expect(appels).toEqual([false, true]);
  });

  it('applique la liste d’e-mails autorisés', async () => {
    const s = await makeSigner();
    const t = await s.sign(validClaims());
    await expect(verifyAccessJwt(t, { ...cfg, allowedEmails: ['MOI@example.com'] }, async () => [s.jwk])).resolves.toBeTruthy();
    await expect(verifyAccessJwt(t, { ...cfg, allowedEmails: ['autre@example.com'] }, async () => [s.jwk])).rejects.toThrow(/non autorisé/);
  });
});

describe('middleware Access', () => {
  it('401 sans en-tête', async () => {
    const { api } = await setup();
    expect((await api('/me', { auth: null })).status).toBe(401);
  });

  it('401 avec un jeton invalide', async () => {
    const { api } = await setup();
    expect((await api('/me', { auth: 'a.b.c' })).status).toBe(401);
  });

  it('200 avec un jeton valide', async () => {
    const { api } = await setup();
    const res = await api('/me');
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ email: 'moi@example.com' });
    expect(res.headers.get('Cache-Control')).toBe('no-store');
  });

  it('503 (échec fermé) si Access n’est pas configuré', async () => {
    const { api } = await setup({ ACCESS_AUD: '' });
    expect((await api('/me')).status).toBe(503);
  });

  it('le contournement de dev ne marche que sur localhost', async () => {
    const { app } = await setup({ ACCESS_DEV_BYPASS: '1' });
    const { env } = await import('cloudflare:test');
    const e = { ...env, ACCESS_DEV_BYPASS: '1' };
    expect((await app.request('https://scanner.example.workers.dev/api/me', {}, e)).status).toBe(401);
    expect((await app.request('http://localhost:8787/api/me', {}, e)).status).toBe(200);
  });

  it('404 JSON sur une route inconnue (après authentification)', async () => {
    const { api } = await setup();
    expect((await api('/nexiste-pas')).status).toBe(404);
    expect((await api('/nexiste-pas', { auth: null })).status).toBe(401);
  });
});
