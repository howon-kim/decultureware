<?php
// Copy to /volume2/web_privates/feedback.php.
// Set real credentials only on the NAS, outside every public web folder.
return [
    'allowed_origins' => ['https://YOUR-WEBSITE.example'],
    'smtp_host' => 'mail.howon.kim',
    'smtp_port' => 587,
    'smtp_security' => 'tls',
    'smtp_username' => 'YOUR-MAILPLUS-LOGIN',
    'smtp_password' => 'REPLACE-ON-THE-NAS',
    'from_email' => 'feedback@decultureware.com',
    'state_dir' => '/volume2/web_privates/state',
    'rate_secret' => 'REPLACE-WITH-A-RANDOM-SECRET-AT-LEAST-32-CHARACTERS',
];
