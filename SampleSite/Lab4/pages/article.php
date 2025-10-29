<?php
// Load article data
$dataPath = __DIR__ . "/../json/articles.json";
$articles = json_decode(file_get_contents($dataPath), true) ?? [];
$id = isset($_GET["id"]) ? intval($_GET["id"]) : 0;

// Find the current article
$article = null;
foreach ($articles as $a) {
    if ($a["id"] === $id) {
        $article = $a;
        break;
    }
}

// Handle invalid IDs
if (!$article) {
    echo "<p>Article not found.</p>";
    exit();
}
?>

<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>
    <?= htmlspecialchars($article["title"]) ?>
  </title>
  <link rel="stylesheet" href="../css/base.css">
  <link rel="stylesheet" href="../css/article.css">
  <script src="../js/article.js" defer></script>
</head>

<body>
  <!-- Navigation -->
  <nav>
    <ul>
      <li><a href="../index.php?page=home">Home</a></li>
      <li><a href="../index.php?page=articles">Blog</a></li>
    </ul>
  </nav>

  <main>
    <!-- Download highlighted text button -->
    <button class="download-highlight-btn" onclick="downloadHighlighted()">Download Highlighted</button>

    <article>
      <h1>
        <?= htmlspecialchars($article["title"]) ?>
      </h1>

      <div>
        <?php foreach ($article["tags"] as $tag): ?>
        <span class="tag">
          <?= htmlspecialchars($tag) ?>
        </span>
        <?php endforeach; ?>
      </div>

      <!-- Article body -->
      <?= $article["content"] ?>

      <!-- Navigation footer -->
      <footer class="article-footer">
        <?php
        // Looping Prev/Next Logic
        $total = count($articles);
        $prev = $id <= 1 ? $total : $id - 1;
        $next = $id >= $total ? 1 : $id + 1;
        ?>
        <div>
          <a href="#" class="button" onclick="scrollToTop()">Page Top</a>
          <a href="../index.php?page=article&id=<?= $prev ?>" class="button">Prev</a>
          <a href="../index.php?page=article&id=<?= $next ?>" class="button">Next</a>
        </div>
        <button id="downloadPage" class="button">Download Page</button>
      </footer>
      <!--Download full page -->
      <script>
  document.addEventListener("DOMContentLoaded", function () {
    const downloadButton = document.getElementById("downloadPage");
    if (!downloadButton) return;

    downloadButton.addEventListener("click", function (e) {
      e.preventDefault();

      // Grab all visible text inside the article element
      const article = document.querySelector("article");
      if (!article) {
        alert("Article content not found.");
        return;
      }

      const textContent = article.innerText.trim();

      // Create a Blob (text file in memory)
      const blob = new Blob([textContent], { type: "text/plain" });

      // Create a temporary link element
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "article.txt";

      // Programmatically trigger the download
      document.body.appendChild(link);
      link.click();

      // Clean up
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
    });
  });
</script>

    </article>
  </main>

  <footer>
    Kenneth Kang &copy; 2025
  </footer>
</body>

</html>