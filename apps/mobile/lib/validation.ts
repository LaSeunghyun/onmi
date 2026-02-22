/**
 * 클라이언트 검증 유틸 및 API 에러 메시지 매핑
 * - 필수 입력, 이메일 형식, 비밀번호 길이 등
 * - API status/detail → 사용자용 한글 메시지
 */

export const MIN_PASSWORD_LENGTH = 8;

/** 간단한 이메일 형식 검사 (RFC 완전 검증은 백엔드에서) */
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function isNonEmpty(value: string): boolean {
  return value.trim().length > 0;
}

export function isValidEmailFormat(value: string): boolean {
  return EMAIL_REGEX.test(value.trim());
}

export function validateEmail(value: string): string | null {
  if (!isNonEmpty(value)) return '이메일을 입력해 주세요.';
  if (!isValidEmailFormat(value)) return '올바른 이메일 형식이 아닙니다.';
  return null;
}

export function validatePasswordRequired(value: string): string | null {
  if (!isNonEmpty(value)) return '비밀번호를 입력해 주세요.';
  return null;
}

export function validatePasswordLength(value: string): string | null {
  if (value.length < MIN_PASSWORD_LENGTH) return `비밀번호는 ${MIN_PASSWORD_LENGTH}자 이상이어야 합니다.`;
  return null;
}

export function validateAdminIdRequired(value: string): string | null {
  if (!isNonEmpty(value)) return '관리자 ID를 입력해 주세요.';
  return null;
}

/** API 에러를 사용자용 한글 메시지로 변환 */
export type ApiErrorLike = { status?: number; message?: string };

export function toAuthLoginMessage(e: ApiErrorLike): string {
  const msg = (e?.message ?? '').toLowerCase();
  const status = e?.status;
  if (status === 401 || msg.includes('invalid credentials') || msg.includes('unauthorized'))
    return '이메일 또는 비밀번호가 올바르지 않습니다.';
  if (status === 422 || msg.includes('validation') || msg.includes('email')) return '입력값을 확인해 주세요.';
  return e?.message && e.message.length > 0 ? e.message : '로그인에 실패했습니다.';
}

export function toAuthSignupMessage(e: ApiErrorLike): string {
  const msg = (e?.message ?? '').toLowerCase();
  const status = e?.status;
  if (status === 409 || msg.includes('already exists') || msg.includes('email already'))
    return '이미 사용 중인 이메일입니다.';
  if (status === 400 && (msg.includes('password') || msg.includes('short')))
    return `비밀번호는 ${MIN_PASSWORD_LENGTH}자 이상이어야 합니다.`;
  if (status === 422 || msg.includes('validation')) return '입력값을 확인해 주세요.';
  return e?.message && e.message.length > 0 ? e.message : '회원가입에 실패했습니다.';
}

export function toAdminLoginMessage(e: ApiErrorLike): string {
  const msg = (e?.message ?? '').toLowerCase();
  const status = e?.status;
  if (status === 401 || msg.includes('invalid') || msg.includes('credentials') || msg.includes('admin'))
    return '관리자 ID 또는 비밀번호가 올바르지 않습니다.';
  return e?.message && e.message.length > 0 ? e.message : '관리자 로그인에 실패했습니다.';
}

export function toAdminChangePasswordMessage(e: ApiErrorLike): string {
  const msg = (e?.message ?? '').toLowerCase();
  const status = e?.status;
  if (status === 400 && (msg.includes('mismatch') || msg.includes('current password')))
    return '현재 비밀번호가 일치하지 않습니다.';
  if (status === 400 && (msg.includes('different') || msg.includes('new password')))
    return '새 비밀번호는 현재 비밀번호와 달라야 합니다.';
  if (status === 400 && (msg.includes('short') || msg.includes('password')))
    return `새 비밀번호는 ${MIN_PASSWORD_LENGTH}자 이상이어야 합니다.`;
  return e?.message && e.message.length > 0 ? e.message : '비밀번호 변경에 실패했습니다.';
}
