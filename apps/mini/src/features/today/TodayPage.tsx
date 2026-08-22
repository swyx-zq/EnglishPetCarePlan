import { Button, Text, View } from '@tarojs/components'

import type { TodayPageProps } from './types'

import './TodayPage.scss'

export function TodayPage({ state, onEmptyAction, onPrimaryAction, onRetry }: TodayPageProps) {
  if (state.kind === 'loading') {
    return (
      <View
        aria-busy="true"
        aria-labelledby="today-title"
        className="today-page today-page-loading"
        role="main"
      >
        <View aria-level={1} className="today-heading" id="today-title" role="heading">
          今日
        </View>
        <View className="today-sync-card">
          <View aria-hidden="true" className="today-scene-placeholder" />
          <Text className="today-sync-message">正在同步 Momo 的近况</Text>
          <Text className="today-sync-description">同步完成前不会展示或提交照料操作。</Text>
        </View>
      </View>
    )
  }

  if (state.kind === 'empty') {
    const isActionAvailable = Boolean(onEmptyAction)

    return (
      <View aria-labelledby="today-title" className="today-page" role="main">
        <View aria-level={1} className="today-heading" id="today-title" role="heading">
          今日
        </View>
        <View className="today-empty-card">
          <Text aria-hidden="true" className="today-empty-icon">
            ○
          </Text>
          <Text className="today-empty-title">{state.title}</Text>
          <Text className="today-empty-message">{state.message}</Text>
          <Text className="today-action-description" id="today-empty-action-description">
            {state.actionDescription}
          </Text>
          <Button
            aria-describedby="today-empty-action-description"
            className="today-primary-button"
            disabled={!isActionAvailable}
            onClick={onEmptyAction}
          >
            {state.actionLabel}
          </Button>
        </View>
      </View>
    )
  }

  if (state.kind === 'error') {
    const isRetryAvailable = Boolean(onRetry)

    return (
      <View aria-labelledby="today-title" className="today-page" role="main">
        <View aria-level={1} className="today-heading" id="today-title" role="heading">
          今日
        </View>
        <View className="today-error-card" role="alert">
          <Text aria-hidden="true" className="today-error-icon">
            !
          </Text>
          <Text className="today-error-title">{state.title}</Text>
          <Text className="today-error-message">{state.message}</Text>
          <Button className="today-secondary-button" disabled={!isRetryAvailable} onClick={onRetry}>
            {state.retryLabel}
          </Button>
        </View>
      </View>
    )
  }

  const { learning, latestMemory, nextAction, pet, points } = state.viewModel
  const isActionAvailable = Boolean(onPrimaryAction) && !nextAction.disabled

  return (
    <View aria-labelledby="today-title" className="today-page" role="main">
      <View aria-level={1} className="today-heading" id="today-title" role="heading">
        今日
      </View>
      <View className="today-pet-card">
        <View
          aria-label={pet.sceneDescription}
          className="today-pet-scene"
          data-care-state={pet.careState}
          role="img"
        >
          <View aria-hidden="true" className="today-pet-sun" />
          <View aria-hidden="true" className="today-pet-cat">
            <View className="today-pet-ear today-pet-ear-left" />
            <View className="today-pet-ear today-pet-ear-right" />
            <View className="today-pet-face">
              <View className="today-pet-eyes">
                <View className="today-pet-eye" />
                <View className="today-pet-eye" />
              </View>
              <View className="today-pet-smile" />
            </View>
          </View>
        </View>
        <View className="today-pet-copy">
          <Text className="today-pet-name">{pet.name}</Text>
          <View
            aria-label={`陪伴状态：${pet.careStateLabel}`}
            className="today-care-banner"
            data-testid="care-state-banner"
          >
            <Text aria-hidden="true" className="today-care-icon">
              ●
            </Text>
            <View className="today-care-copy">
              <Text className="today-care-label">{pet.careStateLabel}</Text>
              <Text className="today-care-message">{pet.careMessage}</Text>
            </View>
          </View>
          <Text className="today-last-interaction">{pet.lastInteractionLabel}</Text>
        </View>
      </View>

      <View className="today-overview-grid">
        <View className="today-overview-card">
          <Text className="today-overview-label">今日学习</Text>
          <Text className="today-overview-value">{learning.progressLabel}</Text>
          <View
            aria-label="今日学习额度"
            aria-valuemax={learning.totalGroups}
            aria-valuemin={0}
            aria-valuenow={learning.completedGroups}
            aria-valuetext={learning.progressLabel}
            className="today-progress"
            role="progressbar"
          >
            <View
              className="today-progress-fill"
              style={{
                width: `${learning.progressPercent}%`,
              }}
            />
          </View>
          <Text className="today-overview-description">{learning.availabilityMessage}</Text>
        </View>
        <View className="today-overview-card">
          <Text className="today-overview-label">可用积分</Text>
          <Text className="today-overview-value">{points.availableLabel}</Text>
          <Text className="today-overview-description">{points.description}</Text>
        </View>
      </View>

      <View className="today-action-card">
        <Text className="today-action-eyebrow">现在可以做什么</Text>
        <Text className="today-action-title">{nextAction.label}</Text>
        <Text className="today-action-description" id="today-primary-action-description">
          {nextAction.description}
        </Text>
        <Button
          aria-describedby="today-primary-action-description"
          className="today-primary-button"
          disabled={!isActionAvailable}
          onClick={onPrimaryAction}
        >
          {nextAction.label}
        </Button>
      </View>

      <View className="today-memory-card">
        <Text className="today-memory-label">最近的共同记忆</Text>
        <Text className="today-memory-copy">{latestMemory}</Text>
      </View>
    </View>
  )
}
