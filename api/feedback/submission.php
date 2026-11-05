<?php
declare(strict_types=1);

function feedbackSaveState($file, array $state): void {
    $json = json_encode($state, JSON_THROW_ON_ERROR);
    rewind($file);
    if (!ftruncate($file, 0) || fwrite($file, $json) !== strlen($json) || !fflush($file)) {
        throw new FeedbackError(503, 'unavailable');
    }
}

/** The sender is injected in tests; tests never connect to a real mail server. */
function feedbackSubmit(array $data, array $config, string $origin, string $address, callable $sender): array {
    if (!in_array($origin, $config['allowed_origins'], true)) {
        throw new FeedbackError(403, 'forbidden');
    }
    $data = feedbackValidate($data);
    $file = fopen($config['state_dir'] . '/feedback-state.json', 'c+');
    if (!$file) { throw new FeedbackError(503, 'unavailable'); }
    // A single small-site lock covers quota and submission IDs, including SMTP.
    // Return promptly instead of tying up PHP workers while another send runs.
    if (!flock($file, LOCK_EX | LOCK_NB)) {
        fclose($file);
        throw new FeedbackError(503, 'busy');
    }
    try {
        $raw = stream_get_contents($file);
        $state = $raw === '' ? ['attempts'=>[], 'sent'=>[]] : json_decode($raw, true, 32, JSON_THROW_ON_ERROR);
        if (!is_array($state['attempts'] ?? null) || !is_array($state['sent'] ?? null)) {
            throw new FeedbackError(503, 'unavailable');
        }
        $now = time();
        $state['attempts'] = array_values(array_filter($state['attempts'], fn($x) => $x['time'] > $now - 3600));
        $state['sent'] = array_filter($state['sent'], fn($x) => $x['time'] > $now - 86400);
        $ipKey = hash_hmac('sha256', $address, $config['rate_secret']);
        $id = hash_hmac('sha256', $data['submission_id'], $config['rate_secret']);
        $fingerprint = hash_hmac('sha256', json_encode($data, JSON_THROW_ON_ERROR), $config['rate_secret']);
        if (isset($state['sent'][$id])) {
            if (!hash_equals($state['sent'][$id]['fingerprint'], $fingerprint)) {
                throw new FeedbackError(409, 'invalid');
            }
            return ['ok'=>true];
        }
        $recent = array_filter($state['attempts'], fn($x) => $x['ip'] === $ipKey && $x['time'] > $now - 600);
        if (count($recent) >= 5 || count($state['attempts']) >= 60) {
            throw new FeedbackError(429, 'rate_limited');
        }
        $state['attempts'][] = ['ip'=>$ipKey, 'time'=>$now];
        feedbackSaveState($file, $state);
        // No personal data is stored in the state file, only keyed hashes/time.
        $sender($data, $config);
        $state['sent'][$id] = ['fingerprint'=>$fingerprint, 'time'=>$now];
        feedbackSaveState($file, $state);
        return ['ok'=>true];
    } finally {
        flock($file, LOCK_UN);
        fclose($file);
    }
}

