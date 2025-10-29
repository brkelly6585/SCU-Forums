<?php
$page = $_GET["page"] ?? "home";

switch ($page) {
    case "home":
        include __DIR__ . "/pages/home.php";
        break;
    case "articles":
        include __DIR__ . "/pages/articles.php";
        break;
    case "article":
        include __DIR__ . "/pages/article.php";
        break;
    default:
        http_response_code(404);
        echo "<p>Page not found.</p>";
}
?>
