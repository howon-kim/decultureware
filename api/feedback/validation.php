<?php
declare(strict_types=1);

function feedbackField(array $data, string $key, int $limit, bool $required = true): string {
    $value = $data[$key] ?? '';
    if (!is_string($value) || strlen($value) > $limit || !preg_match('//u', $value)) {
        throw new FeedbackError(422, 'invalid');
    }
    $value = trim($value);
    if (($required && $value === '') || str_contains($value, "\0")) {
        throw new FeedbackError(422, 'invalid');
    }
    return $value;
}

function feedbackValidate(array $data): array {
    $result = [];
    foreach (['app'=>40, 'kind'=>30, 'platform'=>20, 'email'=>254, 'message'=>12000, 'submission_id'=>64] as $key=>$limit) {
        $result[$key] = feedbackField($data, $key, $limit);
    }
    $result['version'] = feedbackField($data, 'version', 80, false);
    if ($result['app'] !== 'bananacal'
        || !in_array($result['kind'], ['bug', 'idea', 'question', 'other'], true)
        || !in_array($result['platform'], ['ios', 'macos', 'other'], true)
        || !filter_var($result['email'], FILTER_VALIDATE_EMAIL)
        || preg_match('/[\r\n]/', $result['email'] . $result['version'])
        || !preg_match('/^[a-f0-9-]{32,64}$/i', $result['submission_id'])
        || feedbackField($data, 'website', 200, false) !== '') {
        throw new FeedbackError(422, 'invalid');
    }
    return $result;
}

