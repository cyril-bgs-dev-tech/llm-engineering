#!/usr/bin/env python3
"""Contrôle de mise en page de la présentation : débordement des diapositives, texte qui chevauche le pied de page ou un autre texte, texte hors cadre.
Usage : check_deck_layout.py [fichier.html] [--shots DOSSIER] ; code de sortie 1 si un défaut est trouvé. Nécessite playwright et un navigateur installé (python3 système)."""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "docs/presentation/projet_llm_finetuning.html"
MIN_OVERLAP_PX = 6  # côté minimal du rectangle d'intersection pour compter comme chevauchement

PROBE = r"""() => {
  const slide = document.querySelector('.slide.active');
  const sr = slide.getBoundingClientRect();
  const foot = slide.querySelector('.foot');
  const footTop = foot ? foot.getBoundingClientRect().top : sr.bottom;
  const own = el => [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 0);
  const els = [...slide.querySelectorAll('*')].filter(el => own(el) && getComputedStyle(el).visibility !== 'hidden');
  const label = el => (el.className && typeof el.className === 'string' ? el.tagName.toLowerCase() + '.' + el.className.split(' ')[0] : el.tagName.toLowerCase()) + ' « ' + el.textContent.trim().slice(0, 40) + ' »';
  const rects = els.map(el => ({el, r: el.getBoundingClientRect(), inFoot: !!el.closest('.foot')}));
  const out = [];
  for (const c of slide.querySelectorAll('.card, .track')) if (c.getBoundingClientRect().bottom > footTop - 4) out.push('cadre trop bas, collé au pied de page : ' + label(c) + ' (bas ' + Math.round(c.getBoundingClientRect().bottom) + ', pied ' + Math.round(footTop) + ')');
  if (foot && foot.getBoundingClientRect().height > 30) out.push('pied de page sur plusieurs lignes (' + Math.round(foot.getBoundingClientRect().height) + ' px) : le raccourcir');
  for (const h of slide.querySelectorAll('h1, h2')) {
    const w = document.createTreeWalker(h, NodeFilter.SHOW_TEXT); const words = [];
    while (w.nextNode()) for (const m of w.currentNode.textContent.matchAll(/\S+/g)) { const r = document.createRange(); r.setStart(w.currentNode, m.index); r.setEnd(w.currentNode, m.index + m[0].length); words.push({t: m[0], top: r.getBoundingClientRect().top}); }
    if (words.length > 2 && words[words.length - 1].top > words[words.length - 2].top + 5) out.push('titre avec dernier mot seul sur sa ligne « ' + words[words.length - 1].t + ' » : ' + h.textContent.trim().slice(0, 40));
  }
  if (slide.scrollHeight > slide.clientHeight + 1) out.push('débordement vertical de la diapositive : ' + slide.scrollHeight + ' > ' + slide.clientHeight);
  for (const {el, r, inFoot} of rects) {
    if (r.right > sr.right - 40) out.push('texte trop près ou hors du bord droit : ' + label(el));
    if (!inFoot && r.bottom > footTop + 1) out.push('texte sur le pied de page : ' + label(el) + ' (bas ' + Math.round(r.bottom) + ', pied ' + Math.round(footTop) + ')');
    if (el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflow !== 'visible') out.push('texte coupé : ' + label(el));
  }
  for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) {
    const a = rects[i], b = rects[j];
    if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
    const w = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left), h = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
    if (w > __MIN__ && h > __MIN__) out.push('chevauchement : ' + label(a.el) + ' avec ' + label(b.el) + ' (' + Math.round(w) + 'x' + Math.round(h) + ' px)');
  }
  return out;
}""".replace("__MIN__", str(MIN_OVERLAP_PX))


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    shots = Path(sys.argv[sys.argv.index("--shots") + 1]) if "--shots" in sys.argv else None
    if shots is not None:
        args = [a for a in args if a != str(shots)]
        shots.mkdir(parents=True, exist_ok=True)
    deck = Path(args[0]).resolve() if args else DECK
    defects = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(deck.as_uri())
        page.wait_for_timeout(1500)
        fonts = page.evaluate("() => [...document.fonts].map(f => f.family + ':' + f.status).join(', ')")
        print("polices :", fonts or "aucune police web chargée (polices de repli : les largeurs peuvent différer)")
        n = page.evaluate("() => document.querySelectorAll('.slide').length")
        for k in range(n):
            page.goto(f"{deck.as_uri()}#{k + 1}")
            page.reload()
            page.wait_for_timeout(700)
            found = page.evaluate(PROBE)
            if shots is not None:
                page.screenshot(path=str(shots / f"slide_{k + 1:02d}.png"))
            for msg in found:
                print(f"diapositive {k + 1} : {msg}")
            defects += len(found)
        browser.close()
    print(f"{n} diapositives, {defects} défaut(s)")
    return 1 if defects else 0


if __name__ == "__main__":
    sys.exit(main())
