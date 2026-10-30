#!/usr/bin/env python3
"""Job Office tracker.

Keeps job-office/jobs.csv, applications.csv and outreach.csv, applies status rules,
and builds tracker.xlsx, dashboard.html and tracker_rows.json.

Commands:
  init        --office DIR
  known       --office DIR                      print known job_ids and reqs
  add-jobs    --office DIR --file JSON          add new jobs (list of dicts, jobs.csv columns)
  status      --office DIR --job ID --status S [--note TEXT]
  applied     --office DIR --job ID [--letter F] [--cv F] [--answers T] [--confirmation T] [--notes T]
  outreach    --office DIR --job ID --contact NAME --channel C [--role R] [--address A]
              [--subject S] [--status S] [--follow-up DATE] [--reply T]
  sync        --office DIR [--today YYYY-MM-DD]
  summary     --office DIR
"""
import argparse, csv, datetime as dt, html, json, os, sys

JOB_COLS = ["job_id", "board", "req", "title", "employer", "site", "unit", "city", "country", "contract",
            "fte_or_hours", "shifts", "salary", "posted", "closes", "url", "fit_score", "fit_notes",
            "scam_flag", "status", "first_seen", "last_checked", "status_changed", "notes"]
APP_COLS = ["date", "job_id", "req", "title", "employer", "letter_file", "cv_file", "answers",
            "confirmation", "submitted_by", "notes"]
OUT_COLS = ["date", "job_id", "contact_name", "contact_role", "channel", "address", "subject",
            "status", "follow_up_due", "reply"]
STATUSES = ["Found", "Shortlisted", "Skipped", "Applied", "Waiting feedback", "Interview requested",
            "Interview done", "Offer", "Hired", "Rejected", "Closed", "Missed", "Withdrawn"]
ACTIVE = {"Applied", "Waiting feedback", "Interview requested", "Interview done", "Offer"}
COLOURS = {"Found": "E8EEF5", "Shortlisted": "DCE8FA", "Skipped": "EEEEEE", "Applied": "D6F0E0",
           "Waiting feedback": "FFF3CD", "Interview requested": "C7E9FF", "Interview done": "BFD9FF",
           "Offer": "C8F2C2", "Hired": "9EE09A", "Rejected": "F8D7DA", "Closed": "E2E2E2",
           "Missed": "F5C2B8", "Withdrawn": "E6E0F0"}


def today(args=None):
    if args is not None and getattr(args, "today", None):
        return dt.date.fromisoformat(args.today)
    return dt.date.today()


def path(office, name):
    return os.path.join(office, name)


def read(office, name, cols):
    p = path(office, name)
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for c in cols:
            r.setdefault(c, "")
    return rows


def write(office, name, cols, rows):
    p = path(office, name)
    tmp = p + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    os.replace(tmp, p)


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%b %d, %Y", "%B %d, %Y", "%d %B %Y", "%d %b %Y", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def find_job(jobs, key):
    for j in jobs:
        if j["job_id"] == key or (j["req"] and j["req"] == key):
            return j
    return None


def cmd_init(a):
    for d in ["", "cv", "templates", "letters", "notes"]:
        os.makedirs(path(a.office, d), exist_ok=True)
    for name, cols in (("jobs.csv", JOB_COLS), ("applications.csv", APP_COLS), ("outreach.csv", OUT_COLS)):
        if not os.path.exists(path(a.office, name)):
            write(a.office, name, cols, [])
    lp = path(a.office, "log.md")
    if not os.path.exists(lp):
        with open(lp, "w", encoding="utf-8") as f:
            f.write("# Job Office Log\n")
    print("Office ready at", os.path.abspath(a.office))


def cmd_known(a):
    for j in read(a.office, "jobs.csv", JOB_COLS):
        print(f'{j["job_id"]}\t{j["req"]}\t{j["status"]}\t{j["employer"]}\t{j["title"]}')


