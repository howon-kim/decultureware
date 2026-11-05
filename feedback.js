(() => {
  const form = document.querySelector('[data-feedback-form]');
  if (!form) return;
  const ko = document.documentElement.lang === 'ko';
  const text = ko ? {
    sending: '보내는 중…', send: '피드백 보내기', success: '피드백을 보냈습니다. 의견을 남겨 주셔서 감사합니다.',
    error: '전송하지 못했습니다. 입력 내용은 유지됩니다. 잠시 후 다시 시도하거나 아래 이메일로 보내 주세요.',
    rate: '짧은 시간에 여러 번 제출했습니다. 10분 후 다시 시도하거나 이메일로 보내 주세요.',
    invalid: '이메일과 입력 내용을 확인해 주세요.'
  } : {
    sending: 'Sending…', send: 'Send feedback', success: 'Your feedback has been sent. Thank you for sharing it.',
    error: 'We could not send your feedback. Your text is still here. Try again shortly or use the email link below.',
    rate: 'Too many submissions. Please try again in 10 minutes or use the email link below.',
    invalid: 'Please check your email and message.'
  };
  const status = document.getElementById('feedback-status');
  const button = form.querySelector('button[type="submit"]');
  const fields = form.querySelector('fieldset');
  button.disabled = false;
  let pending = false;
  let submissionID;
  form.addEventListener('input', () => { if (!pending) submissionID = undefined; });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (pending || !form.reportValidity()) return;
    const payload = Object.fromEntries(new FormData(form));
    submissionID ||= Array.from(crypto.getRandomValues(new Uint8Array(16)), byte => byte.toString(16).padStart(2, '0')).join('');
    payload.submission_id = submissionID;
    pending = true;
    fields.disabled = true;
    button.disabled = true;
    form.setAttribute('aria-busy', 'true');
    button.textContent = text.sending;
    status.textContent = '';
    status.dataset.state = '';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 35000);
    try {
      const response = await fetch(form.action, {
        method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload), signal: controller.signal, credentials: 'same-origin'
      });
      const result = await response.json();
      if (!response.ok || result.ok !== true) {
        status.textContent = response.status === 429 ? text.rate : response.status === 422 ? text.invalid : text.error;
        status.dataset.state = 'error';
        return;
      }
      form.reset();
      submissionID = undefined;
      status.textContent = text.success;
      status.dataset.state = 'success';
    } catch {
      status.textContent = text.error;
      status.dataset.state = 'error';
    } finally {
      clearTimeout(timeout);
      pending = false;
      fields.disabled = false;
      button.disabled = false;
      form.removeAttribute('aria-busy');
      button.textContent = text.send;
      status.focus();
    }
  });
})();
