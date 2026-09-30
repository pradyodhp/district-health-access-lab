// Accessibility audit: axe-core on each workbench section. Fails on serious/critical issues.
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const SECTIONS = ['Case & evidence', 'Model & runs', 'Sensitivity & research', 'Memo'];

test('landing page has no serious accessibility violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();
  const bad = results.violations.filter((v) => ['serious', 'critical'].includes(v.impact));
  expect(bad.map((v) => `${v.id}: ${v.nodes.length} nodes`)).toEqual([]);
});

for (const name of SECTIONS) {
  test(`workbench section "${name}" has no serious violations`, async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: 'Decision workbench' }).click();
    await page.getByRole('button', { name, exact: true }).click();
    const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();
    const bad = results.violations.filter((v) => ['serious', 'critical'].includes(v.impact));
    expect(bad.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(' ')).slice(0, 3).join(' | ')}`)).toEqual([]);
  });
}
