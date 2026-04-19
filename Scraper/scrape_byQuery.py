"""
╔══════════════════════════════════════════════════════════════════════════╗
║       WUZZUF Scraper v3 — Precision Edition (Confirmed HTML Selectors)   ║
║  Engine  : Playwright (Chromium)                                         ║
║  Strategy: JSON-LD first → Exact CSS selectors → Regex fallbacks         ║
║  Fields  : All original + job_description + job_requirements             ║
╚══════════════════════════════════════════════════════════════════════════╝

INSTALL (run once):
    pip install playwright pandas
    playwright install chromium

CONFIGURATION
  MAX_PAGES_PER_QUERY  →  Search pages per title  (each page = ~15 jobs)
  HEADLESS             →  True = silent | False = watch the browser
  OUTPUT_DIR           →  Folder for CSV + JSON output
  REQUEST_DELAY        →  (min, max) seconds between requests
"""

import os
import re
import json
import time
import random
import logging
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

import pandas as pd
from playwright.sync_api import (
    sync_playwright, Page,
    TimeoutError as PWTimeout
)

# ═══════════════════════════════════════════════════════════════════════
#  USER CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════

MAX_PAGES_PER_QUERY : int   = 75           # 3 pages x ~20 jobs x 15 queries = ~900 jobs
HEADLESS            : bool  = True        # Set False to watch the browser
OUTPUT_DIR          : str   = r"/Data/Raw/By_Query"
REQUEST_DELAY       : tuple = (2.0, 3.5)
LOG_LEVEL           : str   = "DEBUG"      # INFO = normal | DEBUG = verbose

# ═══════════════════════════════════════════════════════════════════════
#  TARGET JOB QUERIES
# ═══════════════════════════════════════════════════════════════════════

TARGET_QUERIES = [
    "Desktop Developer",
    "Software Engineer",
    "Software Developer",
    "Software Tester",
    "QA Engineer",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "Mobile Developer",
    "Game Developer",
    "Data Engineer",
    "Data Scientist",
    "AI Engineer",
    "Machine Learning Engineer",
    "Data Analyst",
    "Database Administrator",
    "DevOps Engineer",
    "Cloud Engineer",
    "Network Engineer",
    "IT Engineer",
    "System Administrator",
    "Cybersecurity",
]

# ═══════════════════════════════════════════════════════════════════════
#  CONFIRMED CSS SELECTORS  (from live Wuzzuf HTML, Feb 2026)
# ═══════════════════════════════════════════════════════════════════════

SEARCH_URL = "https://wuzzuf.net/search/jobs/"

# Job detail page selectors
SEL_TITLE = "h1.css-gkdl1m"
SEL_COMPANY = "strong.css-1vlp604 a.css-p7pghv span"
SEL_LOCATION_STRONG = "strong.css-1vlp604"
SEL_POST_DATE = "span.css-154erwh"
SEL_EMP_TYPE_TAGS = "div.css-5kov97 span.eoyjyou0"
SEL_DETAIL_ROWS = "div.css-1ajx53j"
SEL_DETAIL_LABEL = "span.css-720fa0"
SEL_DETAIL_VALUE = "span.css-2rozun"
SEL_CAT_VALUES = "div.css-1fwfib5 li a span.css-1vi25m1"
SEL_SKILLS = "div.css-14zw0ku div.css-qe7mba a span.css-1vi25m1"
SEL_JD_SECTION = "section.css-5pnqc5"

# URL pattern for job detail pages (confirmed)
JOB_URL_PATTERN = re.compile(
    r"wuzzuf\.net/(jobs/p|internship)/[a-z0-9]+-[a-z0-9-]+", re.I
)
EXCLUDE_PATTERNS = [
    "/search/", "/careers/", "/directory/", "/about",
    "/partners", "/policies", "/recruitment", "/feeds/",
    "/sitemap", "?q=", "?filters", "/a/", "/saudi/", "/internship/",
]

IT_KEYWORDS = [
    "software", "it/", "information technology", "data",
    "cloud", "devops", "cybersecurity", "embedded",
    "hardware", "telecom", "database", "artificial intelligence",
    "machine learning", "computer", "technology",
]

# ═══════════════════════════════════════════════════════════════════════
#  LOGGING
# ═══════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("wuzzuf_v3")


# ═══════════════════════════════════════════════════════════════════════
#  DATA MODEL
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class Job:
    search_query: str = ""
    job_title: str = ""
    company_name: str = ""
    location: str = ""
    posting_date: str = ""
    job_url: str = ""
    years_exp_min: Optional[int] = None
    years_exp_max: Optional[int] = None
    career_level: str = ""
    education_level: str = ""
    salary: str = ""
    employment_type: str = ""  # e.g. "Full Time | Remote"
    job_categories: str = ""  # pipe-separated
    skills: str = ""  # pipe-separated
    job_description: str = ""
    job_requirements: str = ""
    scraped_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )


