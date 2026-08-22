import { render, screen } from '@testing-library/react'

import IndexPage from './index'

describe('IndexPage', () => {
  it('explains the Beta reassurance boundaries before login and adoption are available', () => {
    render(<IndexPage />)

    expect(
      screen.getByRole('heading', { name: '欢迎，和 Momo 建立一段安心的陪伴。' }),
    ).toBeInTheDocument()
    expect(screen.getByText('离开不会失去 Momo')).toBeInTheDocument()
    expect(screen.getByText('基础互动始终免费')).toBeInTheDocument()
    expect(screen.getByText('陪伴声可以随时关闭')).toBeInTheDocument()
  })

  it('does not create a demonstration account before the login service is connected', () => {
    render(<IndexPage />)

    expect(screen.getByTestId('welcome-adoption-action')).toBeDisabled()
    expect(screen.getByTestId('welcome-adoption-action')).toHaveAttribute('aria-disabled', 'true')
    expect(screen.getByText('服务连接准备中，暂不创建演示账户或虚构记录。')).toBeInTheDocument()
  })
})
