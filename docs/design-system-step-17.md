# 1. Product Context Summary

- Product type: 모바일 뉴스 리포트 앱 + 운영자 어드민(웹)
- Target audience: 일반 사용자(빠른 정보 소비), 운영자(회원/모듈/감사로그 관리)
- Brand personality: 신뢰 기반 정보 서비스 + 운영 효율 중심 내부 도구
- Platform: React Native(앱), Expo Web(어드민)
- Interaction complexity: 사용자 앱은 중간(리포트/키워드/상세), 어드민은 중간~높음(운영 조작/상태 전환)
- Trust level: 계정/운영 조작이 포함되어 명확한 상태 표현, 오류 피드백, 접근성 준수가 필수

# 2. Reference Analysis Summary

검토 레퍼런스(8):
- Material 3: semantic color role, state layer, 컴포넌트 상태 일관성 강점 / 브랜드 차별화 약함
- Apple HIG: 타이포 위계, 여백 밀도, 터치 타겟 기준 강점 / 데이터 테이블 패턴은 상대적으로 제한
- Atlassian Design System: 운영 툴용 정보 밀도/상태 배지 강점 / 초기 학습 복잡도 큼
- Shopify Polaris: 관리자 UX(표/폼/피드백) 강점 / B2C 앱 감성에는 직접 이식 어려움
- Ant Design: 어드민 패턴 풍부, 상태 표현 명확 / 과도한 시각적 복잡성 위험
- GitHub Primer: 뉴트럴/경계선/포커스 링 단순 일관 강점 / 강한 브랜드 톤은 별도 설계 필요
- WCAG 2.2: 대비·포커스·키보드·타겟 크기 기준 제공 / 시각 언어 자체는 정의하지 않음
- Radix Color 접근: 라이트/다크 대비가 예측 가능한 팔레트 운영 강점 / RN 직접 적용은 매핑 필요

재사용 원칙 추출:
- 의미 기반 색상(Primary/Secondary + Semantic)과 표면 계층(Surface/Elevated) 분리
- 컴포넌트는 variant보다 state 명세를 먼저 고정(default/hover/focus/disabled/error)
- 운영 화면은 액션 색을 절제하고, 위험 작업만 error 계열로 강조
- 최소 44px 터치 타겟, 명확한 focus indicator, 본문 대비 4.5:1 이상 유지

# 3. Design Philosophy

- 하나의 토큰 소스로 앱/어드민 모두를 커버한다.
- 브랜드 강조는 `primary`(오렌지), 운영 컨트롤은 `secondary`(인디고)로 역할 분리한다.
- 시각 장식보다 상태 전달(읽기/입력/성공/오류/비활성)을 우선한다.
- 하드코딩 색상/간격을 금지하고 토큰만 사용한다.

# 4. Token Definitions

## Color Tokens (CSS 변수 기준)

```css
:root {
  --color-primary-50: #fff7ed;
  --color-primary-500: #f97316;
  --color-primary-600: #ea580c;

  --color-secondary-100: #e0e7ff;
  --color-secondary-500: #6366f1;
  --color-secondary-600: #4f46e5;

  --color-neutral-50: #f9fafb;
  --color-neutral-100: #f3f4f6;
  --color-neutral-200: #e5e7eb;
  --color-neutral-300: #d1d5db;
  --color-neutral-500: #6b7280;
  --color-neutral-700: #374151;
  --color-neutral-900: #111827;

  --color-success-600: #16a34a;
  --color-warning-600: #d97706;
  --color-error-600: #dc2626;
  --color-info-600: #2563eb;

  --color-surface-canvas: #ffffff;
  --color-surface-subtle: #f9fafb;
  --color-surface-elevated: #ffffff;
}
```

## Typography Tokens

```css
:root {
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;

  --line-height-sm: 18px;
  --line-height-base: 22px;
  --line-height-lg: 24px;
}
```

## Spacing / Radius / Motion

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;

  --radius-sm: 8px;
  --radius-md: 10px;
  --radius-lg: 12px;
  --radius-xl: 16px;

  --motion-fast: 120ms;
  --motion-normal: 180ms;
  --motion-slow: 260ms;
}
```

RN 구현 매핑:
- `apps/mobile/theme/tokens.ts`
- `apps/mobile/theme/primitives.ts`

# 5. Component Standards

- Button
  - Variants: primary/secondary/danger
  - States: default, pressed(Opacity), disabled(opacity 0.6), focus(웹에서 outline 2px secondary-300 권장)
  - Rule: 파괴적 액션만 danger 사용
- Input
  - States: default(border neutral-300), focus(border secondary-500), error(border error-600), disabled(bg neutral-100)
  - Rule: placeholder는 text-tertiary 이하 대비 유지
- Card
  - Surface elevated + border subtle + radius lg
  - Rule: 카드 내부 간격은 `space-2` 또는 `space-3`만 사용
- Navigation (탭/상단링크)
  - 활성 탭은 primary, 어드민 네비게이션은 secondary/neutral 중심
- Modal / Feedback
  - 오류 메시지는 error-700, 성공 메시지는 success-700
  - Toast/Alert는 텍스트 대비 4.5:1 이상 유지
- Table/List (어드민 목록)
  - 행 경계선은 neutral-200, 본문은 neutral-900, 메타는 neutral-700

# 6. Accessibility Notes

- WCAG 2.2 AA 기준으로 텍스트 대비(일반 4.5:1, 큰 텍스트 3:1) 준수
- 키보드 탐색: 웹 어드민 링크/버튼/입력 focus 표시 필수
- 터치 타겟: 주요 액션 높이 44px 이상(현재 버튼 높이 44 적용)
- 스크린리더: 아이콘 단독 버튼에는 `accessibilityLabel` 유지
- Reduced motion: 장식 애니메이션 최소화, 상태 변경 중심 피드백 유지

# 7. Implementation Guide

적용 완료 범위:
- 토큰/프리미티브 생성: `apps/mobile/theme/tokens.ts`, `apps/mobile/theme/primitives.ts`
- 앱 화면: `app/(auth)/login.tsx`, `app/(auth)/signup.tsx`, `app/(tabs)/index.tsx`, `app/(tabs)/two.tsx`, `app/article/[articleId].tsx`, `app/modal.tsx`
- 어드민 화면: `app/admin/_layout.tsx`, `app/admin/login.tsx`, `app/admin/dashboard.tsx`, `app/admin/members.tsx`, `app/admin/modules.tsx`, `app/admin/audit.tsx`
- 탭 컬러: `constants/Colors.ts`

Tailwind 확장 방향(웹 확장 시):
- `theme.extend.colors.primary/secondary/neutral/semantic`를 토큰과 동일 키로 정의
- `theme.extend.spacing`에 `1,2,3,4,6,8`을 동일 수치로 매핑
- 컴포넌트 클래스는 semantic alias(`bg-surface`, `text-primary`) 우선 사용

금지(anti-pattern):
- 화면별 임의 hex 직접 사용
- 동일 역할 버튼에 색상 다중 사용
- 카드/입력 radius를 임의 숫자로 혼용
- 오류/성공 상태를 텍스트 없이 색만으로 전달