# ═══════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════

def polite_delay():
    time.sleep(random.uniform(*REQUEST_DELAY))


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip() if text else ""


def parse_experience(text: str) -> tuple[Optional[int], Optional[int]]:
    """
    '2 to 7 years' → (2, 7)
    '3 - 5 Yrs'    → (3, 5)
    '2+ years'     → (2, None)
    '3 years'      → (3, 3)
    """
    if not text:
        return None, None
    t = text.lower()
    m = re.search(r"(\d+)\s*(?:to|-|–)\s*(\d+)", t)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"(\d+)\+", t)
    if m:
        return int(m.group(1)), None
    m = re.search(r"(\d+)", t)
    if m:
        v = int(m.group(1))
        return v, v
    return None, None


# ═══════════════════════════════════════════════════════════════════════
#  LAYER 1 — SEARCH RESULTS
# ═══════════════════════════════════════════════════════════════════════

def _collect_hrefs(page: Page) -> list[str]:
    """
    Scroll the page top→bottom in steps to trigger Wuzzuf's lazy-loaded job
    cards, then harvest all hrefs.  Returns only confirmed job-detail URLs.

    Fix for Bug 3: without scrolling, only the first ~6 cards are in the DOM
    when we collect hrefs, even though 15 exist on the page.
    """
    for fraction in [0.4, 0.7, 1.0]:
        page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {fraction})")
        page.wait_for_timeout(800)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(400)

    all_hrefs: list[str] = page.evaluate(
        "() => [...document.querySelectorAll('a[href]')].map(a => a.href)"
    )

    job_urls = list(dict.fromkeys(
        h for h in all_hrefs
        if JOB_URL_PATTERN.search(h)
        and not any(ex in h for ex in EXCLUDE_PATTERNS)
    ))
    return job_urls


def get_job_links(page: Page, query: str, page_num: int) -> list[str]:
    """
    Navigate to one search-results page and return unique job-detail URLs.

    Fixes applied:
      Bug 3 — scrolls the full page before collecting hrefs (lazy-load)
      Bug 4 — wait_for_selector only watches /jobs/p/ links (not /internship/
               which are excluded anyway), preventing a false-ready signal
    """
    url = f"{SEARCH_URL}?q={query.replace(' ', '+')}&start={page_num * 15}"
    log.info("  Search page %d \u2192 %s", page_num + 1, url)

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
    except PWTimeout:
        log.warning("  Timeout on navigation \u2014 continuing with what rendered")

    # Fix Bug 4: only watch /jobs/p/ (internship links are excluded anyway)
    try:
        page.wait_for_selector("a[href*='/jobs/p/']", timeout=25000)
    except PWTimeout:
        log.warning("  No /jobs/p/ links appeared within 25s for page %d", page_num + 1)
        return []

    # Fix Bug 3: scroll to trigger lazy loading of all 15 cards
    job_urls = _collect_hrefs(page)

    log.info("    Found %d job links", len(job_urls))

    if not job_urls:
        sample = [h for h in page.evaluate(
            "() => [...document.querySelectorAll('a[href]')].map(a => a.href)"
        ) if "/jobs/" in h or "/internship/" in h][:6]
        for s in sample:
            log.debug("    sample href: %s", s)

    return job_urls


# ═══════════════════════════════════════════════════════════════════════
#  LAYER 2 — JOB DETAIL PAGE
# ═══════════════════════════════════════════════════════════════════════

def extract_json_ld(page: Page) -> dict:
    """
    Extract the JobPosting JSON-LD block from <head>.
    Confirmed present in Wuzzuf detail pages.
    Provides: title, employmentType, datePosted, company, location, salary
    """
    try:
        raw = page.evaluate("""
                            () => {
                                const el = document.querySelector('script[type="application/ld+json"]');
                                return el ? el.textContent : null;
                            }
                            """)
        if raw:
            data = json.loads(raw)
            if data.get("@type") == "JobPosting":
                return data
    except Exception as exc:
        log.debug("JSON-LD failed: %s", exc)
    return {}


