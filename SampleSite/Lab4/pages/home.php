<?php
// Load latest article
$dataPath = __DIR__ . '/../json/articles.json';
$articles = json_decode(file_get_contents($dataPath), true) ?? [];
$latest = end($articles);
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kenneth Kang | Home</title>
  <link rel="stylesheet" href="../css/base.css">
  <link rel="stylesheet" href="../css/index.css">
</head>
<body>
  <nav>
    <ul>
      <li><a href="../index.php?page=home" class="active">Home</a></li>
      <li><a href="../index.php?page=articles">Blog</a></li>
    </ul>
  </nav>

  <div class="layout">
    <main>
      <div class="content">
        <img id="profile" src="../Photos/KennethPhoto.jpg" alt="Kenneth Kang">
        <h1>Kenneth Kang</h1>
        <p>Computer Science and Engineering student at SCU.</p>
        <div class="socials">
          <a href="https://www.linkedin.com/in/kennykennethkkang/" target="_blank">
            <img src="../Photos/Linkedin.png" alt="LinkedIn" width="50">
          </a>
          <a href="https://instagram.com/kennykennethkkang/" target="_blank">
            <img src="../Photos/Instagram.png" alt="Instagram" width="50">
          </a>
        </div>
      </div>
    </main>

    <aside>
      <div class="content">
        <h1><a href="../index.php?page=article&id=<?= $latest[
            "id"
        ] ?>"><?= htmlspecialchars($latest["title"]) ?></a></h1>
        <div>
          <?php foreach ($latest["tags"] as $tag): ?>
            <span class="tag"><?= htmlspecialchars($tag) ?></span>
          <?php endforeach; ?>
        </div>
        <?= $latest["content"] ?>
        <a href="../index.php?page=article&id=<?= $latest[
            "id"
        ] ?>" class="button">View Article</a>
        <a href="../index.php?page=articles" class="button">View All</a>
      </div>
    </aside>
  </div>

  <footer>Kenneth Kang &copy; 2025</footer>
</body>
</html>
