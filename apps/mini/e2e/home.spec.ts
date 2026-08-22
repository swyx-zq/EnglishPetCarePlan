import { expect, test } from '@playwright/test'

test('shows the Beta welcome and reassurance boundaries without a demo account', async ({
  page,
}) => {
  await page.goto('/')

  await expect(page.getByLabel('英语养宠计划标识')).toContainText('英语养宠计划')
  await expect(
    page.getByRole('heading', { name: '欢迎，和 Momo 建立一段安心的陪伴。' }),
  ).toBeVisible()
  await expect(page.getByText('离开不会失去 Momo')).toBeVisible()
  await expect(page.getByText('基础互动始终免费')).toBeVisible()
  await expect(page.getByRole('button', { name: '登录并领养 Momo' })).toBeDisabled()
})
