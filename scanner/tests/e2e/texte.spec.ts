import { expect, test } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { photoSynthetique } from './helpers';

test('onglet Texte : OCR, correction d’une ligne, export TXT et PDF', async ({ page }) => {
  const photo = await photoSynthetique(page);
  await page.goto('/');

  const chooser = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: /Scanner/ }).click();
  await (await chooser).setFiles({ name: 'photo.jpg', mimeType: 'image/jpeg', buffer: photo });
  await expect(page.getByRole('heading', { name: 'Ajuster les coins' })).toBeVisible({ timeout: 60_000 });
  await page.getByRole('button', { name: /Valider/ }).click();
  await expect(page.getByRole('img', { name: 'Page 1' })).toBeVisible({ timeout: 60_000 });

  // L'OCR démarre tout seul à l'ouverture de l'onglet.
  await page.getByRole('tab', { name: /Texte/ }).click();
  const lines = page.locator('textarea.line');
  await expect(lines.first()).toBeVisible({ timeout: 120_000 });
  await expect(lines.first()).toHaveValue(/Facture/);
  expect(await page.locator('.text-image rect').count()).toBe(await lines.count());

  // Toucher un cadre sur l'image sélectionne la ligne correspondante.
  const box = (await page.locator('.text-image rect').nth(2).boundingBox())!;
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
  await expect(lines.nth(2)).toHaveClass(/selected/);

  // Correction d'une ligne, puis export texte : la correction doit y figurer.
  await lines.first().fill('Facture corrigée à la main');
  await page.screenshot({ path: 'test-results/texte.png' });

  // Titre sans accent : le Chromium du conteneur de test ignore un nom de téléchargement accentué
  // (sur iPhone, l'export passe par la feuille de partage, pas par ce téléchargement).
  await page.locator('.title-button').click();
  await page.getByRole('dialog').locator('input').fill('Facture chaudiere');
  await page.getByRole('dialog').locator('input').press('Enter');

  await page.getByRole('button', { name: 'Exporter' }).click();
  await page.getByRole('button', { name: /Texte \(\.txt\)/ }).click();
  let dl = page.waitForEvent('download');
  await page.getByRole('button', { name: /Partager/ }).click();
  const txtDl = await dl;
  expect(txtDl.suggestedFilename()).toBe('Facture chaudiere.txt');
  const txt = readFileSync((await txtDl.path())!, 'utf8');
  expect(txt).toContain('Facture corrigée à la main');
  expect(txt).toContain('septembre 2026');

  // Export PDF : toutes les pages ont déjà leur texte, pas de question posée.
  await page.locator('.sheet-backdrop').click({ position: { x: 5, y: 5 } });
  await page.getByRole('button', { name: 'Exporter' }).click();
  await page.getByRole('button', { name: /PDF/ }).click();
  dl = page.waitForEvent('download');
  await page.getByRole('button', { name: /Partager/ }).click();
  const download = await dl;
  expect(download.suggestedFilename()).toBe('Facture chaudiere.pdf');
  const pdf = readFileSync((await download.path())!);
  expect(pdf.subarray(0, 5).toString()).toBe('%PDF-');
});
