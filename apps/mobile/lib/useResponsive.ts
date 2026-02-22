import { useWindowDimensions } from 'react-native';

const BREAKPOINT_SM = 380;
const BREAKPOINT_MD = 480;
const CARD_MAX_WIDTH = 340;
const CARD_MAX_WIDTH_WIDE = 420;

export function useResponsive() {
  const { width, height } = useWindowDimensions();
  const isNarrow = width < BREAKPOINT_SM;
  const isMedium = width >= BREAKPOINT_SM && width < BREAKPOINT_MD;
  const pagePaddingHorizontal = isNarrow ? 16 : isMedium ? 20 : 24;
  const pagePaddingVertical = height < 500 ? 16 : 24;
  const cardMaxWidth = Math.min(width - pagePaddingHorizontal * 2, CARD_MAX_WIDTH);
  const cardMaxWidthWide = Math.min(width - pagePaddingHorizontal * 2, CARD_MAX_WIDTH_WIDE);
  return {
    width,
    height,
    isNarrow,
    pagePaddingHorizontal,
    pagePaddingVertical,
    cardMaxWidth,
    cardMaxWidthWide,
  };
}
