import { render, screen } from '@testing-library/react'
import { vi } from 'vitest'

import { TodayPage } from './TodayPage'
import { readyTodayFixture } from './TodayPage.test-fixtures'

describe('TodayPage', () => {
  it('renders only values supplied by the authoritative view model', () => {
    const onPrimaryAction = vi.fn()

    render(<TodayPage onPrimaryAction={onPrimaryAction} state={readyTodayFixture} />)

    expect(screen.getByRole('heading', { name: '今日' })).toBeInTheDocument()
    expect(screen.getByText('Momo')).toBeInTheDocument()
    expect(screen.getByTestId('care-state-banner')).toHaveAccessibleName('陪伴状态：正常陪伴')
    expect(screen.getByRole('progressbar', { name: '今日学习额度' })).toHaveAttribute(
      'aria-valuetext',
      '1/3 组已确认',
    )
    expect(screen.getByText('24 分')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '开始背词' })).toBeEnabled()
  })

  it('renders a non-submittable loading state while the authority is synchronising', () => {
    render(<TodayPage state={{ kind: 'loading' }} />)

    expect(screen.getByText('正在同步 Momo 的近况')).toBeInTheDocument()
    expect(screen.getByRole('main')).toHaveAttribute('aria-busy', 'true')
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('does not invent pet history when the authority reports no pet', () => {
    render(
      <TodayPage
        state={{
          kind: 'empty',
          title: '还没有 Momo',
          message: '登录并完成领养后，学习和陪伴记录会从这里出现。',
          actionLabel: '去领养',
          actionDescription: '领养服务连接后可用。',
        }}
      />,
    )

    expect(screen.getByText('还没有 Momo')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '去领养' })).toBeDisabled()
    expect(screen.queryByTestId('care-state-banner')).not.toBeInTheDocument()
  })

  it('offers a supplied retry path without exposing internal diagnostics', () => {
    const onRetry = vi.fn()

    render(
      <TodayPage
        onRetry={onRetry}
        state={{
          kind: 'error',
          title: '暂时无法同步',
          message: '请检查网络后重试，已确认的记录不会丢失。',
          retryLabel: '重新同步',
        }}
      />,
    )

    expect(screen.getByRole('alert')).toHaveTextContent('请检查网络后重试')
    expect(screen.getByRole('button', { name: '重新同步' })).toBeEnabled()
  })
})
