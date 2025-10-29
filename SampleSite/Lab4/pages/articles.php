<?php
$dataPath = __DIR__ . "/../json/articles.json";
$articles = json_decode(file_get_contents($dataPath), true) ?? [];
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="../css/base.css">
  <link rel="stylesheet" href="../css/articles.css">
  <script src="../js/articles.js" defer></script>
</head>
<body>
  <nav>
    <ul>
      <li><a href="../index.php?page=home">Home</a></li>
      <li><a href="../index.php?page=articles" class="active">Blog</a></li>
    </ul>
  </nav>

  <header>
    <input type="text" placeholder="Search tags...">
    <div class="tag-holder"></div>
  </header>

  <main>
    <?php foreach ($articles as $article): ?>
      <article class="article-card">
        <h2><a href="../index.php?page=article&id=<?= $article[
            "id"
        ] ?>"><?= htmlspecialchars($article["title"]) ?></a></h2>
        <div>
          <?php foreach ($article["tags"] as $tag): ?>
            <span class="tag"><?= htmlspecialchars($tag) ?></span>
          <?php endforeach; ?>
        </div>
        <p><?= htmlspecialchars(
            mb_strimwidth(strip_tags($article["content"]), 0, 150, "...")
        ) ?></p>
      </article>
    <?php endforeach; ?>
  </main>

  <footer>Kenneth Kang &copy; 2025</footer>
</body>
</html>
