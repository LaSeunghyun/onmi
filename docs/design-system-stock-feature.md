# Design System: 주식 신호·알림 기능 (Design System Architect 협업)

## 1. Product Context Summary
- **Product type**: 모바일 앱(Expo) 중심의 개인 투자 보조 도구.
- **Target audience**: 1인 개인 투자자, 매수/매도 타이밍 알림·공시 요약 확인.
- **Brand personality**: 신뢰형·전문형(금융 데이터, 규칙 기반 신호).
- **Platform**: Mobile (iOS/Android), 기존 touch 앱 탭 구조 내 통합.
- **Interaction complexity**: 중 (리스트·정렬·상세·설정·푸시).
- **Trust level**: 금융 데이터 표시·접근성·명확한 상태 전달 필요.

## 2. Reference Analysis Summary
- **Material / Apple HIG**: 카드·리스트·상태 배지·세미포닉 색상 일관 사용.
- **Polaris / Atlassian**: 테이블·필터·설정 폼 밀도, 토큰 기반 spacing.
- **WCAG**: 색상만 의존 금지, 대비 4.5:1, 터치 44pt 최소.
- **Reusable principles**: Semantic 색상(성공/경고/오류/정보), 8px 베이스, 상태별 아이콘+텍스트 병행.

## 3. Design Philosophy
- 기존 `@/theme/tokens` 확장으로 일관성 유지.
- 신호·공시 감성은 **semantic 색상 + 라벨 텍스트**로만 전달하지 않고 **아이콘+텍스트** 병행.
- 카드·버튼·입력은 기존 radius/space 재사용, 새 컴포넌트는 동일 규칙 적용.

## 4. Token Definitions (추가/확장)

기존 `theme/tokens`에 추가할 항목만 정의.

```ts
// 신호·공시 전용 시맨틱 (기존 color.success/error/warning 활용)
signal: {
  buy: color.success[600],   // 매수 후보
  sell: color.error[600],     // 매도 고려
  hold: color.neutral[600],   // 홀딩
},
disclosure: {
  positive: color.success[600],
  neutral: color.neutral[500],
  negative: color.error[600],
},
```

- **Typography**: 기존 `fontSize.xs`~`2xl`, `fontWeight` 그대로 사용. 카드 제목 `fontSize.lg` + `fontWeight.semibold`, 보조 `fontSize.sm` + `text.secondary`.
- **Spacing**: 기존 `space.1`~`8` 유지. 카드 패딩 `space.4`, 리스트 간격 `space.3`.
- **Motion**: 기존 `motion.fast/normal/slow`, 리스트 재정렬 시 `normal`.

## 5. Component Standards (주식 기능용)

| 컴포넌트 | States | Variants | A11y | 일관성 |
|----------|--------|----------|------|--------|
| **SignalBadge** | default | buy / sell / hold | 색+텍스트+아이콘, 44pt 터치 | semantic.signal |
| **DisclosureChip** | default | positive / neutral / negative | 색+텍스트 | semantic.disclosure |
| **WatchlistCard** | default, loading, error | - | 터치 영역 44pt, role="button" | 카드 radius.md, space.4 |
| **RuleInput** | default, focus, error, disabled | percent / number / toggle | label+value+에러메시지 | 기존 Input 패턴 |
| **OrderableList** | default, dragging | - | 드래그 핸들 접근성 라벨 | space.3 항목 간격 |

- **Button/Input/Card**: 기존 디자인 시스템 규칙 따름. Primary = 신호 액션, Secondary = 보조.
- **Feedback**: Toast/Alert는 기존 패턴; 공시 요약은 Modal/Sheet 내 텍스트+링크.

## 6. Accessibility Notes
- WCAG 2.1 AA: 본문 대비 4.5:1, 큰 텍스트 3:1.
- 신호/공시 상태: `accessibilityLabel`에 "매수 후보", "긍정 공시" 등 텍스트 포함.
- 터치 타겟 최소 44×44pt.
- Reduced motion: 기존 `motion.reduceMotion` 존중.

## 7. Implementation Guide
- **CSS 변수**: React Native에서는 `tokens.ts` export 유지, 필요 시 `ThemeContext`로 dark 대응.
- **Tailwind**: 웹 확장 시 `theme.extend.colors`에 `signal.*`, `disclosure.*` 매핑.
- **안티패턴**: 색상만으로 "매수/매도" 구분 금지. 라벨/아이콘 필수.
- **검증**: 신호 배지·공시 칩은 light/dark 모두 대비 검사.
