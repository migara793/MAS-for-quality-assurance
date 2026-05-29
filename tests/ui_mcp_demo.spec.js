const { test, expect } = require('@playwright/test');
const path = require('path');

test('System can interact with UI elements', async ({ page }) => {
  const filePath = `file://${path.resolve(__dirname, 'ui_test_demo.html')}`;
  await page.goto(filePath);
  await expect(page.locator('#title')).toHaveText('UI Tester App');
  await expect(page.locator('#result')).toBeHidden();
  await page.fill('#test-input', 'MCP_UI_TEST_SUCCESS');
  await page.click('#action-btn');
  await expect(page.locator('#result')).toBeVisible();
  await expect(page.locator('#output-text')).toHaveText('MCP_UI_TEST_SUCCESS');
});
