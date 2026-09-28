import type { DocState, PageState } from './doc';

export function TextPanel(_: { doc: DocState; page: PageState; onChange: (p: PageState) => void }) {
  return (
    <main class="content">
      <p class="empty">La reconnaissance du texte arrive à la phase 3.</p>
    </main>
  );
}
