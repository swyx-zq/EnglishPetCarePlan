import { render, screen } from '@testing-library/react'

import IndexPage from './index'

describe('IndexPage', () => {
  it('shows the confirmed bilingual product name and visual direction', () => {
    render(<IndexPage />)

    expect(screen.getByText('英语养宠计划')).toBeInTheDocument()
    expect(screen.getByText('English Pet Care Plan')).toBeInTheDocument()
    expect(screen.getByText('学一点英语，照顾好一个生命。')).toBeInTheDocument()
    expect(screen.getByText('状态变化清晰可解释')).toBeInTheDocument()
  })
})
