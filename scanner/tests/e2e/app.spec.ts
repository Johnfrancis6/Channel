import { expect, test } from '@playwright/test';

test('la coquille de l’app s’affiche', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Documents' })).toBeVisible();
  await expect(page.getByRole('button', { name: /Scanner/ })).toBeVisible();
});
