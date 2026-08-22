import { Button, Text, View } from '@tarojs/components'

import './index.scss'

export default function IndexPage() {
  return (
    <View className="welcome-page">
      <View className="welcome-brand" aria-label="英语养宠计划标识">
        <View aria-hidden="true" className="welcome-brand-mark">
          <View className="welcome-brand-ear welcome-brand-ear-left" />
          <View className="welcome-brand-ear welcome-brand-ear-right" />
          <View className="welcome-brand-face">
            <View className="welcome-brand-eyes">
              <View className="welcome-brand-eye" />
              <View className="welcome-brand-eye" />
            </View>
            <View className="welcome-brand-smile" />
          </View>
          <View className="welcome-brand-book">
            <View className="welcome-brand-book-page welcome-brand-book-page-left" />
            <View className="welcome-brand-book-page welcome-brand-book-page-right" />
          </View>
        </View>
        <View className="welcome-brand-name">
          <Text className="welcome-product-name">英语养宠计划</Text>
          <Text className="welcome-product-name-en">English Pet Care Plan</Text>
        </View>
      </View>

      <View aria-labelledby="welcome-title" className="welcome-main" role="main">
        <View className="welcome-hero-card">
          <Text className="welcome-eyebrow">一起慢慢学英语</Text>
          <View aria-level={1} className="welcome-title" id="welcome-title" role="heading">
            欢迎，和 Momo 建立一段安心的陪伴。
          </View>
          <Text className="welcome-description">
            短暂离开不会失去 Momo。每一组学习、每一次互动，都只在服务端确认后才会被记录。
          </Text>
          <View aria-label="Momo 的静态欢迎场景" className="welcome-momo-scene" role="img">
            <View aria-hidden="true" className="welcome-momo-moon" />
            <View aria-hidden="true" className="welcome-momo-cat">
              <View className="welcome-momo-ear welcome-momo-ear-left" />
              <View className="welcome-momo-ear welcome-momo-ear-right" />
              <View className="welcome-momo-face">
                <View className="welcome-momo-eyes">
                  <View className="welcome-momo-eye" />
                  <View className="welcome-momo-eye" />
                </View>
                <View className="welcome-momo-smile" />
              </View>
            </View>
          </View>
        </View>

        <View aria-labelledby="welcome-promises-title" className="welcome-promises">
          <View
            aria-level={2}
            className="welcome-section-title"
            id="welcome-promises-title"
            role="heading"
          >
            先把这些安心的话说清楚
          </View>
          <View className="welcome-promise-list" role="list">
            <View className="welcome-promise" role="listitem">
              <Text aria-hidden="true" className="welcome-promise-icon">
                ♡
              </Text>
              <View className="welcome-promise-copy">
                <Text className="welcome-promise-title">离开不会失去 Momo</Text>
                <Text className="welcome-promise-description">
                  Momo 会在安全的空间等你，记忆和关系都会保留。
                </Text>
              </View>
            </View>
            <View className="welcome-promise" role="listitem">
              <Text aria-hidden="true" className="welcome-promise-icon">
                ✓
              </Text>
              <View className="welcome-promise-copy">
                <Text className="welcome-promise-title">基础互动始终免费</Text>
                <Text className="welcome-promise-description">
                  喂食、补水、整理和重逢不扣积分，也不需要购买。
                </Text>
              </View>
            </View>
            <View className="welcome-promise" role="listitem">
              <Text aria-hidden="true" className="welcome-promise-icon">
                ◌
              </Text>
              <View className="welcome-promise-copy">
                <Text className="welcome-promise-title">陪伴声可以随时关闭</Text>
                <Text className="welcome-promise-description">
                  未来有轻声陪伴时，你仍可在“我的”中关闭声音或减少动态效果。
                </Text>
              </View>
            </View>
          </View>
        </View>

        <View className="welcome-next-step-card">
          <Text className="welcome-next-step-title">准备好后，再从今天开始。</Text>
          <Text className="welcome-next-step-description" id="welcome-login-description">
            登录与领养服务接入后，Momo 的名字、学习和陪伴记录才会安全地保存下来。
          </Text>
          <Button
            aria-disabled="true"
            aria-describedby="welcome-login-description"
            className="welcome-primary-button"
            data-testid="welcome-adoption-action"
            disabled
          >
            登录并领养 Momo
          </Button>
          <Text className="welcome-service-note">服务连接准备中，暂不创建演示账户或虚构记录。</Text>
        </View>
      </View>
    </View>
  )
}
