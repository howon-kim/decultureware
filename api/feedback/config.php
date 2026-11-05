<?php
declare(strict_types=1);

function feedbackConfig(): array {
    $path = getenv('DCW_FEEDBACK_CONFIG') ?: '/volume2/web_privates/feedback.php';
    $real = realpath($path);
    $webRoot = realpath(dirname(__DIR__, 2));
    if (!$real || ($webRoot && str_starts_with($real, $webRoot . DIRECTORY_SEPARATOR))) {
        throw new FeedbackError(503, 'unavailable');
    }
    $config = require $real;
    if (!is_array($config)) { throw new FeedbackError(503, 'unavailable'); }
    foreach (['smtp_host', 'smtp_username', 'smtp_password', 'from_email', 'state_dir', 'rate_secret'] as $key) {
        if (!isset($config[$key]) || !is_string($config[$key]) || $config[$key] === '') {
            throw new FeedbackError(503, 'unavailable');
        }
    }
    if (strlen($config['rate_secret']) < 32 || empty($config['allowed_origins'])
        || !is_array($config['allowed_origins'])
        || !filter_var($config['from_email'], FILTER_VALIDATE_EMAIL)
        || !in_array($config['smtp_security'] ?? '', ['tls', 'ssl'], true)
        || !in_array($config['smtp_port'] ?? 0, [465, 587], true)
        || !preg_match('/^[a-zA-Z0-9.-]+$/', $config['smtp_host'])) {
        throw new FeedbackError(503, 'unavailable');
    }
    $state = realpath($config['state_dir']);
    if (!$state || !is_writable($state) || ($webRoot && ($state === $webRoot || str_starts_with($state, $webRoot . DIRECTORY_SEPARATOR)))) {
        throw new FeedbackError(503, 'unavailable');
    }
    return $config;
}