def cmd_add_jobs(a):
    jobs = read(a.office, "jobs.csv", JOB_COLS)
    new = json.load(open(a.file, encoding="utf-8"))
    known_ids = {j["job_id"] for j in jobs}
    known_reqs = {(j["employer"], j["req"]) for j in jobs if j["req"]}
    added = skipped = 0
    t = today(a).isoformat()
    for n in new:
        n = {k: ("" if v is None else str(v)) for k, v in n.items()}
        if not n.get("job_id"):
            n["job_id"] = n.get("req") or n.get("url", "")
        if n["job_id"] in known_ids or (n.get("req") and (n.get("employer", ""), n["req"]) in known_reqs):
            skipped += 1
            continue
        for dc in ("closes", "posted"):
            d = parse_date(n.get(dc, ""))
            if d:
                n[dc] = d.isoformat()
        n.setdefault("status", "Found")
        if n["status"] not in STATUSES:
            n["status"] = "Found"
        n.setdefault("first_seen", t)
        n["last_checked"] = t
        n["status_changed"] = t
        jobs.append(n)
        known_ids.add(n["job_id"])
        added += 1
    write(a.office, "jobs.csv", JOB_COLS, jobs)
    print(f"added {added}, already known {skipped}")


def set_status(job, status, note, t):
    if status not in STATUSES:
        sys.exit(f"Unknown status '{status}'. Use one of: {', '.join(STATUSES)}")
    job["status"] = status
    job["status_changed"] = t
    if note:
        job["notes"] = (job.get("notes", "") + f" [{t}] {note}").strip()


def cmd_status(a):
    jobs = read(a.office, "jobs.csv", JOB_COLS)
    j = find_job(jobs, a.job)
    if not j:
        sys.exit(f"Job {a.job} not found")
    set_status(j, a.status, a.note, today(a).isoformat())
    write(a.office, "jobs.csv", JOB_COLS, jobs)
    print(f'{j["req"] or j["job_id"]} -> {a.status}')


def cmd_applied(a):
    jobs = read(a.office, "jobs.csv", JOB_COLS)
    apps = read(a.office, "applications.csv", APP_COLS)
    j = find_job(jobs, a.job)
    t = today(a).isoformat()
    if not j:
        sys.exit(f"Job {a.job} not found; add it with add-jobs first")
    set_status(j, "Applied", None, t)
    apps.append({"date": t, "job_id": j["job_id"], "req": j["req"], "title": j["title"],
                 "employer": j["employer"], "letter_file": a.letter or "", "cv_file": a.cv or "",
                 "answers": a.answers or "", "confirmation": a.confirmation or "",
                 "submitted_by": a.by or "office", "notes": a.notes or ""})
    write(a.office, "jobs.csv", JOB_COLS, jobs)
    write(a.office, "applications.csv", APP_COLS, apps)
    print(f'logged application {j["req"] or j["job_id"]}')


def cmd_outreach(a):
    rows = read(a.office, "outreach.csv", OUT_COLS)
    rows.append({"date": today(a).isoformat(), "job_id": a.job, "contact_name": a.contact,
                 "contact_role": a.role or "", "channel": a.channel, "address": a.address or "",
                 "subject": a.subject or "", "status": a.status or "drafted",
                 "follow_up_due": a.follow_up or "", "reply": a.reply or ""})
    write(a.office, "outreach.csv", OUT_COLS, rows)
    print("outreach logged")


def apply_rules(jobs, apps, t):
    applied_on = {}
    for ap in apps:
        d = parse_date(ap["date"])
        if d:
            applied_on[ap["job_id"]] = max(d, applied_on.get(ap["job_id"], d))
    changes = []
    for j in jobs:
        s = j["status"]
        close = parse_date(j["closes"])
        if s in ("Found", "Shortlisted") and close and close < t:
            set_status(j, "Missed", "closing date passed", t.isoformat())
            changes.append((j, "Missed"))
        elif s == "Applied":
            d = applied_on.get(j["job_id"]) or parse_date(j.get("status_changed"))
            if d and (t - d).days > 7:
                set_status(j, "Waiting feedback", None, t.isoformat())
                changes.append((j, "Waiting feedback"))
    return changes


def counts(jobs):
    c = {s: 0 for s in STATUSES}
    for j in jobs:
        c[j["status"]] = c.get(j["status"], 0) + 1
    return c


