<?php
declare(strict_types=1);

// No request field can change the recipient or SMTP configuration.
const FEEDBACK_RECIPIENT = 'feedback@decultureware.com';

final class FeedbackError extends RuntimeException {
    public int $status;
    public function __construct(int $status, string $code) {
        parent::__construct($code);
        $this->status = $status;
    }
}

require_once __DIR__ . '/validation.php';
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/submission.php';
require_once __DIR__ . '/mail.php';
