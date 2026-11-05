# decultureware 폴더를 그대로 복사해서 배포하기

> 이전 NAS 배포 방식의 참고 문서입니다. 현재 웹사이트는 Cloudflare Pages와 이메일 문의 링크를 사용합니다.
> 현재 배포 방법은 [README](README.md#cloudflare-pages-deployment)를 참고하세요.

앞으로는 로컬 `decultureware` 폴더를 기존 NAS 사이트 위치에 그대로 복사하면 됩니다.
ZIP 압축 해제나 `public` 폴더 선택 업로드는 필요 없습니다.
아래 최초 설정만 한 번 해두세요. NAS 설정과 실제 메일 수신은 아직 확인 전입니다.

## 1. 처음 한 번: Web Station

- 패키지 센터에서 Apache HTTP Server 2.4와 PHP 8.2 이상을 설치합니다.
- Web Station에서 현재 사이트의 웹 서비스를 편집합니다.
- HTTP 백엔드를 **Apache HTTP Server 2.4**로 선택하고 PHP 프로필을 연결합니다.
- 기존 도메인과 문서 루트는 유지하고 HTTPS로 접속합니다.
- PHP에서 openssl, ctype, filter를 사용할 수 있어야 합니다.

이 폴더의 `.htaccess`가 개발용 파일과 배포 ZIP에 대한 웹 접근을 막습니다.
Nginx를 HTTP 백엔드로 선택하면 이 파일이 적용되지 않습니다.
NAS 앞단의 기본 Nginx 프록시는 그대로 두어도 됩니다. 바꾸는 것은 해당 사이트의 HTTP 백엔드입니다.

## 2. 처음 한 번: 메일 설정

웹사이트와 별도로 `/volume2/web_privates` 폴더를 만듭니다.
NAS에서 `/volume2/web_privates` 폴더를 만듭니다.
PHP 실행 계정이 상위 폴더에도 접근할 수 있어야 합니다.

1. 로컬의 `config/feedback.example.php`를 그 폴더에 복사합니다.
2. NAS의 복사본 이름을 `feedback.php`로 바꿉니다.
3. 같은 위치에 빈 `state` 폴더를 만듭니다.
4. NAS의 `feedback.php`를 편집합니다.

| 설정 | 입력할 내용 |
|---|---|
| allowed_origins | 실제 사이트 주소. `['https://실제도메인']` 형태, 끝의 `/`와 페이지 경로 제외 |
| smtp_host | `mail.howon.kim` 유지 |
| smtp_port / smtp_security | `587` / `'tls'` 유지 |
| smtp_username | MailPlus 발송 계정의 로그인 아이디 |
| smtp_password | 해당 계정 비밀번호 |
| from_email | 해당 계정에 발송 권한이 있는 주소. 가능하면 `feedback@decultureware.com` |
| state_dir | `/volume2/web_privates/state` 유지 |
| rate_secret | 비밀번호 관리자로 만든 무작위 영문·숫자 64자 |

MailPlus Server에서 인증된 SMTP-STARTTLS(587)를 활성화하세요.
`mail.howon.kim`에 맞는 유효한 인증서가 필요합니다.
피드백 수신자는 항상 `feedback@decultureware.com`입니다.

PHP 실행 계정에 비공개 폴더 접근, `feedback.php` 읽기, `state` 쓰기 권한을 줍니다.
PHP 프로필의 `open_basedir`에 제한이 있다면 기존 경로를 유지하면서
`/volume2/web_privates`를 허용 경로에 추가합니다.
실제 비밀번호는 로컬 프로젝트, ZIP, 웹 공개 폴더에 넣지 마세요.

## 3. 이후 매번: 평소처럼 폴더 복사

로컬 `decultureware`를 NAS의 기존 `decultureware` 위치에 복사하고 덮어씁니다.
예를 들어 기존 사이트가 `/volume1/web/decultureware`라면 다음 구조입니다.

```text
/volume1/web/decultureware/     ← 기존 공개 사이트 위치 예시, 로컬 폴더 복사
├── .htaccess
├── index.html
├── api/
├── feedback.js
└── 나머지 기존 파일들

/volume2/web_privates/  ← 비공개 설정, 복사 대상 밖
├── feedback.php
└── state/
```

`decultureware/decultureware`처럼 이중 폴더가 생기지 않게 확인하세요.
폴더 전체를 복사하면 숨김 파일 `.htaccess`도 포함됩니다. 내용물을 직접 선택해
복사하는 경우 Finder에서 Command + Shift + . 로 숨김 파일을 표시하고 함께 복사하세요.
NAS의 비공개 설정과 전송 기록은 사이트 폴더 밖에 있어 사이트 교체 후에도 유지됩니다.
`apps.json`이나 페이지 생성기를 바꿨다면 복사 전에 `python3 scripts/build-showroom.py`를 실행합니다.
완성된 HTML/CSS/JS만 수정했다면 추가 빌드가 필요 없습니다.

## 4. 첫 복사 후 확인

- 기존 홈페이지와 `/ko/bananacal/contact.html`이 열리는지 확인합니다.
  사이트가 하위 경로에 있다면 그 경로 뒤에 붙입니다.
- `/config/feedback.example.php`와 `/tests/feedback.php`는 **403 또는 404**가 나와야 합니다.
  문서 내용이 보이면 `.htaccess` 복사 여부와 Apache 백엔드 설정을 확인합니다.
- 피드백 한 건을 전송하고 `feedback@decultureware.com` 받은편지함/스팸함을 확인합니다.
- 503 오류: 비공개 설정 위치, 폴더 권한, PHP 설정을 확인합니다.
- 502 오류: SMTP 로그인, 서버 연결, 인증서를 확인합니다.

구조 및 유지보수: [프로젝트 안내](README.md)
