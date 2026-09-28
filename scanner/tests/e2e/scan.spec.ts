import { expect, test } from '@playwright/test';
import { photoSynthetique } from './helpers';

test('scanner une page : photo → coins → éditeur, puis filtre et rotation', async ({ page }) => {
  const photo = await photoSynthetique(page);
  await page.goto('/');

  const chooser = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: /Scanner/ }).click();
  await (await chooser).setFiles({ name: 'photo.jpg', mimeType: 'image/jpeg', buffer: photo });

  await expect(page.getByRole('heading', { name: 'Ajuster les coins' })).toBeVisible({ timeout: 60_000 });
  await expect(page.getByText('Bords non trouvés')).toHaveCount(0);
  await page.screenshot({ path: 'test-results/coins.png' });
  await page.getByRole('button', { name: /Valider/ }).click();

  const img = page.getByRole('img', { name: 'Page 1' });
  await expect(img).toBeVisible({ timeout: 60_000 });
  const ratio = await img.evaluate((i: HTMLImageElement) => i.naturalHeight / i.naturalWidth);
  // Page A4 redressée : hauteur / largeur ≈ 1,41.
  expect(ratio).toBeGreaterThan(1.3);
  expect(ratio).toBeLessThan(1.52);

  await page.getByRole('button', { name: /Pivoter/ }).click();
  await expect(async () => {
    const r = await page.getByRole('img', { name: 'Page 1' }).evaluate((i: HTMLImageElement) => i.naturalHeight / i.naturalWidth);
    expect(r).toBeLessThan(1);
  }).toPass({ timeout: 30_000 });

  await page.getByRole('button', { name: /Filtre/ }).click();
  await page.getByRole('button', { name: 'Noir et blanc' }).click();
  await expect(page.locator('.busy')).toHaveCount(0, { timeout: 30_000 });
  await page.screenshot({ path: 'test-results/editeur.png' });

  // Ajout d'une 2e page depuis la photothèque.
  await page.getByRole('button', { name: 'Ajouter une page' }).click();
  const chooser2 = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: /Photothèque/ }).click();
  await (await chooser2).setFiles({ name: 'photo2.jpg', mimeType: 'image/jpeg', buffer: photo });
  await expect(page.getByRole('button', { name: 'Page 2' })).toBeVisible({ timeout: 60_000 });
});
