import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'

const releaseMode = process.argv.includes('--release')
const baselinePath = new URL('../security/production-audit-baseline.json', import.meta.url)
const baseline = JSON.parse(readFileSync(baselinePath, 'utf8'))
const audit = spawnSync('npm', ['audit', '--omit=dev', '--json'], {
  encoding: 'utf8',
  stdio: ['ignore', 'pipe', 'pipe'],
})

if (audit.error) {
  throw new Error(`无法执行 npm audit: ${audit.error.message}`)
}

let report

try {
  report = JSON.parse(audit.stdout)
} catch {
  const detail = audit.stderr.trim() || audit.stdout.trim() || '未收到审计报告'
  throw new Error(`无法解析 npm audit 报告：${detail}`)
}

const counts = report.metadata?.vulnerabilities

if (!counts) {
  throw new Error('npm audit 报告缺少漏洞统计信息')
}

const limits = releaseMode ? baseline.releaseMaximum : baseline.maximum
const exceeded = Object.entries(limits).filter(([severity, maximum]) => {
  return (counts[severity] ?? 0) > maximum
})
const mode = releaseMode ? '发布门槛' : '回归基线'

console.log(`生产依赖审计（${mode}）：${JSON.stringify(counts)}`)

if (exceeded.length > 0) {
  const message = exceeded
    .map(([severity, maximum]) => `${severity}=${counts[severity] ?? 0}，上限=${maximum}`)
    .join('；')
  throw new Error(`生产依赖审计未通过：${message}`)
}
