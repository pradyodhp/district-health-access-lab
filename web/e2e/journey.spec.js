// Primary journey: evidence gate -> hypothetical run -> run-backed memo.
// Asserts honesty labels survive the full UI path; no district estimate may appear.
import { test, expect } from '@playwright/test';

test('evidence to run to memo keeps the decision on hold', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Decision workbench' }).click();

  // Case & evidence: the gate is visible before any run.
  await expect(page.getByText(/REAL DECISION: HOLD/)).toBeVisible();
  await expect(page.getByText('OBSERVED_UNVERIFIED').first()).toBeVisible();

  // Model & runs: execute a seeded hypothetical run.
  await page.getByRole('button', { name: 'Model & runs' }).click();
  await page.getByRole('button', { name: 'Run reproducible model' }).click();
  await expect(page.getByText(/SAVED LOCAL RUN \/ run-/)).toBeVisible({ timeout: 30000 });
  await expect(page.getByText(/HYPOTHETICAL/).first()).toBeVisible();

  // Replay verification from the stored snapshot.
  await page.getByRole('button', { name: 'Verify replay' }).click();
  await expect(page.getByText(/reproduced from the stored snapshot/)).toBeVisible({ timeout: 30000 });

  // Memo: generated from the frozen run, still a hold, never a district estimate.
  await page.getByRole('button', { name: 'Memo', exact: true }).click();
  await page.getByRole('button', { name: 'Generate memo from run' }).click();
  await expect(page.getByText(/DECISION ON HOLD/).first()).toBeVisible({ timeout: 30000 });
  await expect(page.getByText('What we do not know')).toBeVisible();
});

test('API failure surfaces an error instead of an invented zero', async ({ page }) => {
  await page.route('**/api/readiness', (route) => route.abort());
  await page.goto('/');
  await page.getByRole('button', { name: 'Decision workbench' }).click();
  // The workbench must not render a fabricated readiness score of 0 as if real.
  await expect(page.getByText(/REAL DECISION: HOLD \(/)).toBeVisible();
});
