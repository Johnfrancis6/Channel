import { Hono } from 'hono';
import { AccessError, fetchAccessKeys, verifyAccessJwt, type KeyFetcher } from './access';

export interface Env {
  DB: D1Database;
  FILES: R2Bucket;
  ASSETS: Fetcher;
  ACCESS_TEAM_DOMAIN?: string;
  ACCESS_AUD?: string;
  /** Liste d'e-mails séparés par des virgules (facultatif). */
  ACCESS_ALLOWED_EMAILS?: string;
  /** « 1 » dans .dev.vars : pas de vérification, et seulement sur localhost. */
  ACCESS_DEV_BYPASS?: string;
}

export type AppEnv = { Bindings: Env; Variables: { email: string } };

export interface AppDeps {
  getKeys?: KeyFetcher;
}

const LOCAL_HOSTS = new Set(['localhost', '127.0.0.1', '[::1]']);

export function createApp(deps: AppDeps = {}) {
  const getKeys = deps.getKeys ?? fetchAccessKeys;
  const app = new Hono<AppEnv>().basePath('/api');

  // Toutes les routes de l'API exigent un jeton Access valide.
  app.use('*', async (c, next) => {
    c.header('Cache-Control', 'no-store');
    const env = c.env;
    const host = new URL(c.req.url).hostname;
    if (env.ACCESS_DEV_BYPASS === '1' && LOCAL_HOSTS.has(host)) {
      c.set('email', 'dev@localhost');
      return next();
    }
    if (!env.ACCESS_TEAM_DOMAIN || !env.ACCESS_AUD) {
      return c.json({ error: 'Cloudflare Access non configuré sur le Worker' }, 503);
    }
    const token = c.req.header('Cf-Access-Jwt-Assertion');
    if (!token) return c.json({ error: 'authentification requise' }, 401);
    try {
      const id = await verifyAccessJwt(
        token,
        {
          teamDomain: env.ACCESS_TEAM_DOMAIN,
          aud: env.ACCESS_AUD,
          allowedEmails: (env.ACCESS_ALLOWED_EMAILS ?? '')
            .split(',')
            .map((e) => e.trim())
            .filter(Boolean),
        },
        getKeys,
      );
      c.set('email', id.email);
    } catch (err) {
      if (err instanceof AccessError) return c.json({ error: `accès refusé : ${err.message}` }, 401);
      throw err;
    }
    return next();
  });

  app.get('/me', (c) => c.json({ email: c.get('email') }));

  app.notFound((c) => c.json({ error: 'route inconnue' }, 404));
  app.onError((err, c) => {
    console.error(err);
    return c.json({ error: 'erreur interne' }, 500);
  });
  return app;
}

const app = createApp();

export default {
  fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === '/api' || url.pathname.startsWith('/api/')) {
      return app.fetch(request, env, ctx);
    }
    return env.ASSETS.fetch(request);
  },
} satisfies ExportedHandler<Env>;
