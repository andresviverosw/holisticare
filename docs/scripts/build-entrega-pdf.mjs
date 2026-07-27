/**
 * Build docs/entrega-final-capstone.pdf from Markdown + Mermaid via Playwright Chromium.
 *
 * Usage (repo root):
 *   node docs/scripts/build-entrega-pdf.mjs
 *
 * Requires: Node 22+, Playwright browsers installed in frontend/
 *   cd frontend && npx playwright install chromium
 */
import { createRequire } from "node:module";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { spawnSync } from "node:child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "../..");
const docsDir = path.join(repoRoot, "docs");
const mdPath = path.join(docsDir, "entrega-final-capstone.md");
const outPdf = path.join(docsDir, "entrega-final-capstone.pdf");
const outHtml = path.join(docsDir, "entrega-final-capstone.html");

const require = createRequire(path.join(repoRoot, "frontend/package.json"));

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function markdownToHtml(md) {
  // Lightweight converter tuned for this delivery doc (tables, mermaid, images, headings).
  const lines = md.replace(/\r\n/g, "\n").split("\n");
  const html = [];
  let i = 0;
  let inCode = false;
  let codeLang = "";
  let codeBuf = [];
  let inUl = false;
  let inTable = false;
  let tableRows = [];

  const closeLists = () => {
    if (inUl) {
      html.push("</ul>");
      inUl = false;
    }
  };
  const flushTable = () => {
    if (!inTable) return;
    html.push("<table>");
    tableRows.forEach((row, idx) => {
      const tag = idx === 0 ? "th" : "td";
      if (idx === 1 && row.every((c) => /^[-: ]+$/.test(c))) return;
      html.push("<tr>");
      row.forEach((cell) => html.push(`<${tag}>${inline(cell)}</${tag}>`));
      html.push("</tr>");
    });
    html.push("</table>");
    inTable = false;
    tableRows = [];
  };

  const inline = (text) => {
    let t = escapeHtml(text);
    t = t.replace(/`([^`]+)`/g, "<code>$1</code>");
    t = t.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    t = t.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
    return t;
  };

  while (i < lines.length) {
    const line = lines[i];

    if (line.startsWith("```")) {
      if (!inCode) {
        closeLists();
        flushTable();
        inCode = true;
        codeLang = line.slice(3).trim();
        codeBuf = [];
      } else {
        inCode = false;
        const body = codeBuf.join("\n");
        if (codeLang === "mermaid") {
          html.push(`<pre class="mermaid">${escapeHtml(body)}</pre>`);
        } else {
          html.push(`<pre><code>${escapeHtml(body)}</code></pre>`);
        }
        codeLang = "";
        codeBuf = [];
      }
      i += 1;
      continue;
    }
    if (inCode) {
      codeBuf.push(line);
      i += 1;
      continue;
    }

    if (line.startsWith("|")) {
      closeLists();
      inTable = true;
      const cells = line
        .split("|")
        .slice(1, -1)
        .map((c) => c.trim());
      tableRows.push(cells);
      i += 1;
      continue;
    }
    if (inTable) flushTable();

    if (/^#{1,3} /.test(line)) {
      closeLists();
      const level = line.match(/^#+/)[0].length;
      html.push(`<h${level}>${inline(line.replace(/^#+\s+/, ""))}</h${level}>`);
      i += 1;
      continue;
    }

    if (line.startsWith("- ") || line.startsWith("* ")) {
      if (!inUl) {
        html.push("<ul>");
        inUl = true;
      }
      html.push(`<li>${inline(line.slice(2))}</li>`);
      i += 1;
      continue;
    }
    closeLists();

    const img = line.match(/^!\[([^\]]*)\]\(([^)]+)\)/);
    if (img) {
      const src = img[2].startsWith("http")
        ? img[2]
        : "/" + img[2].replace(/^\.\//, "");
      html.push(`<figure><img src="${src}" alt="${escapeHtml(img[1])}" /><figcaption>${inline(img[1])}</figcaption></figure>`);
      i += 1;
      continue;
    }

    if (line.trim() === "---") {
      html.push("<hr />");
      i += 1;
      continue;
    }

    if (line.trim() === "") {
      i += 1;
      continue;
    }

    if (line.startsWith("> ")) {
      html.push(`<blockquote>${inline(line.slice(2))}</blockquote>`);
      i += 1;
      continue;
    }

    html.push(`<p>${inline(line)}</p>`);
    i += 1;
  }
  closeLists();
  flushTable();
  return html.join("\n");
}

function ensureChromium() {
  const r = spawnSync(
    process.platform === "win32" ? "npx.cmd" : "npx",
    ["playwright", "install", "chromium"],
    { cwd: path.join(repoRoot, "frontend"), stdio: "inherit", shell: process.platform === "win32" },
  );
  if (r.status !== 0) {
    throw new Error("Failed to install Playwright Chromium");
  }
}

