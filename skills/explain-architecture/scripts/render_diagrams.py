#!/usr/bin/env python3
"""Render Mermaid diagram sources to PNG and bundle them into a single PDF.

Usage:
    python3 render_diagrams.py <output-dir>

Expects <output-dir>/src/*.mmd, produces:
    <output-dir>/diagrams/<name>.png   (one per .mmd)
    <output-dir>/architecture.pdf      (all diagrams + captions)
    <output-dir>/architecture.html     (fallback when no renderer is available)

Renderer resolution order:
    1. `mmdc` on PATH (mermaid-cli installed globally)
    2. `npx -y @mermaid-js/mermaid-cli` (needs node, downloads on first use)
    3. Self-contained HTML fallback (open in a browser and print to PDF)

PDF assembly order:
    1. mmdc direct PDF per diagram, merged if pypdf is available
    2. Pillow: PNGs -> single PDF
    3. HTML fallback only

Exit code 0 if PNGs or the HTML fallback were produced; prints a summary either way.
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MERMAID_ESM = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]


def find_browser():
    """System Chrome/Chromium for puppeteer, so mmdc works without a
    'npx puppeteer browsers install' step."""
    for p in CHROME_PATHS:
        if Path(p).exists():
            return p
    for name in ("google-chrome", "google-chrome-stable", "chromium",
                 "chromium-browser", "msedge", "brave-browser"):
        found = shutil.which(name)
        if found:
            return found
    return None


def puppeteer_config_args():
    browser = find_browser()
    if not browser:
        return []
    cfg = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, prefix="puppeteer-")
    json.dump({"executablePath": browser}, cfg)
    cfg.close()
    return ["-p", cfg.name]


def find_renderer():
    if shutil.which("mmdc"):
        return ["mmdc"]
    if shutil.which("npx"):
        try:
            probe = subprocess.run(
                ["npx", "-y", "@mermaid-js/mermaid-cli", "--version"],
                capture_output=True, text=True, timeout=300,
            )
            if probe.returncode == 0:
                return ["npx", "-y", "@mermaid-js/mermaid-cli"]
        except subprocess.TimeoutExpired:
            print("npx mermaid-cli probe timed out; using HTML fallback")
    return None


def read_caption(mmd_path: Path) -> str:
    for line in mmd_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*%%\s*caption:\s*(.+)", line)
        if m:
            return m.group(1).strip()
    return ""


def title_from_name(mmd_path: Path) -> str:
    stem = re.sub(r"^\d+[-_]?", "", mmd_path.stem)
    return stem.replace("-", " ").replace("_", " ").title()


def render_pngs(renderer, sources, diagrams_dir: Path):
    ok, failed = [], []
    pconfig = puppeteer_config_args()
    for src in sources:
        out = diagrams_dir / (src.stem + ".png")
        cmd = renderer + pconfig + ["-i", str(src), "-o", str(out),
                                    "-b", "white", "-s", "3", "--quiet"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired:
            failed.append((src, "render timed out"))
            continue
        if r.returncode == 0 and out.exists() and out.stat().st_size > 0:
            ok.append(out)
        else:
            failed.append((src, (r.stderr or r.stdout).strip()[-400:]))
    return ok, failed


def build_pdf_with_pillow(sources, diagrams_dir: Path, pdf_path: Path) -> bool:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False

    PAGE_W, PAGE_H, MARGIN = 2480, 3508, 140  # A4 @ 300dpi
    font = header_font = None
    for fp in ("/System/Library/Fonts/Helvetica.ttc",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(fp).exists():
            try:
                font = ImageFont.truetype(fp, 44)
                header_font = ImageFont.truetype(fp, 64)
                break
            except OSError:
                pass
    if font is None:
        font = header_font = ImageFont.load_default()

    pages = []
    for src in sources:
        png = diagrams_dir / (src.stem + ".png")
        if not png.exists():
            continue
        page = Image.new("RGB", (PAGE_W, PAGE_H), "white")
        draw = ImageDraw.Draw(page)
        draw.text((MARGIN, MARGIN), title_from_name(src),
                  fill="black", font=header_font)
        y = MARGIN + 120

        caption = read_caption(src)
        if caption:
            words, line, lines = caption.split(), "", []
            for w in words:
                trial = (line + " " + w).strip()
                if draw.textlength(trial, font=font) > PAGE_W - 2 * MARGIN:
                    lines.append(line)
                    line = w
                else:
                    line = trial
            lines.append(line)
            for ln in lines:
                draw.text((MARGIN, y), ln, fill="#333333", font=font)
                y += 58
        y += 60

        img = Image.open(png).convert("RGB")
        max_w, max_h = PAGE_W - 2 * MARGIN, PAGE_H - y - MARGIN
        scale = min(max_w / img.width, max_h / img.height, 1.0)
        img = img.resize((max(1, int(img.width * scale)),
                          max(1, int(img.height * scale))))
        page.paste(img, ((PAGE_W - img.width) // 2, y))
        pages.append(page)

    if not pages:
        return False
    pages[0].save(pdf_path, save_all=True, append_images=pages[1:],
                  resolution=300.0)
    return True


def write_html_fallback(sources, html_path: Path):
    blocks = []
    for src in sources:
        code = src.read_text(encoding="utf-8")
        caption = read_caption(src)
        blocks.append(
            f"<section><h2>{title_from_name(src)}</h2>"
            f"<p class='cap'>{caption}</p>"
            f"<pre class='mermaid'>\n{code}\n</pre></section>"
        )
    html_path.write_text(f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Architecture</title>
<style>
 body{{font-family:-apple-system,Segoe UI,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem}}
 section{{page-break-after:always;margin-bottom:3rem}}
 h2{{border-bottom:2px solid #ddd;padding-bottom:.3rem}}
 .cap{{color:#444}}
 @media print{{body{{max-width:none}}}}
</style></head><body>
<h1>Architecture</h1>
<p>Open this file in a browser. Diagrams render automatically (needs internet once).
Use <b>Print &rarr; Save as PDF</b> to export.</p>
{''.join(blocks)}
<script type="module">
import mermaid from "{MERMAID_ESM}";
mermaid.initialize({{startOnLoad:true, theme:"neutral"}});
</script></body></html>""", encoding="utf-8")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    out_dir = Path(sys.argv[1]).resolve()
    src_dir = out_dir / "src"
    diagrams_dir = out_dir / "diagrams"
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    sources = sorted(src_dir.glob("*.mmd"))
    if not sources:
        print(f"ERROR: no .mmd files in {src_dir}")
        sys.exit(1)

    renderer = find_renderer()
    pngs, failed = ([], [(s, "no renderer") for s in sources])
    if renderer:
        print(f"renderer: {' '.join(renderer)}")
        pngs, failed = render_pngs(renderer, sources, diagrams_dir)

    pdf_path = out_dir / "architecture.pdf"
    pdf_ok = bool(pngs) and build_pdf_with_pillow(sources, diagrams_dir, pdf_path)

    html_path = out_dir / "architecture.html"
    if not pngs or not pdf_ok:
        write_html_fallback(sources, html_path)

    print(f"\nsources : {len(sources)}")
    print(f"pngs    : {len(pngs)} -> {diagrams_dir}" if pngs else "pngs    : none")
    for src, err in failed:
        print(f"  FAILED {src.name}: {err}")
    if pdf_ok:
        print(f"pdf     : {pdf_path}")
    else:
        print(f"pdf     : not built directly — open {html_path} in a browser "
              f"and Print -> Save as PDF")
    sys.exit(0 if (pngs or html_path.exists()) else 1)


if __name__ == "__main__":
    main()
