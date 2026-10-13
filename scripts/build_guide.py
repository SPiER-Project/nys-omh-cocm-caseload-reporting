"""Build the guide's web pages, web/docs/, from the Markdown in docs/.

    python3 scripts/build_guide.py           write web/docs/
    python3 scripts/build_guide.py --check   exit non-zero if web/docs/ is out of date

The guide stays Markdown in docs/; these pages are how clinics read it, next to the
calculator on GitHub Pages. docs/guide, docs/collecting and docs/reference are published,
each page at the same path with .html (docs/guide/start-here.md becomes
web/docs/guide/start-here.html, and a README.md becomes index.html). A link to another
published page points at its .html; a link to anything else in the repo (open questions,
the calculator's code, the rules) points at GitHub. The build fails if a link between
pages, or an #anchor, doesn't resolve, or if a page has no place in the site map
(scripts/sitenav.py), which sets the header, the breadcrumbs and next and previous.

The pages link the stylesheets in web/styles/ rather than carrying their own.

The Markdown converter covers what the guide uses: headings, paragraphs, lists (nested,
with continuation lines), block quotes, tables, fenced code, rules, links, bold, italics
and inline code. HTML comments, such as the <!--rule:...--> markers, are dropped and the
text between them kept. Standard library only, like the rest of the repo.
"""

import glob
import html
import os
import re
import sys

import sitenav

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
OUTPUT = os.path.join(ROOT, "web", "docs")
SECTIONS = ("guide", "collecting", "reference")
REPO = "https://github.com/SPiER-Project/nys-omh-cocm-caseload-reporting"

# ---------------------------------------------------------------------- pages and links


def published():
    """Every published Markdown file, as a path relative to docs/."""
    files = []
    for section in SECTIONS:
        files += glob.glob(os.path.join(DOCS, section, "**", "*.md"), recursive=True)
    return sorted(os.path.relpath(f, DOCS) for f in files)


def html_path(md):
    """docs-relative .md path -> web/docs-relative .html path."""
    return sitenav.html_name(md)


def slug(heading):
    """GitHub's anchor rule, as scripts/check_links.py uses it."""
    heading = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return heading.replace(" ", "-")


class Links:
    """Rewrites each link in a page, and records the ones to check once every page exists."""

    def __init__(self, pages):
        self.pages = set(pages)
        self.to_check = []  # (from page, target page, anchor)

    def rewrite(self, url, page):
        if re.match(r"[a-z]+:", url) or url.startswith("//"):
            return url
        path, _, anchor = url.partition("#")
        if not path:
            self.to_check.append((page, page, anchor))
            return url
        target = os.path.normpath(os.path.join(os.path.dirname(page), path))
        if target in self.pages:
            if anchor:
                self.to_check.append((page, target, anchor))
            here = os.path.dirname(html_path(page))
            rel = os.path.relpath(html_path(target), here or ".")
            return rel + (f"#{anchor}" if anchor else "")
        # Not published: the repo file on GitHub.
        repo_path = os.path.normpath(os.path.join("docs", os.path.dirname(page), path))
        if repo_path.startswith(".."):
            raise SystemExit(f"docs/{page}: link outside the repo: {url}")
        kind = "tree" if os.path.isdir(os.path.join(ROOT, repo_path)) else "blob"
        return f"{REPO}/{kind}/main/{repo_path}" + (f"#{anchor}" if anchor else "")


# ------------------------------------------------------------------------------- inline


def inline(text, page, links):
    codes = []

    def keep_code(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep_code, text)
    text = html.escape(text, quote=False)

    def link(m):
        href = html.escape(links.rewrite(html.unescape(m.group(2)), page))
        return f'<a href="{href}">{m.group(1)}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![*\w])\*([^*\s][^*]*?)\*(?![*\w])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


# -------------------------------------------------------------------------------- blocks

LIST_ITEM = re.compile(r"( *)([-*]|\d+\.) +(.*)")
TABLE_RULE = re.compile(r"\|? *:?-+:? *(\| *:?-+:? *)*\|? *$")


def cells(row):
    row = row.strip()
    row = row[1:] if row.startswith("|") else row
    row = row[:-1] if row.endswith("|") else row
    return [c.strip() for c in re.split(r"(?<!\\)\|", row)]


def starts_block(line):
    return (line.startswith(("#", ">", "|", "```")) or LIST_ITEM.match(line)
            or re.match(r"(---|\*\*\*)\s*$", line))