def scrape_job_detail(page: Page, url: str, query: str) -> Optional[Job]:
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector(SEL_TITLE, timeout=15000)
    except PWTimeout:
        log.warning("  Timeout on: %s", url)
        return None

    page.wait_for_timeout(1500)

    job = Job(search_query=query, job_url=url)

    # ── STEP 1: JSON-LD (highest confidence) ──────────────────────────
    ld = extract_json_ld(page)
    if ld:
        job.job_title = clean(ld.get("title", ""))
        org = ld.get("hiringOrganization", {})
        job.company_name = clean(org.get("name", ""))

        loc = ld.get("jobLocation", {})
        addr = loc.get("address", {}) if isinstance(loc, dict) else {}
        region = addr.get("addressRegion", "")
        country = addr.get("addressCountry", "")
        if region and country:
            job.location = f"{region}, {country}"
        elif region:
            job.location = region

        date_raw = ld.get("datePosted", "")
        if date_raw:
            try:
                from email.utils import parsedate_to_datetime
                job.posting_date = parsedate_to_datetime(date_raw).strftime("%Y-%m-%d")
            except Exception:
                job.posting_date = date_raw

        sal_obj = ld.get("baseSalary", {})
        if sal_obj:
            val = sal_obj.get("value", {})
            currency = sal_obj.get("currency", "")
            if isinstance(val, dict):
                mn = val.get("minValue", "")
                mx = val.get("maxValue", "")
                per = val.get("unitText", "MONTH").capitalize()
                if mn and mx:
                    job.salary = f"{mn} to {mx} {currency} Per {per}"
                elif mn:
                    job.salary = f"{mn} {currency} Per {per}"

        emp_raw = ld.get("employmentType", "")
        if emp_raw:
            job.employment_type = emp_raw.replace("_", " ").title()

    # ── STEP 2: Exact CSS selectors ───────────────────────────────────

    # Title fallback
    if not job.job_title:
        try:
            job.job_title = clean(page.locator(SEL_TITLE).first.inner_text())
        except Exception:
            pass

    # Company fallback
    if not job.company_name:
        try:
            job.company_name = clean(page.locator(SEL_COMPANY).first.inner_text())
        except Exception:
            pass

    # Posting date: always use the human-readable DOM version
    # "posted 6 days ago" is more useful than the ISO date
    try:
        dom_date = clean(page.locator(SEL_POST_DATE).first.inner_text())
        if dom_date:
            job.posting_date = dom_date
    except Exception:
        pass

    # Employment type badges: "Full Time", "Remote", "Freelance", etc.
    # More accurate than JSON-LD (shows multiple types)
    try:
        tags = page.locator(SEL_EMP_TYPE_TAGS).all_inner_texts()
        tags = [clean(t) for t in tags if t.strip()]
        if tags:
            job.employment_type = " | ".join(tags)
    except Exception:
        pass

    # Job details rows: Experience, Career Level, Education Level, Salary
    try:
        rows = page.locator(SEL_DETAIL_ROWS).all()
        for row in rows:
            try:
                label = clean(row.locator(SEL_DETAIL_LABEL).first.inner_text()).lower().rstrip(":")
                value = clean(row.locator(SEL_DETAIL_VALUE).first.inner_text())
            except Exception:
                continue

            if "experience" in label:
                job.years_exp_min, job.years_exp_max = parse_experience(value)
            elif "career" in label:
                job.career_level = value
            elif "education" in label:
                job.education_level = value
            elif "salary" in label and not job.salary:
                job.salary = value
    except Exception as exc:
        log.debug("Detail rows error: %s", exc)

    # Categories
    try:
        cats = page.locator(SEL_CAT_VALUES).all_inner_texts()
        cats = list(dict.fromkeys(clean(c) for c in cats if c.strip()))
        job.job_categories = " | ".join(cats)
    except Exception:
        pass

    # Skills
    try:
        skills = page.locator(SEL_SKILLS).all_inner_texts()
        skills = list(dict.fromkeys(clean(s) for s in skills if s.strip()))
        job.skills = " | ".join(skills)
    except Exception:
        pass

    # Job Description and Requirements
    # There are two section.css-5pnqc5 on the page:
    #   1st h2 = "Job Description"  → div[dir='auto']
    #   2nd h2 = "Job Requirements" → div[dir='auto']
    try:
        sections = page.locator(SEL_JD_SECTION).all()
        for section in sections:
            try:
                heading = clean(section.locator("h2").first.inner_text()).lower()
                body = section.locator("div[dir='auto']").first.inner_text()
                body = re.sub(r"\n{3,}", "\n\n", body.strip())
                if "description" in heading:
                    job.job_description = body
                elif "requirement" in heading:
                    job.job_requirements = body
            except Exception:
                continue
    except Exception as exc:
        log.debug("Description/requirements error: %s", exc)

    # Location fallback from strong tag
    if not job.location:
        try:
            strong_text = clean(page.locator(SEL_LOCATION_STRONG).first.inner_text())
            if "-" in strong_text:
                job.location = strong_text.split("-", 1)[-1].strip()
        except Exception:
            pass

    log.info(
        "  ✓ %-38s | %-20s | exp:%s-%s | type:%-18s | skills:%d",
        (job.job_title[:38] or "—"),
        (job.company_name[:20] or "—"),
        job.years_exp_min, job.years_exp_max,
        job.employment_type,
        len(job.skills.split(" | ")) if job.skills else 0,
    )
    return job


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════

