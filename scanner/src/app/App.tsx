import { useEffect, useState } from 'preact/hooks';
import { api } from './api';
import { IconCamera, IconImport } from './icons';

export function App() {
  const [who, setWho] = useState('');
  useEffect(() => {
    api.me().then((r) => setWho(r.email), (e: Error) => setWho(e.message));
  }, []);
  return (
    <div class="screen">
      <header class="topbar">
        <h1>Documents</h1>
      </header>
      <main class="content">
        <p class="empty">Aucun document pour l’instant.</p>
        <p class="status">{who}</p>
      </main>
      <div class="fab-row">
        <button class="btn big" disabled>
          <IconImport /> Importer
        </button>
        <button class="btn big primary" disabled>
          <IconCamera /> Scanner
        </button>
      </div>
    </div>
  );
}
