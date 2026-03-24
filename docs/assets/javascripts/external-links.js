document.addEventListener("DOMContentLoaded", () => {
  for (const link of document.querySelectorAll("a[href]")) {
    const href = link.getAttribute("href");

    if (!href || href.startsWith("#")) {
      continue;
    }

    try {
      const url = new URL(href, window.location.href);
      if (url.origin !== window.location.origin) {
        link.setAttribute("target", "_blank");
        link.setAttribute("rel", "noopener noreferrer");
      }
    } catch {
      // Ignore malformed URLs and leave the link unchanged.
    }
  }
});