def build_rows(jobs, apps, outs):
    app_by = {}
    for ap in apps:
        app_by[ap["job_id"]] = ap
    fu = {}
    for o in outs:
        if o["follow_up_due"] and o["status"] not in ("replied", "closed"):
            fu[o["job_id"]] = min(o["follow_up_due"], fu.get(o["job_id"], o["follow_up_due"]))
    rows = []
    for j in jobs:
        ap = app_by.get(j["job_id"], {})
        rows.append({"Req": j["req"], "Role": j["title"], "Employer": j["employer"], "Site": j["site"],
                     "Unit": j["unit"], "City": j["city"], "Country": j["country"],
                     "Contract": j["contract"], "Hours/FTE": j["fte_or_hours"], "Shifts": j["shifts"],
                     "Fit": j["fit_score"], "Status": j["status"], "Applied on": ap.get("date", ""),
                     "Closes": j["closes"], "Follow up due": fu.get(j["job_id"], ""),
                     "Letter": ap.get("letter_file", ""), "Board": j["board"], "Link": j["url"],
                     "Notes": j["notes"]})
    order = {s: i for i, s in enumerate(["Interview requested", "Offer", "Interview done", "Waiting feedback",
                                          "Applied", "Shortlisted", "Found", "Hired", "Rejected", "Missed",
                                          "Closed", "Skipped", "Withdrawn"])}
    rows.sort(key=lambda r: (order.get(r["Status"], 99), r["Closes"] or "9999"))
    return rows


def write_xlsx(office, rows, outs, c):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter
    except ImportError:
        print("openpyxl not installed; skipped tracker.xlsx (pip install openpyxl)")
        return
    wb = Workbook()
    ws = wb.active
    ws.title = "Applications"
    head = list(rows[0].keys()) if rows else ["Req", "Role", "Employer", "Status"]
    ws.append(head)
    for r in rows:
        ws.append([r.get(h, "") for h in head])
    hdr = PatternFill("solid", fgColor="1F3A5F")
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = hdr
        cell.alignment = Alignment(vertical="center")
    if rows:
        si = head.index("Status") + 1
        for i in range(2, len(rows) + 2):
            st = ws.cell(row=i, column=si).value
            ws.cell(row=i, column=si).fill = PatternFill("solid", fgColor=COLOURS.get(st, "FFFFFF"))
            if "Link" in head:
                lc = ws.cell(row=i, column=head.index("Link") + 1)
                if lc.value:
                    lc.hyperlink = lc.value
                    lc.font = Font(color="1F5FBF", underline="single")
    widths = {"Role": 34, "Employer": 26, "Site": 28, "Unit": 24, "Notes": 40, "Link": 30, "Letter": 30}
    for i, h in enumerate(head, 1):
        ws.column_dimensions[get_column_letter(i)].width = widths.get(h, 14)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    wo = wb.create_sheet("Outreach")
    wo.append(OUT_COLS)
    for o in outs:
        wo.append([o.get(k, "") for k in OUT_COLS])
    wsum = wb.create_sheet("Summary")
    wsum.append(["Status", "Count"])
    for s in STATUSES:
        wsum.append([s, c.get(s, 0)])
    wb.save(path(office, "tracker.xlsx"))


def weekly_counts(apps, weeks=10, t=None):
    t = t or dt.date.today()
    start = t - dt.timedelta(days=t.weekday())
    buckets = []
    for i in range(weeks - 1, -1, -1):
        ws = start - dt.timedelta(weeks=i)
        n = sum(1 for a in apps if (d := parse_date(a["date"])) and ws <= d < ws + dt.timedelta(days=7))
        buckets.append((ws.strftime("%d %b"), n))
    return buckets


