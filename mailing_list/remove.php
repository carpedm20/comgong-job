<?php
  if ($_GET["email"]) {
    $email = $_GET["email"];
    $f = "../emails.txt";

    $lines = file($f, FILE_IGNORE_NEW_LINES);
    $indexCompleted = array_search($email, $lines);

    if($indexCompleted == FALSE) {
      echo count($lines);
      return;
    }
    unset($lines[$indexCompleted]);

    $new_emails = array_unique($lines);

    array_walk($new_emails, function(&$value, $key) { $value .= "\n"; });

    file_put_contents($f, $new_emails);
    echo count($new_emails);
  } else {
    echo "Need email";
  }
?>
