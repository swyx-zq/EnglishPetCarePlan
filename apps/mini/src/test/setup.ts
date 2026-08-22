import '@testing-library/jest-dom/vitest'
import { vi } from 'vitest'

vi.mock('@tarojs/components', () => ({
  Button: 'button',
  Text: 'span',
  View: 'div',
}))
