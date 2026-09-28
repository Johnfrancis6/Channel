import { Sheet } from './components';
import type { DocState } from './doc';

export function ExportSheet({ onClose }: { doc: DocState; onChange: (d: DocState) => void; onClose: () => void }) {
  return (
    <Sheet title="Exporter" onClose={onClose}>
      <p class="empty">L’export PDF arrive à la phase 3.</p>
    </Sheet>
  );
}
