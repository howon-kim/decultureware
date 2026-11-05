#!/usr/bin/env python3
"""Generate BananaCal's English/Korean email contact pages."""
from html import escape as e
from site_common import ROOT as R
TEXT={
'en':dict(title='Share your feedback',intro='Found a bug? Have an idea? Tell us how BananaCal can work better for you.',back='← BananaCal',apps='The apps',studio='The studio',hello='Say hello ↗',support='Feedback',privacy='Privacy policy',terms='Terms & conditions',legend='A note to the BananaCal team',kind='What would you like to share?',kinds=['Report a bug','Suggest a feature','Ask a question','Something else'],platform='Where do you use BananaCal?',platforms=['iPhone / iPad','Mac','Other'],version='App version (optional)',version_hint='For example, 2.0.1',email='Your email',email_hint='So we can reply to your feedback.',message='Your feedback',placeholder='What happened, or what would you like to see? For a bug, include the steps that led to it.',note='Please leave out passwords and private calendar details.',send='Send feedback',notice='Your email and message will be sent to our support inbox to handle your request. Calendar data is not attached automatically.',or_email='Prefer email?',nojs='Enable JavaScript to submit the form, or email us directly below.',footer='Small tools. Everyday possibilities.'),
'ko':dict(title='여러분의 의견을 들려주세요',intro='불편했던 점이나 새로 바라는 기능이 있나요? BananaCal을 더 편리하게 만드는 데 여러분의 의견이 도움이 됩니다.',back='← BananaCal',apps='앱 둘러보기',studio='스튜디오',hello='문의하기 ↗',support='피드백',privacy='개인정보 처리방침',terms='이용약관',legend='BananaCal 팀에게 보내는 의견',kind='어떤 의견인가요?',kinds=['오류 제보','기능 제안','사용 문의','기타'],platform='어디에서 사용하시나요?',platforms=['iPhone / iPad','Mac','기타'],version='앱 버전 (선택)',version_hint='예: 2.0.1',email='답변받을 이메일',email_hint='남겨주신 의견에 답변할 때만 사용합니다.',message='피드백 내용',placeholder='어떤 일이 있었나요? 오류라면 문제가 발생한 과정을 함께 적어 주세요.',note='비밀번호나 개인 일정의 민감한 내용은 적지 말아 주세요.',send='피드백 보내기',notice='이메일과 작성한 내용은 문의 응대를 위해 지원 메일함으로 전달됩니다. 캘린더 데이터는 자동으로 첨부되지 않습니다.',or_email='이메일로 보내고 싶다면',nojs='폼을 전송하려면 JavaScript를 켜거나 아래 이메일로 직접 보내 주세요.',footer='작은 도구. 매일의 가능성.')
}

def build():
 for lang,t in TEXT.items():
  ko=lang=='ko'; base='../../' if ko else '../'; home='../index.html'; product='../apps/bananacal.html'
  english='../../bananacal/contact.html' if ko else 'contact.html'
  korean='contact.html' if ko else '../ko/bananacal/contact.html'
  privacy=base+'bananacal/privacy.html'; terms=base+'bananacal/terms.html'
  email_intro = '아래 이메일 주소를 누르면 메일 앱이 열립니다. 내용을 작성한 뒤 메일 앱에서 보내 주세요.' if ko else 'Select the email address below to open your email app. Write your message and send it from there.'
  email_hint = '오류를 알려주실 때는 사용 기기, 운영체제와 BananaCal 버전, 문제가 발생한 과정을 함께 적어 주세요.' if ko else 'For a bug report, please include your device, operating system, BananaCal version, and the steps that led to the issue.'
  html=f'''<!doctype html>
<html lang="{lang}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{e(t['intro'])}"><title>{t['support']} · BananaCal</title>
<link rel="stylesheet" href="{base}subpage.css">
<link rel="alternate" hreflang="en" href="{english}"><link rel="alternate" hreflang="ko" href="{korean}">
</head><body>
<a class="skip" href="#main">{'본문으로 이동' if ko else 'Skip to content'}</a>
<header class="header wrap"><a class="brand" href="{home}" aria-label="Design Culture Software"><span class="brand-mark">dcw.</span><span class="brand-name">Design Culture<br>Software</span></a><nav aria-label="{'주 메뉴' if ko else 'Main navigation'}"><a href="{home}#apps">{t['apps']}</a><a href="{home}#studio">{t['studio']}</a><span class="language-switch"><a href="{english}" lang="en" {'aria-current="page"' if not ko else ''}>EN</a><span aria-hidden="true"> / </span><a href="{korean}" lang="ko" {'aria-current="page"' if ko else ''}>한국어</a></span></nav></header>
<div class="wrap support-context"><a class="back" href="{product}">{t['back']}</a><nav aria-label="BananaCal"><a href="contact.html" aria-current="page">{t['support']}</a><a href="{privacy}">{t['privacy']}</a><a href="{terms}">{t['terms']}</a></nav></div>
<header class="page-header yellow"><div class="container"><span class="sp-badge yellow">BananaCal</span><h1>{t['title']}</h1></div></header>
<main id="main" class="content-container"><div class="container"><div class="contact-wrap"><p>{t['intro']}</p>
<p>{email_intro}</p><p>{email_hint}</p>
<div class="contact-divider">{'이메일 문의' if ko else 'Email support'}</div>
<a class="contact-email-link" href="mailto:feedback@howon.kim?subject=BananaCal%20feedback">feedback@howon.kim</a>
<p>{t['note']} <a href="{privacy}#website-feedback">{t['privacy']} ↗</a></p>
</div></div></main><footer class="wrap footer"><a class="brand-mark" href="{home}">dcw.</a><p>{t['footer']}</p><span>© 2026 Design Culture Software</span></footer></body></html>'''
  dest=R/('ko/bananacal/contact.html' if ko else 'bananacal/contact.html');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(html)
if __name__=='__main__':build()