async function main() {
  const md = await fs.readFile(mdPath, "utf8");
  const body = markdownToHtml(md);
  const html = `<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <title>HolistiCare — Entrega final</title>
  <style>
    @page { size: A4; margin: 16mm 14mm; }
    body { font-family: "Segoe UI", system-ui, sans-serif; font-size: 11pt; line-height: 1.45; color: #212529; }
    h1 { font-size: 20pt; color: #1f7d4b; page-break-after: avoid; }
    h2 { font-size: 14pt; color: #184f32; margin-top: 1.4em; page-break-after: avoid; }
    h3 { font-size: 12pt; color: #343a40; page-break-after: avoid; }
    table { border-collapse: collapse; width: 100%; margin: 0.8em 0; font-size: 9.5pt; }
    th, td { border: 1px solid #dee2e6; padding: 4px 6px; vertical-align: top; }
    th { background: #f0faf4; }
    code { font-family: ui-monospace, Consolas, monospace; font-size: 0.9em; background: #f1f3f5; padding: 0 3px; }
    pre { background: #f8f9fa; border: 1px solid #e9ecef; padding: 10px; overflow: hidden; font-size: 8.5pt; }
    pre.mermaid { background: #fff; border: 1px solid #e9ecef; }
    figure { margin: 1em 0; page-break-inside: avoid; }
    img { max-width: 100%; height: auto; border: 1px solid #dee2e6; }
    figcaption { font-size: 9pt; color: #868e96; margin-top: 4px; }
    blockquote { border-left: 3px solid #52b880; margin: 0.8em 0; padding: 0.2em 0.8em; color: #495057; }
    a { color: #1f7d4b; }
    hr { border: none; border-top: 1px solid #dee2e6; margin: 1.5em 0; }
  </style>
</head>
<body>
${body}
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({ startOnLoad: false, theme: "neutral", securityLevel: "loose" });
  mermaid.run().then(function () {
    document.documentElement.dataset.mermaidReady = "1";
  }).catch(function () {
    document.documentElement.dataset.mermaidReady = "1";
  });
</script>
</body>
</html>`;

  await fs.writeFile(outHtml, html, "utf8");

  let chromium;
  try {
    ({ chromium } = require("playwright"));
  } catch {
    ensureChromium();
    ({ chromium } = require("playwright"));
  }

  // Serve docs/ over HTTP so Mermaid CDN modules and local image paths work.
  const { createServer } = await import("node:http");
  const mime = {
    ".html": "text/html; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".css": "text/css",
    ".js": "text/javascript",
    ".md": "text/markdown",
  };
  const server = createServer(async (req, res) => {
    try {
      const urlPath = decodeURIComponent((req.url || "/").split("?")[0]);
      const rel = urlPath === "/" ? "/entrega-final-capstone.html" : urlPath;
      const filePath = path.normalize(path.join(docsDir, rel.replace(/^\//, "")));
      if (!filePath.startsWith(docsDir)) {
        res.writeHead(403);
        res.end("Forbidden");
        return;
      }
      const data = await fs.readFile(filePath);
      res.writeHead(200, { "Content-Type": mime[path.extname(filePath)] || "application/octet-stream" });
      res.end(data);
    } catch {
      res.writeHead(404);
      res.end("Not found");
    }
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();
  const pageUrl = `http://127.0.0.1:${port}/entrega-final-capstone.html`;

  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(pageUrl, { waitUntil: "networkidle", timeout: 120000 });
  try {
    await page.waitForFunction(() => document.documentElement.dataset.mermaidReady === "1", null, {
      timeout: 90000,
    });
  } catch {
    console.warn("Mermaid render timed out; exporting PDF with fallback diagrams.");
  }
  await page.waitForTimeout(1000);
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const pdfTarget = outPdf;
  try {
    await page.pdf({
      path: pdfTarget,
      format: "A4",
      printBackground: true,
      margin: { top: "14mm", bottom: "14mm", left: "12mm", right: "12mm" },
    });
    console.log(`Wrote ${pdfTarget}`);
  } catch (err) {
    if (err && (err.code === "EBUSY" || String(err.message || "").includes("EBUSY"))) {
      const alt = path.join(docsDir, `entrega-final-capstone-${stamp}.pdf`);
      await page.pdf({
        path: alt,
        format: "A4",
        printBackground: true,
        margin: { top: "14mm", bottom: "14mm", left: "12mm", right: "12mm" },
      });
      console.warn(`PDF locked; wrote alternate file: ${alt}`);
    } else {
      throw err;
    }
  }
  await browser.close();
  server.close();
  console.log(`Also wrote intermediate HTML: ${outHtml}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
