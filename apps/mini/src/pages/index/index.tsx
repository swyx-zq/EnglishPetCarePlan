import { Text, View } from '@tarojs/components'

import './index.scss'

export default function IndexPage() {
  return (
    <View className="page" aria-label="英语养宠计划首页">
      <View className="brand-row" aria-label="英语养宠计划标识">
        <View className="brand-mark" aria-hidden="true">
          <View className="brand-ear brand-ear-left" />
          <View className="brand-ear brand-ear-right" />
          <View className="brand-face">
            <View className="brand-eyes">
              <View className="brand-eye" />
              <View className="brand-eye" />
            </View>
            <View className="brand-smile" />
          </View>
          <View className="brand-book">
            <View className="brand-book-page brand-book-page-left" />
            <View className="brand-book-page brand-book-page-right" />
          </View>
        </View>
        <View className="brand-name">
          <Text className="product-name">英语养宠计划</Text>
          <Text className="product-name-en">English Pet Care Plan</Text>
        </View>
      </View>

      <View className="hero-card">
        <Text className="eyebrow">LEARN · CARE · GROW</Text>
        <Text className="title">学一点英语，照顾好一个生命。</Text>
        <Text className="description">
          每一次认真学习，都将变成可追溯的积分，帮助你按时照料宠物。
        </Text>
        <View className="principle-list" aria-label="产品原则">
          <View className="principle">
            <Text className="principle-label">学习</Text>
            <Text className="principle-text">完成任务才获得积分</Text>
          </View>
          <View className="principle">
            <Text className="principle-label principle-label-care">照料</Text>
            <Text className="principle-text">状态变化清晰可解释</Text>
          </View>
        </View>
      </View>
    </View>
  )
}