def write_dashboard(office, rows, apps, outs, c, t):
    sent = sum(c[s] for s in ["Applied", "Waiting feedback", "Interview requested", "Interview done",
                              "Offer", "Hired", "Rejected", "Withdrawn"])
    responded = sum(c[s] for s in ["Interview requested", "Interview done", "Offer", "Hired", "Rejected"])
    rate = f"{round(100 * responded / sent)}%" if sent else "n/a"
    soon = [r for r in rows if r["Status"] in ("Found", "Shortlisted") and (d := parse_date(r["Closes"]))
            and 0 <= (d - t).days <= 7]
    inter = [r for r in rows if r["Status"] == "Interview requested"]
    due = [o for o in outs if o["follow_up_due"] and (d := parse_date(o["follow_up_due"])) and d <= t
           and o["status"] not in ("replied", "closed")]
    weeks = weekly_counts(apps, 10, t)
    wmax = max([n for _, n in weeks] + [1])
    e = html.escape

    def tile(label, val, sub=""):
        return f'<div class="tile"><div class="lab">{e(label)}</div><div class="val">{e(str(val))}</div><div class="sub">{e(sub)}</div></div>'

    bars = "".join(
        f'<div class="bar"><div class="b" style="height:{max(4, int(140 * n / wmax))}px" title="{n}"><span>{n}</span></div><div class="x">{e(lbl)}</div></div>'
        for lbl, n in weeks)
    pipe = "".join(
        f'<div class="pill" style="--c:#{COLOURS[s]}"><b>{c[s]}</b> {e(s)}</div>' for s in STATUSES if c[s])

    def table(items, cols):
        if not items:
            return '<p class="empty">Nothing here right now.</p>'
        h = "".join(f"<th>{e(x)}</th>" for x in cols)
        b = "".join("<tr>" + "".join(f"<td>{e(str(it.get(x, '')))}</td>" for x in cols) + "</tr>" for it in items)
        return f'<div class="tw"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'

    allrows = table(rows, ["Req", "Role", "Employer", "City", "Hours/FTE", "Status", "Applied on", "Closes"])
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Job Office Dashboard</title>
<style>
:root{{--bg:#F6F7F9;--card:#FFFFFF;--ink:#1B2430;--mut:#5B6675;--line:#E3E7EC;--acc:#1F3A5F;--bar:#3E6FA8}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#12161C;--card:#1B212A;--ink:#E8EDF3;--mut:#9AA6B4;--line:#2A323D;--acc:#9CC0EA;--bar:#6C9AD3}}}}
:root[data-theme="dark"]{{--bg:#12161C;--card:#1B212A;--ink:#E8EDF3;--mut:#9AA6B4;--line:#2A323D;--acc:#9CC0EA;--bar:#6C9AD3}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:24px 16px 48px}}h1{{font-size:24px;margin:0 0 4px;color:var(--acc)}}h2{{font-size:17px;margin:28px 0 10px}}
.meta{{color:var(--mut);font-size:13px}}.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:18px}}
.tile{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}}.lab{{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.04em}}
.val{{font-size:30px;font-weight:700;margin-top:4px}}.sub{{color:var(--mut);font-size:12px}}
.pipe{{display:flex;flex-wrap:wrap;gap:8px}}.pill{{background:var(--c);color:#1B2430;border-radius:999px;padding:5px 12px;font-size:13px}}
.chart{{display:flex;align-items:flex-end;gap:10px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;overflow-x:auto}}
.bar{{flex:1;min-width:36px;text-align:center}}.b{{background:var(--bar);border-radius:6px 6px 0 0;margin:0 auto;width:70%;position:relative}}
.b span{{position:absolute;top:-18px;left:0;right:0;font-size:12px;color:var(--mut)}}.x{{font-size:11px;color:var(--mut);margin-top:6px;white-space:nowrap}}
.tw{{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;font-size:13px}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);white-space:nowrap}}th{{color:var(--mut);font-weight:600}}
.empty{{color:var(--mut)}}.grid2{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}}
</style></head><body><main>
<h1>Job Office Dashboard</h1><div class="meta">Updated {t.strftime('%d %B %Y')}</div>
<div class="tiles">{tile('Applications sent', sent)}{tile('Waiting feedback', c['Waiting feedback'] + c['Applied'])}{tile('Interviews', c['Interview requested'] + c['Interview done'])}{tile('Offers', c['Offer'] + c['Hired'])}{tile('Response rate', rate, 'replies with an outcome')}{tile('Closing in 7 days', len(soon), 'not yet applied')}</div>
<h2>Pipeline</h2><div class="pipe">{pipe or '<span class="empty">No jobs yet.</span>'}</div>
<h2>Applications per week</h2><div class="chart">{bars}</div>
<div class="grid2"><div><h2>Interviews coming up</h2>{table(inter, ['Req', 'Role', 'Employer', 'Notes'])}</div>
<div><h2>Follow ups due</h2>{table([{'Due': o['follow_up_due'], 'Contact': o['contact_name'], 'Channel': o['channel'], 'Job': o['job_id']} for o in due], ['Due', 'Contact', 'Channel', 'Job'])}</div></div>
<h2>Closing soon, not applied</h2>{table(soon, ['Req', 'Role', 'Employer', 'Closes', 'Fit'])}
<h2>All applications</h2>{allrows}
</main></body></html>"""
    with open(path(office, "dashboard.html"), "w", encoding="utf-8") as f:
        f.write(doc)


def cmd_sync(a):
    t = today(a)
    jobs = read(a.office, "jobs.csv", JOB_COLS)
    apps = read(a.office, "applications.csv", APP_COLS)
    outs = read(a.office, "outreach.csv", OUT_COLS)
    changes = apply_rules(jobs, apps, t)
    write(a.office, "jobs.csv", JOB_COLS, jobs)
    c = counts(jobs)
    rows = build_rows(jobs, apps, outs)
    with open(path(a.office, "tracker_rows.json"), "w", encoding="utf-8") as f:
        json.dump({"updated": t.isoformat(), "counts": c, "rows": rows, "outreach": outs}, f, indent=1)
    write_xlsx(a.office, rows, outs, c)
    write_dashboard(a.office, rows, apps, outs, c, t)
    for j, s in changes:
        print(f'auto: {j["req"] or j["job_id"]} -> {s}')
    print("synced:", ", ".join(f"{k} {v}" for k, v in c.items() if v))


def cmd_summary(a):
    t = today(a)
    jobs = read(a.office, "jobs.csv", JOB_COLS)
    outs = read(a.office, "outreach.csv", OUT_COLS)
    c = counts(jobs)
    soon = [j for j in jobs if j["status"] in ("Found", "Shortlisted") and (d := parse_date(j["closes"]))
            and 0 <= (d - t).days <= 3]
    due = [o for o in outs if o["follow_up_due"] and (d := parse_date(o["follow_up_due"])) and d <= t
           and o["status"] not in ("replied", "closed")]
    applied = sum(c[s] for s in ACTIVE | {"Hired", "Rejected", "Withdrawn"})
    print(json.dumps({"applied_total": applied, "waiting": c["Applied"] + c["Waiting feedback"],
                      "interviews": c["Interview requested"] + c["Interview done"],
                      "offers": c["Offer"], "hired": c["Hired"], "shortlisted": c["Shortlisted"],
                      "found_unreviewed": c["Found"], "closing_in_3_days": [j["req"] or j["job_id"] for j in soon],
                      "follow_ups_due": len(due), "counts": c}, indent=1))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def sp(name, fn):
        s = sub.add_parser(name)
        s.add_argument("--office", default="job-office")
        s.add_argument("--today")
        s.set_defaults(fn=fn)
        return s

    sp("init", cmd_init)
    sp("known", cmd_known)
    s = sp("add-jobs", cmd_add_jobs); s.add_argument("--file", required=True)
    s = sp("status", cmd_status); s.add_argument("--job", required=True); s.add_argument("--status", required=True); s.add_argument("--note")
    s = sp("applied", cmd_applied)
    for x in ("--job",):
        s.add_argument(x, required=True)
    for x in ("--letter", "--cv", "--answers", "--confirmation", "--notes", "--by"):
        s.add_argument(x)
    s = sp("outreach", cmd_outreach)
    for x in ("--job", "--contact", "--channel"):
        s.add_argument(x, required=True)
    for x in ("--role", "--address", "--subject", "--status", "--follow-up", "--reply"):
        s.add_argument(x)
    sp("sync", cmd_sync)
    sp("summary", cmd_summary)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
