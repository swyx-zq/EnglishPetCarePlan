/**
 * Read-only UI contract for the Today page.
 *
 * The API adapter will translate the versioned OpenAPI response into this
 * presentation model. Values in this type are already decided by the service;
 * UI components must not recalculate care status, learning eligibility, or
 * points.
 */
export type CareStateKey = 'normal' | 'reminder' | 'resting'

export interface TodayPetSnapshot {
  name: string
  careState: CareStateKey
  careStateLabel: string
  careMessage: string
  lastInteractionLabel: string
  sceneDescription: string
}

export interface TodayLearningSnapshot {
  completedGroups: number
  totalGroups: number
  progressPercent: number
  progressLabel: string
  availabilityMessage: string
}

export interface TodayPointsSnapshot {
  availableLabel: string
  description: string
}

export interface TodayNextAction {
  label: string
  description: string
  disabled?: boolean
}

export interface TodayAuthoritativeViewModel {
  pet: TodayPetSnapshot
  learning: TodayLearningSnapshot
  points: TodayPointsSnapshot
  nextAction: TodayNextAction
  latestMemory: string
}

export type TodayViewState =
  | { kind: 'loading' }
  | {
      kind: 'empty'
      title: string
      message: string
      actionLabel: string
      actionDescription: string
    }
  | {
      kind: 'error'
      title: string
      message: string
      retryLabel: string
    }
  | {
      kind: 'ready'
      viewModel: TodayAuthoritativeViewModel
    }

export interface TodayPageProps {
  state: TodayViewState
  onPrimaryAction?: () => void
  onEmptyAction?: () => void
  onRetry?: () => void
}