class Page:
    def __init__(self, page, links):
        self.page, self.links = page, links
        self.ids = {}

    def heading_id(self, text):
        base = slug(text)
        n = self.ids.get(base, 0)
        self.ids[base] = n + 1
        return base if n == 0 else f"{base}-{n}"

    def blocks(self, lines, tight=False):
        out, i = [], 0
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            m = re.match(r"(#{1,6}) +(.*?) *#*$", line)
            if m:
                level, text = len(m.group(1)), m.group(2)
                out.append(f'<h{level} id="{self.heading_id(text)}">'
                           f"{inline(text, self.page, self.links)}</h{level}>")
                i += 1
                continue
            if line.startswith("```"):
                j = i + 1
                while j < len(lines) and not lines[j].startswith("```"):
                    j += 1
                code = html.escape("\n".join(lines[i + 1:j]))
                out.append(f"<pre><code>{code}</code></pre>")
                i = j + 1
                continue
            if re.match(r"(---|\*\*\*)\s*$", line):
                out.append("<hr>")
                i += 1
                continue
            if line.startswith(">"):
                j = i
                while j < len(lines) and lines[j].startswith(">"):
                    j += 1
                inner = [re.sub(r"^> ?", "", l) for l in lines[i:j]]
                out.append(f"<blockquote>\n{self.blocks(inner)}\n</blockquote>")
                i = j
                continue
            if line.startswith("|") and i + 1 < len(lines) and TABLE_RULE.match(lines[i + 1]):
                head = cells(line)
                j = i + 2
                rows = []
                while j < len(lines) and lines[j].startswith("|"):
                    rows.append(cells(lines[j]))
                    j += 1
                th = "".join(f'<th scope="col">{inline(c, self.page, self.links)}</th>' for c in head)
                body = "\n".join(
                    "<tr>" + "".join(f"<td>{inline(c, self.page, self.links)}</td>" for c in r) + "</tr>"
                    for r in rows)
                out.append(f'<div class="table"><table>\n<thead><tr>{th}</tr></thead>\n'
                           f"<tbody>\n{body}\n</tbody>\n</table></div>")
                i = j
                continue
            if LIST_ITEM.match(line):
                html_list, i = self.list_(lines, i)
                out.append(html_list)
                continue
            j = i
            while j < len(lines) and lines[j].strip() and (j == i or not starts_block(lines[j])):
                j += 1
            text = inline(" ".join(l.strip() for l in lines[i:j]), self.page, self.links)
            out.append(text if tight else f"<p>{text}</p>")
            i = j
        return "\n".join(out)

    def list_(self, lines, i):
        first = LIST_ITEM.match(lines[i])
        indent = len(first.group(1))
        ordered = first.group(2)[0].isdigit()
        start = int(first.group(2)[:-1]) if ordered else 1
        items, loose = [], False
        while i < len(lines):
            m = LIST_ITEM.match(lines[i])
            if not m or len(m.group(1)) != indent or m.group(2)[0].isdigit() != ordered:
                break
            offset = len(lines[i]) - len(m.group(3))
            content = [m.group(3)]
            i += 1
            while i < len(lines):
                line = lines[i]
                if not line.strip():
                    nxt = next((l for l in lines[i + 1:] if l.strip()), "")
                    if len(nxt) - len(nxt.lstrip()) >= offset:
                        loose = loose or not LIST_ITEM.match(nxt)
                        content.append("")
                        i += 1
                        continue
                    break
                lead = len(line) - len(line.lstrip())
                if lead >= offset:
                    content.append(line[offset:])
                elif lead > indent and LIST_ITEM.match(line):
                    content.append(line[min(lead, offset):])
                elif lead > indent or not starts_block(line):
                    content.append(line.lstrip())  # a lazy continuation line
                else:
                    break
                i += 1
            items.append(content)
            if i < len(lines) and not lines[i].strip():
                nxt = next((l for l in lines[i:] if l.strip()), "")
                m2 = LIST_ITEM.match(nxt)
                if m2 and len(m2.group(1)) == indent and m2.group(2)[0].isdigit() == ordered:
                    loose = True
                    i = lines.index(nxt, i)
        tag = "ol" if ordered else "ul"
        attrs = f' start="{start}"' if ordered and start != 1 else ""
        body = "\n".join(f"<li>{self.blocks(item, tight=not loose)}</li>" for item in items)
        return f"<{tag}{attrs}>\n{body}\n</{tag}>", i


# ---------------------------------------------------------------------------------- page

STYLES = sitenav.STYLES + ("guide.css",)


def collapse_automation(body):
    """Fold a "For automation" section, which is for developers, so clinic readers can
    skip it. It runs to the next h2 or the end of the page."""
    m = re.search(r'<h2 id="(for-automation[\w-]*)">For automation</h2>\n?', body)
    if not m:
        return body
    end = body.find("\n<h2 ", m.end())
    end = len(body) if end == -1 else end
    return (body[:m.start()]
            + f'<details class="dev" id="{m.group(1)}">\n<summary><h2>For automation</h2> '
            '<span>For developers building their own report. Not needed to report.</span></summary>\n'
            + body[m.end():end] + "\n</details>" + body[end:])


