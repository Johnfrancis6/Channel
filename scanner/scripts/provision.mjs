// Crée la base D1 et le bucket R2 s'ils n'existent pas, puis écrit l'id de la base
// dans wrangler.toml (copie de travail de la CI uniquement). Idempotent.
// Requiert CLOUDFLARE_API_TOKEN et CLOUDFLARE_ACCOUNT_ID dans l'environnement.
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';

const root = join(dirname(new URL(import.meta.url).pathname), '..');
const tomlPath = join(root, 'wrangler.toml');
let toml = readFileSync(tomlPath, 'utf8');

const dbName = toml.match(/database_name\s*=\s*"([^"]+)"/)?.[1];
const bucket = toml.match(/bucket_name\s*=\s*"([^"]+)"/)?.[1];
if (!dbName || !bucket) throw new Error('database_name ou bucket_name introuvable dans wrangler.toml');

function wrangler(args) {
  return execFileSync('npx', ['wrangler', ...args], {
    cwd: root,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env, CI: 'true' },
  });
}

function listDatabases() {
  const out = wrangler(['d1', 'list', '--json']);
  return JSON.parse(out.slice(out.indexOf('[')));
}

// --- D1 ---
let db = listDatabases().find((d) => d.name === dbName);
if (!db) {
  console.log(`D1 : création de la base « ${dbName} »`);
  wrangler(['d1', 'create', dbName]);
  db = listDatabases().find((d) => d.name === dbName);
}
if (!db?.uuid) throw new Error(`D1 : base « ${dbName} » introuvable après création`);
console.log(`D1 : ${dbName} = ${db.uuid}`);
toml = toml.replace(/database_id\s*=\s*"[^"]*"/, `database_id = "${db.uuid}"`);
writeFileSync(tomlPath, toml);

// --- R2 ---
try {
  wrangler(['r2', 'bucket', 'info', bucket]);
  console.log(`R2 : bucket « ${bucket} » présent`);
} catch {
  console.log(`R2 : création du bucket « ${bucket} »`);
  wrangler(['r2', 'bucket', 'create', bucket]);
}
