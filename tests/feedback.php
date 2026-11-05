<?php
declare(strict_types=1);
// Folder-copy deployments also include tests; never run them over HTTP.
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
require dirname(__DIR__) . '/api/feedback/bootstrap.php';
function check(bool $ok, string $label): void { if (!$ok) { throw new RuntimeException($label); } }
function expectStatus(int $status, callable $fn): void {
    try { $fn(); } catch (FeedbackError $e) { check($status === $e->status, 'Unexpected error code'); return; }
    throw new RuntimeException('Expected rejection: ' . $status);
}
$dir = __DIR__ . '/.feedback-test-' . bin2hex(random_bytes(8));
mkdir($dir, 0700);
$config = ['allowed_origins'=>['https://site.example'], 'state_dir'=>$dir, 'rate_secret'=>str_repeat('x', 40),
    'smtp_host'=>'smtp.example', 'smtp_port'=>587, 'smtp_security'=>'tls', 'smtp_username'=>'fixture',
    'smtp_password'=>'fixture-not-a-real-password', 'from_email'=>'feedback@decultureware.com'];
$data = ['app'=>'bananacal', 'kind'=>'bug', 'platform'=>'ios', 'email'=>'tester@example.com',
    'version'=>'2.0', 'message'=>"한글 테스트\n<script>plain text</script>", 'submission_id'=>str_repeat('a',32), 'website'=>''];
$count = 0;
$sender = function($payload, $settings) use (&$count) { $count++; };
try {
    check(feedbackValidate($data)['message'] === $data['message'], 'Unicode preserved');
    expectStatus(422, fn()=>feedbackValidate(array_replace($data,['email'=>"test@example.com\r\nBcc: bad@example.com"])));
    expectStatus(422, fn()=>feedbackValidate(array_replace($data,['email'=>['bad']])));
    expectStatus(422, fn()=>feedbackValidate(array_replace($data,['message'=>str_repeat('a',12001)])));
    expectStatus(422, fn()=>feedbackValidate(array_replace($data,['message'=>'  '])));
    expectStatus(422, fn()=>feedbackValidate(array_replace($data,['website'=>'spam.example'])));
    expectStatus(422, fn()=>feedbackValidate(array_replace($data,['app'=>'someone-else'])));
    expectStatus(403, fn()=>feedbackSubmit($data,$config,'https://other.example','127.0.0.1',$sender));
    expectStatus(403, fn()=>feedbackSubmit($data,$config,'','127.0.0.1',$sender));
    check($count===0,'Rejected submissions never send');
    feedbackSubmit($data,$config,'https://site.example','127.0.0.1',$sender);
    feedbackSubmit($data,$config,'https://site.example','127.0.0.1',$sender);
    check($count===1,'Network retry must not send a duplicate');
    expectStatus(409,fn()=>feedbackSubmit(array_replace($data,['message'=>'changed']),$config,'https://site.example','127.0.0.1',$sender));
    for($i=0;$i<4;$i++) {
        $next=array_replace($data,['submission_id'=>bin2hex(random_bytes(16))]);
        feedbackSubmit($next,$config,'https://site.example','127.0.0.1',$sender);
    }
    $next=array_replace($data,['submission_id'=>bin2hex(random_bytes(16))]);
    expectStatus(429,fn()=>feedbackSubmit($next,$config,'https://site.example','127.0.0.1',$sender));
    check($count===5,'Per-address quota enforced');
    expectStatus(502,fn()=>feedbackSubmit($next,$config,'https://site.example','127.0.0.2',function(){throw new FeedbackError(502,'delivery_failed');}));
    feedbackSubmit($next,$config,'https://site.example','127.0.0.2',$sender);
    check($count===6,'Failed send is retryable and never acknowledged as sent');
    $mail=feedbackCreateMail(array_replace($data,['to'=>'attacker@example.com']),$config);
    check($mail->getToAddresses()[0][0]==='feedback@decultureware.com','Fixed recipient');
    check(array_values($mail->getReplyToAddresses())[0][0]==='tester@example.com','Visitor is Reply-To');
    check($mail->From==='feedback@decultureware.com' && $mail->SMTPAuth && $mail->SMTPSecure==='tls','Authenticated TLS sender');
    check($mail->ContentType==='text/plain','User HTML stays plain text');
    check($mail->preSend(),'Valid MIME message');
    $raw=file_get_contents($dir.'/feedback-state.json');
    check(!str_contains($raw,'tester@example.com')&&!str_contains($raw,'한글')&&!str_contains($raw,'127.0.0.1'),'No raw email/message/IP in state');
    $state=json_decode($raw,true);
    $state['attempts']=array_fill(0,60,['ip'=>'some-other-address','time'=>time()]);
    file_put_contents($dir.'/feedback-state.json',json_encode($state));
    expectStatus(429,fn()=>feedbackSubmit(array_replace($data,['submission_id'=>bin2hex(random_bytes(16))]),$config,'https://site.example','127.0.0.3',$sender));
    file_put_contents($dir.'/feedback-state.json','bad json');
    try { feedbackSubmit($data,$config,'https://site.example','127.0.0.1',$sender); throw new RuntimeException('Corrupt state should fail closed'); }
    catch (JsonException $expected) {}
    echo "PASS: validation, origin, header injection, quotas, idempotency, failure/retry, MIME, recipient and private state\n";
} finally {
    if(is_file($dir.'/feedback-state.json'))unlink($dir.'/feedback-state.json');
    rmdir($dir);
}
