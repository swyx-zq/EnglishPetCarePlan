import { expect, test } from '@playwright/test'

test('shows the bilingual product brand on the H5 entry page', async ({ page }) => {
  await page.goto('/')

  const brand = page.getByLabel('英语养宠计划标识')

  await expect(brand).toContainText('英语养宠计划')
  await expect(brand).toContainText('English Pet Care Plan')
  await expect(page.getByText('学一点英语，照顾好一个生命。')).toBeVisible()
})
