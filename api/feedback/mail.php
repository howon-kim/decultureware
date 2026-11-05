<?php
declare(strict_types=1);

function feedbackCreateMail(array $data, array $config): PHPMailer\PHPMailer\PHPMailer {
    require_once dirname(__DIR__) . '/lib/PHPMailer/src/Exception.php';
    require_once dirname(__DIR__) . '/lib/PHPMailer/src/PHPMailer.php';
    require_once dirname(__DIR__) . '/lib/PHPMailer/src/SMTP.php';
    $mail = new PHPMailer\PHPMailer\PHPMailer(true);
    $mail->isSMTP();
    $mail->Host = $config['smtp_host'];
    $mail->Port = $config['smtp_port'];
    $mail->SMTPSecure = $config['smtp_security'];
    $mail->SMTPAuth = true;
    $mail->Username = $config['smtp_username'];
    $mail->Password = $config['smtp_password'];
    $mail->Timeout = 15;
    $mail->getSMTPInstance()->Timelimit = 20;
    $mail->CharSet = 'UTF-8';
    $mail->setFrom($config['from_email'], 'BananaCal Feedback');
    $mail->addAddress(FEEDBACK_RECIPIENT);
    $mail->addReplyTo($data['email']);
    $mail->Subject = '[BananaCal][' . $data['platform'] . '] ' . $data['kind'];
    $mail->Body = "App: BananaCal\nType: {$data['kind']}\nPlatform: {$data['platform']}\nVersion: {$data['version']}\nReply to: {$data['email']}\n\n{$data['message']}";
    $mail->isHTML(false);
    // Leave TLS peer/name validation enabled. Never trust a visitor's From/To.
    return $mail;
}

function feedbackMail(array $data, array $config): void {
    $mail = feedbackCreateMail($data, $config);
    try { $mail->send(); }
    catch (Throwable $error) { throw new FeedbackError(502, 'delivery_failed'); }
}
