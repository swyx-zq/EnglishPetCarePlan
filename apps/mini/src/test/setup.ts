import '@testing-library/jest-dom/vitest'
import { vi } from 'vitest'

vi.mock('@tarojs/components', () => ({
  Text: 'span',
  View: 'div',
}))
