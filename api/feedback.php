<?php
declare(strict_types=1);
ini_set('display_errors', '0');
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
require __DIR__ . '/feedback/bootstrap.php';

try {
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
        header('Allow: POST');
        throw new FeedbackError(405, 'method_not_allowed');
    }
    if (strtolower(trim(explode(';', $_SERVER['CONTENT_TYPE'] ?? '')[0])) !== 'application/json') {
        throw new FeedbackError(415, 'invalid');
    }
    if ((int)($_SERVER['CONTENT_LENGTH'] ?? 0) > 20000) { throw new FeedbackError(413, 'invalid'); }
    $raw = file_get_contents('php://input', false, null, 0, 20001);
    if ($raw === false || strlen($raw) > 20000) { throw new FeedbackError(413, 'invalid'); }
    try { $data = json_decode($raw, true, 16, JSON_THROW_ON_ERROR); }
    catch (JsonException $error) { throw new FeedbackError(422, 'invalid'); }
    if (!is_array($data)) { throw new FeedbackError(422, 'invalid'); }
    $config = feedbackConfig();
    $response = feedbackSubmit($data, $config, $_SERVER['HTTP_ORIGIN'] ?? '',
        $_SERVER['REMOTE_ADDR'] ?? '', 'feedbackMail');
    echo json_encode($response);
} catch (FeedbackError $error) {
    http_response_code($error->status);
    if ($error->status === 429) { header('Retry-After: 600'); }
    if ($error->status >= 500) { error_log('Feedback: ' . $error->getMessage()); }
    echo json_encode(['ok'=>false, 'code'=>$error->getMessage()]);
} catch (Throwable $error) {
    http_response_code(503);
    error_log('Feedback: service unavailable');
    echo json_encode(['ok'=>false, 'code'=>'unavailable']);
}
