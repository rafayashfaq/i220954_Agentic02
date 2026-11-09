import { test, expect } from '@playwright/test';

test.describe('GigBid End-to-End User Journeys', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to local frontend URL
    await page.goto('http://localhost:3000');
  });

  test('1. Onboarding & Persona Selection', async ({ page }) => {
    // Switch to Onboarding view
    await page.getByRole('button', { name: /Settings/i }).click();
    await expect(page.getByText('System Settings & Memory')).toBeVisible();

    // Verify persona selector in navbar
    const personaSelect = page.locator('select');
    await expect(personaSelect).toBeVisible();
    await personaSelect.selectOption('fullstack_dev');
    await expect(personaSelect).toHaveValue('fullstack_dev');
  });

  test('2. Inspecting Evidence Hover & Approving a Proposal', async ({ page }) => {
    // Click on Draft Proposal for first job
    const draftButton = page.getByRole('button', { name: /Draft Proposal/i }).first();
    await draftButton.click();

    // Verify Proposal Studio opened
    await expect(page.getByText('Evidence-Grounded Proposal Draft')).toBeVisible();

    // Verify evidence hover elements exist
    const evidenceUnderlines = page.locator('.cursor-help');
    await expect(evidenceUnderlines.first()).toBeVisible();

    // Click Approve & Submit
    const approveBtn = page.getByRole('button', { name: /Approve & Submit/i });
    await expect(approveBtn).toBeVisible();
    await approveBtn.click();

    // Confirm success message appears
    await expect(page.getByText(/Submitted successfully to GigSim/i)).toBeVisible();
  });

  test('3. Editing a Draft and Saving to Style Memory', async ({ page }) => {
    // Open studio
    await page.getByRole('button', { name: /Draft Proposal/i }).first().click();
    await expect(page.getByText('Evidence-Grounded Proposal Draft')).toBeVisible();

    // Click Edit Draft
    await page.getByRole('button', { name: /Edit Draft/i }).click();

    // Modify text in textarea
    const textarea = page.locator('textarea');
    await textarea.fill('Edited custom opening: Built production microservices with 99.99% uptime.');

    // Save and submit
    const submitEditsBtn = page.getByRole('button', { name: /Save Edits & Submit/i });
    await expect(submitEditsBtn).toBeVisible();
    await submitEditsBtn.click();

    await expect(page.getByText(/Edits saved to Style Memory/i)).toBeVisible();
  });

  test('4. Rejecting a Proposal with Reason', async ({ page }) => {
    // Open studio
    await page.getByRole('button', { name: /Draft Proposal/i }).first().click();

    // Click Reject Bid
    await page.getByRole('button', { name: /Reject Bid/i }).click();

    // Modal appears
    await expect(page.getByText('Reject Proposal Submission')).toBeVisible();
    await page.locator('textarea').fill('Budget ceiling is below minimum hourly floor.');

    // Confirm rejection
    await page.getByRole('button', { name: /Confirm Rejection/i }).click();
    await expect(page.getByText(/Proposal rejected/i)).toBeVisible();
  });

  test('5. Degraded Mode Warning Banner & Recovery', async ({ page }) => {
    // Click Degraded Mode toggle in navbar
    const toggleBtn = page.getByRole('button', { name: /GigSim OK/i });
    await toggleBtn.click();

    // Degraded mode alert banner should now be visible
    const alertBanner = page.getByText(/Marketplace Degraded Mode Active/i);
    await expect(alertBanner).toBeVisible();

    // Click restore
    await page.getByRole('button', { name: /Restore Normal Service/i }).click();
    await expect(alertBanner).not.toBeVisible();
  });
});

