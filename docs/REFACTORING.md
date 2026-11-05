# decultureware 리팩토링 가이드

현재 Cloudflare Pages 배포는 `scripts/build-cloudflare.py`가 공개 파일만 `dist/`에 모읍니다.
BananaCal 문의 페이지는 이메일 링크를 사용하며, 아래 PHP/SMTP 구조는 이전 NAS 구현의 참고 자료입니다.

## 기준

1. 기존 공개 URL, 화면, SMTP 동작을 유지한 채 내부 구조를 정리한다.
2. 앱 정보는 apps.json 한 곳에서 관리한다. 생성 HTML은 NAS에 바로 복사하기 위해 유지한다.
3. 실제로 반복되는 데이터 읽기, 스크린샷 선택, 상대 경로 처리는 scripts/site_common.py로 모은다.
4. PHP는 HTTP 진입점, 설정, 입력 검증, 전송 제한/중복 방지, SMTP 발송으로 나눈다.
5. 사용처와 외부 링크 역할을 확인한 파일만 제거한다. 파일 이름이나 오래된 날짜만으로 삭제하지 않는다.
6. 빌드를 반복해도 출력이 같아야 한다. 변경 후 링크와 기존 피드백 회귀 검사를 실행한다.

## 구조

- 루트 CSS/JS: 기존 공개 경로를 유지하는 공통 화면 자원.
- apps.json, locales/: 콘텐츠 원본과 번역.
- scripts/: 로컬 생성 도구. 서버에서 실행하지 않는다.
- api/feedback.php: 공개 피드백 요청 처리.
- api/feedback/: 역할별 내부 PHP. 직접 웹 접근 차단.
- api/lib/PHPMailer/: 외부 SMTP 라이브러리. 라이선스 포함, 직접 수정하지 않는다.
- config/: 실제 비밀번호가 없는 설정 예제. 직접 웹 접근 차단.
- tests/: 메일을 보내지 않는 회귀 검사와 빌드/링크 검사.
- apps/, ko/, 각 앱 폴더: 그대로 배포하는 공개 HTML 및 이미지.

## 이번 정리

- 참조되지 않는 이전 Bootstrap navbar.js 제거.
- 폴더 통째로 복사하는 운영 방식에 불필요하고, 이미 없는 deploy 폴더를 요구하는 ZIP 생성기 제거.
- 합쳐져 있던 feedback-core.php는 api/feedback/의 역할별 파일로 대체.
- Finder 임시 파일 .DS_Store 제거, Python 캐시 제외.
- 스크린샷 갱신기의 중복 앱 목록은 apps.json에서 읽도록 변경.
- 번역 스크립트를 반복 실행할 때 언어 링크가 누적되는 문제 해결.

약관/개인정보 문서, BananaSnap 대체 이미지, wyr/index.html 및 habitplate/index.html의
이전 URL 이동 페이지는 유지한다. 기존 사용자 수정과 앱 콘텐츠도 유지한다.
NAS 비공개 설정은 /volume2/web_privates에 계속 둔다.
