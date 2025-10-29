// Scroll Save/Restore
const scrollKey = `scroll-${document.title}`;

function saveScroll() {
  localStorage.setItem(scrollKey, window.scrollY);
}

function restoreScroll() {
  const saved = localStorage.getItem(scrollKey);
  if (saved && !isNaN(saved)) {
    window.scrollTo(0, parseInt(saved));
  }
}

window.addEventListener("load", restoreScroll);
window.addEventListener("scroll", () => {
  clearTimeout(window.__scrollTimeout);
  window.__scrollTimeout = setTimeout(saveScroll, 100);
});

// Highlight Selection
document.querySelector("article").addEventListener("mouseup", () => {
  const selection = window.getSelection();
  if (!selection.rangeCount) return;

  const selectedText = selection.toString().trim();
  if (!selectedText) return;

  const range = selection.getRangeAt(0);
  const article = document.querySelector("article");

  const start = range.startContainer;
  const end = range.endContainer;

  const startP =
    start.nodeType === 1
      ? start.closest("p")
      : start.parentElement.closest("p");
  const endP =
    end.nodeType === 1 ? end.closest("p") : end.parentElement.closest("p");

  if (!startP || !endP || startP !== endP || !article.contains(startP)) {
    console.warn("Highlight must stay within a single <p>");
    selection.removeAllRanges();
    return;
  }

  // Create highlight span
  const highlightSpan = document.createElement("span");
  highlightSpan.classList.add("yellow-highlight");

  try {
    // Use extractContents for clean insert
    const contents = range.extractContents();
    highlightSpan.appendChild(contents);
    range.insertNode(highlightSpan);

    // Click to remove span, restore text in the same <p>
    highlightSpan.addEventListener("click", () => {
      const text = document.createTextNode(highlightSpan.textContent);
      const parent = highlightSpan.parentNode;
      parent.replaceChild(text, highlightSpan);
      parent.normalize(); // Merge text nodes
    });
  } catch (err) {
    console.warn("Highlight failed:", err);
  }

  selection.removeAllRanges();
});

// Download highlights
function downloadHighlighted() {
  const highlights = document.querySelectorAll(".yellow-highlight");
  if (highlights.length === 0) {
    alert("No highlighted text");
    return;
  }

  const lines = Array.from(highlights).map(
    (span) => `- ${span.textContent.trim()}`
  );
  const textBlob = new Blob([lines.join("\n")], { type: "text/plain" });

  const link = document.createElement("a");
  link.href = URL.createObjectURL(textBlob);
  link.download = "highlighted-text.txt";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(link.href);
}

// Page top function
function scrollToTop() {
  window.scrollTo({
    top: 0,
  });
}