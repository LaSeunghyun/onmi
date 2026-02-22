# devlog 도구 사용법

`tools/devlog.py`는 "구조화 개발 워크플로우"를 강제/보조하기 위한 최소 CLI입니다.

## 파일 구성

- `devlog/DEVELOPMENT_LOG.md`: 단일 개발 로그(소스 오브 트루스)
- `devlog/CONTEXT.md`: 컨텍스트 리셋용(자동 생성/갱신)
- `devlog/state.json`: 기계가 읽는 현재 step 상태
- `tools/devlog.py`: 상태 조회/컨텍스트 로드/step 시작/step 완료

## 사용법 (PowerShell)

워크스페이스 루트(`touch/`)에서 실행하세요.

```powershell
python tools/devlog.py validate
python tools/devlog.py status
python tools/devlog.py load
python tools/devlog.py check
python tools/devlog.py start 2
python tools/devlog.py complete 2
python tools/devlog.py next
python tools/devlog.py enforce on
python tools/devlog.py enforce off
```

## 권장 운영 규칙 (컨텍스트 리셋)

다음 Step을 시작하기 전, 아래를 반드시 실행:

```powershell
python tools/devlog.py load
```

`devlog/CONTEXT.md`를 열어 **그대로** 컨텍스트로 삼아 작업을 재개하세요.

## 강제(가드) 모드

기본값으로 `enforce_context_before_start=true`이며, 이 모드에서는:

- `start`는 컨텍스트가 최신(`check=ok`)이 아니면 실패합니다.
- `next`는 `load` 후 다음 Step을 시작합니다.