def run():
    log.info("=" * 68)
    log.info("  WUZZUF Scraper v3")
    log.info("  Queries: %d  |  Pages/query: %d  |  Est. jobs: ~%d",
             len(TARGET_QUERIES), MAX_PAGES_PER_QUERY,
             len(TARGET_QUERIES) * MAX_PAGES_PER_QUERY * 15)
    log.info("=" * 68)

    all_jobs: list[Job] = []
    seen_urls: set[str] = set()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=HEADLESS,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ]
        )

        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            locale="en-US",
        )

        page = context.new_page()

        # Block heavy/tracking resources for speed
        def route_handler(route):
            rtype = route.request.resource_type
            rurl = route.request.url
            if rtype in ("image", "media", "font"):
                route.abort()
            elif any(t in rurl for t in [
                "googletagmanager", "hotjar", "clarity.ms",
                "facebook.net", "doubleclick", "inspectlet",
                "helpscout", "moengage", "criteo", "licdn",
            ]):
                route.abort()
            else:
                route.continue_()

        page.route("**/*", route_handler)

        # ── Scrape loop ────────────────────────────────────────────────
        for query in TARGET_QUERIES:
            log.info("\n>> Query: '%s'", query)
            query_urls: list[str] = []

            consecutive_empty = 0  # Bug 2 fix: track empties, don't break on first

            for page_num in range(MAX_PAGES_PER_QUERY):
                links = get_job_links(page, query, page_num)

                if not links:
                    consecutive_empty += 1
                    if consecutive_empty == 1:
                        # First empty: could be a slow render — retry once
                        log.info("  Page %d returned 0 links — retrying once...", page_num + 1)
                        polite_delay()
                        links = get_job_links(page, query, page_num)

                    if not links:
                        # Still empty after retry: genuinely no more pages
                        log.info("  No results on page %d after retry — stopping.", page_num + 1)
                        break
                    else:
                        consecutive_empty = 0  # retry succeeded, reset counter

                query_urls.extend(links)
                consecutive_empty = 0
                polite_delay()

            query_urls = list(dict.fromkeys(query_urls))
            log.info("  -> %d unique jobs to scrape", len(query_urls))

            for idx, url in enumerate(query_urls, 1):
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                job = scrape_job_detail(page, url, query)
                if job:
                    job_in_lower = (job.job_categories + " " + job.job_title).lower()
                    for kw in IT_KEYWORDS:
                        if kw in job_in_lower:
                            all_jobs.append(job)
                            log.info("  [%d/%d] %s", idx, len(query_urls), url)
                            break
                    else:
                        log.info("  Job Removed by IT/SW filter → [%s]", url)
                polite_delay()

        browser.close()

    # ── Save ──────────────────────────────────────────────────────────
    log.info("\n" + "=" * 68)

    log.info("  Total collected: %d jobs", len(all_jobs))

    if not all_jobs:
        log.warning("No jobs collected. Try HEADLESS=False to debug.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.DataFrame([asdict(j) for j in all_jobs])

    csv_path = os.path.join(OUTPUT_DIR, "Scrapped_Data.csv")
    json_path = os.path.join(OUTPUT_DIR, "Scrapped_Data.json")

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([asdict(j) for j in all_jobs], f, ensure_ascii=False, indent=2)

    log.info("  CSV  -> %s", csv_path)
    log.info("  JSON -> %s", json_path)

    # ── Fill-rate report ──────────────────────────────────────────────
    print("\n" + "=" * 68)
    print("  FIELD FILL RATE")
    print("=" * 68)
    key_cols = [
        "job_title", "company_name", "location", "posting_date",
        "years_exp_min", "years_exp_max", "career_level", "education_level",
        "salary", "employment_type", "job_categories", "skills",
        "job_description", "job_requirements",
    ]
    for col in key_cols:
        filled = (
                df[col].notna() &
                (df[col].astype(str).str.strip() != "") &
                (df[col].astype(str) != "None")
        ).sum()
        rate = filled / len(df) * 100
        bar = "█" * int(rate / 5) + "░" * (20 - int(rate / 5))
        print(f"  {col:<22} {bar}  {rate:5.1f}%  ({filled}/{len(df)})")

    print("=" * 68)
    print("\n  PER-QUERY SUMMARY")
    print("=" * 68)
    summary = (
        df.groupby("search_query")
        .agg(
            jobs=("job_title", "count"),
            with_salary=("salary", lambda x: (x.str.strip() != "").sum()),
            with_skills=("skills", lambda x: (x.str.strip() != "").sum()),
            avg_exp_min=("years_exp_min", "mean"),
        )
        .round(1)
    )
    print(summary.to_string())
    print("=" * 68)
    print(f"\n  Files saved to: {os.path.abspath(OUTPUT_DIR)}\n")


if __name__ == "__main__":
    run()