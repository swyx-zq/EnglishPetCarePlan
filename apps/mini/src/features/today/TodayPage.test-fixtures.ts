import type { TodayViewState } from './types'

export const readyTodayFixture: TodayViewState = {
  kind: 'ready',
  viewModel: {
    pet: {
      name: 'Momo',
      careState: 'normal',
      careStateLabel: '正常陪伴',
      careMessage: 'Momo 正在安静陪伴。',
      lastInteractionLabel: '最近互动：由服务端同步',
      sceneDescription: 'Momo 坐在窗边的静态陪伴场景',
    },
    learning: {
      completedGroups: 1,
      totalGroups: 3,
      progressPercent: 33,
      progressLabel: '1/3 组已确认',
      availabilityMessage: '剩余额度以服务端结果为准。',
    },
    points: {
      availableLabel: '24 分',
      description: '仅展示服务端确认的可用积分。',
    },
    nextAction: {
      label: '开始背词',
      description: '完成结果需要服务端确认后才会记录积分。',
    },
    latestMemory: '这是一条由服务端返回的共同记忆。',
  },
}
