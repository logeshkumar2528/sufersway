<?php
$randomNumbersURL = "https://message-53c5c-default-rtdb.firebaseio.com/random_numbers.json";
$statusURL = "https://message-53c5c-default-rtdb.firebaseio.com/status.json";
$hiDataURL = "https://message-53c5c-default-rtdb.firebaseio.com/hi.json";

function fetchFirebaseData($url) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FAILONERROR, true);
    $response = curl_exec($ch);
    if ($response === false) {
        curl_close($ch);
        return false;
    }
    curl_close($ch);
    return json_decode($response, true);
}

$randomNumbersData = fetchFirebaseData($randomNumbersURL);
$statusData = fetchFirebaseData($statusURL);
$hiData = fetchFirebaseData($hiDataURL);

if ($randomNumbersData === false || $statusData === false || $hiData === false) {
    echo json_encode(["error" => "Client is offline or Firebase is unreachable"]);
    exit;
}

$response = [
    "random_numbers" => $randomNumbersData ?: [],
    "status" => $statusData ?: [],
    "hi" => $hiData ?: []
];

header("Content-Type: application/json");
echo json_encode($response);
?>