def title_of(page):
    """A page's title as plain text, from its first # heading."""
    with open(os.path.join(DOCS, page)) as f:
        lines = f.read().split("\n")
    title = next((l[2:].strip() for l in lines if l.startswith("# ")), page)
    return re.sub(r"<[^>]+>", "", inline(title, page, Links([])))


def crumbs(page, here):
    """The trail above the title: the header section, then the group, if any."""
    order = {p: (s, g) for p, s, g in sitenav.reading_order()}
    section, group = order[page]
    trail = [(section, sitenav.landing(section))]
    if group:
        trail.append((group, sitenav.group_landing(section, group)))
    if trail[0][1] == page:
        return ""
    items = "".join(
        f"<li>{html.escape(label)}</li>" if target == page else
        f'<li><a href="{os.path.relpath(html_path(target), here)}">{html.escape(label)}</a></li>'
        for label, target in trail)
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{items}</ol></nav>\n'


def pager(page, here, titles):
    """Previous and next, in the site map's reading order."""
    order = [p for p, _, _ in sitenav.reading_order()]
    i = order.index(page)
    links = []
    for j, rel, label in ((i - 1, "prev", "Previous"), (i + 1, "next", "Next")):
        if 0 <= j < len(order):
            href = os.path.relpath(html_path(order[j]), here)
            links.append(f'<a class="{rel}" rel="{rel}" href="{href}"><small>{label}</small>'
                         f"<strong>{html.escape(titles[order[j]])}</strong></a>")
    return f'<nav class="pager" aria-label="Previous and next">\n{chr(10).join(links)}\n</nav>'


def render(page, links, titles):
    with open(os.path.join(DOCS, page)) as f:
        text = f.read()
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    body = collapse_automation(Page(page, links).blocks(text.split("\n")))
    here = os.path.dirname(html_path(page)) or "."
    up = os.path.relpath(OUTPUT, os.path.join(OUTPUT, here))  # to web/docs/
    web = os.path.join(up, "..")
    section = next(s for p, s, _ in sitenav.reading_order() if p == page)
    header = sitenav.header(
        os.path.join(web, "index.html"),
        lambda s: os.path.relpath(html_path(sitenav.landing(s)), here),
        section, sitenav.landing(section) == page)
    styles = "\n".join(f'<link rel="stylesheet" href="{web}/styles/{name}">' for name in STYLES)
    return f"""<!doctype html>
<!-- Built from docs/{page} by scripts/build_guide.py. Edit the Markdown, then rebuild. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titles[page]} · CoCM caseload reporting</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&display=swap">
{styles}
</head>
<body>
{header}
<main id="main">
{crumbs(page, here)}{body}
{pager(page, here, titles)}
</main>
<footer>
<p>This guide is an opinionated approach to the NYS Office of Mental Health's
Collaborative Care caseload metrics. It's an independent project, not an OMH product, and
every call it makes is provisional until approved.</p>
<p><a href="{REPO}/blob/main/docs/{page}">This page on GitHub</a></p>
</footer>
</body>
</html>
"""


def build():
    pages = published()
    mapped = [p for p, _, _ in sitenav.reading_order()]
    missing = sorted(set(pages) - set(mapped))
    gone = sorted(set(mapped) - set(pages))
    doubled = sorted({p for p in mapped if mapped.count(p) > 1})
    if missing or gone or doubled:
        raise SystemExit("scripts/sitenav.py doesn't match docs/: "
                         + "; ".join(f"{what}: {', '.join(ps)}" for what, ps in (
                             ("not in the site map", missing), ("no such page", gone),
                             ("listed twice", doubled)) if ps))
    links = Links(pages)
    titles = {p: title_of(p) for p in pages}
    out = {html_path(p): render(p, links, titles) for p in pages}
    ids = {}
    for p in pages:
        ids[p] = set(re.findall(r' id="([^"]+)"', out[html_path(p)]))
    broken = [f"docs/{src}: no #{anchor} in docs/{dst}"
              for src, dst, anchor in links.to_check if anchor not in ids[dst]]
    if broken:
        raise SystemExit("\n".join(broken))
    return out


def existing():
    found = {}
    for path in glob.glob(os.path.join(OUTPUT, "**", "*.html"), recursive=True):
        with open(path) as f:
            found[os.path.relpath(path, OUTPUT)] = f.read()
    return found


def main(argv):
    pages = build()
    if "--check" in argv:
        if existing() != pages:
            print("web/docs/ is out of date; run python3 scripts/build_guide.py")
            return 1
        print(f"web/docs/ is up to date ({len(pages)} pages)")
        return 0
    for path in set(existing()) - set(pages):
        os.remove(os.path.join(OUTPUT, path))
    for path, text in pages.items():
        os.makedirs(os.path.dirname(os.path.join(OUTPUT, path)), exist_ok=True)
        with open(os.path.join(OUTPUT, path), "w") as f:
            f.write(text)
    print(f"wrote {len(pages)} pages to web/docs/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
