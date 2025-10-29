const includedTags = [];

function createTag(tagName) {
  const button = document.createElement("button");
  button.classList.add("tag");
  button.textContent = tagName;

  //remove tag on click
  button.addEventListener("click", () => {
    button.remove();
    const index = includedTags.indexOf(tagName);
    if (index !== -1) includedTags.splice(index, 1);
    hideArticles();
  });

  return button;
}

function hideArticles() {
  const articles = document.querySelectorAll("article");
  const includedArticles = [];

  if (includedTags.length === 0) {
    articles.forEach((article) => article.classList.remove("hidden"));
    return;
  }

  articles.forEach((article) => {
    const tags = article.querySelectorAll(".tag");
    tags.forEach((tag) => {
      const tagText = tag.textContent.trim().toLowerCase();
      if (includedTags.includes(tagText)) {
        if (!includedArticles.includes(article)) {
          includedArticles.push(article);
        }
      }
    });
  });

  articles.forEach((article) => {
    if (includedArticles.includes(article)) {
      article.classList.remove("hidden");
    } else {
      article.classList.add("hidden");
    }
  });
}

function addSearchTerm(term) {
  const sanitizedTerm = term.trim().toLowerCase();
  if (!sanitizedTerm || includedTags.includes(sanitizedTerm)) return;

  includedTags.push(sanitizedTerm);
  const button = createTag(sanitizedTerm);
  document.querySelector(".tag-holder").prepend(button);
  hideArticles();
}

function initialize() {
  const params = new URLSearchParams(window.location.search);
  const tags = params.getAll("tag");

  tags.forEach((tag) => {
    console.log(tag);
    addSearchTerm(tag);
  });

  const input = document.querySelector("input[type='text']");
  input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      addSearchTerm(input.value);
      input.value = "";
    }
  });
}

document.addEventListener("DOMContentLoaded", initialize);
