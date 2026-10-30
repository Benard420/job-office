#!/usr/bin/env python3
"""Check every cover letter PDF in a folder: page count, dashes, banned phrases, requisition in text.

Usage: python3 check_letters.py job-office/letters
Needs pdfinfo/pdftotext (poppler) or the pypdf package.
"""
import os, re, subprocess, sys

BANNED = ["excited to apply", "great fit", "passionate", "leverage", "synergy", "fast paced", "fast-paced",
          "proven track record", "go above and beyond", "delve", "tapestry", "express my interest", "esteemed",
          "dynamic team"]


def text_and_pages(fp):
    try:
        pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", fp], capture_output=True, text=True).stdout).group(1))
        txt = subprocess.run(["pdftotext", fp, "-"], capture_output=True, text=True).stdout
        return txt, pages
    except Exception:
        from pypdf import PdfReader
        r = PdfReader(fp)
        return "\n".join(p.extract_text() or "" for p in r.pages), len(r.pages)


def main(folder):
    bad = 0
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith(".pdf"))
    for f in files:
        txt, pages = text_and_pages(os.path.join(folder, f))
        issues = []
        if pages != 1:
            issues.append(f"{pages} pages")
        if re.search("[–—]", txt):
            issues.append("dash")
        low = txt.lower()
        issues += [f"phrase '{b}'" for b in BANNED if b in low]
        req = f.split("_")[0]
        if req.isdigit() and req not in txt:
            issues.append(f"req {req} not in text")
        if issues:
            bad += 1
        print(("OK   " if not issues else "FIX  ") + f + ("" if not issues else "  -> " + ", ".join(issues)))
    print(f"{len(files)} checked, {bad} need attention")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "job-office/letters"))
