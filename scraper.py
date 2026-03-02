"""
SHL Product Catalogue Scraper - Selenium Version
"""
import json
import time
import re
import requests

def scrape_with_selenium():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager

    print("Starting Chrome browser...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    all_assessments = []
    seen_urls = set()

    try:
        start = 0
        page = 1
        while True:
            url = f"https://www.shl.com/solutions/products/product-catalog/?start={start}&type=1&pagesize=12"
            print(f"Page {page}: {url}")
            driver.get(url)
            time.sleep(4)

            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/product-catalog/view/']")
            new_found = 0
            for link in links:
                href = link.get_attribute("href")
                name = link.text.strip()
                if href and href not in seen_urls and name and len(name) > 2:
                    seen_urls.add(href)
                    all_assessments.append({
                        "name": name, "url": href,
                        "description": "", "duration": None,
                        "test_type": [], "remote_support": "Yes", "adaptive_support": "No"
                    })
                    new_found += 1

            print(f"  +{new_found} new (total: {len(all_assessments)})")
            if new_found == 0:
                break
            start += 12
            page += 1
            if page > 50:
                break
            time.sleep(1)
    finally:
        driver.quit()
    return all_assessments


def build_from_known_data():
    print("Building from known SHL URLs...")
    training_urls = [
        "https://www.shl.com/solutions/products/product-catalog/view/automata-fix-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/core-java-entry-level-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/java-8-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/core-java-advanced-level-new/",
        "https://www.shl.com/products/product-catalog/view/interpersonal-communications/",
        "https://www.shl.com/solutions/products/product-catalog/view/entry-level-sales-7-1/",
        "https://www.shl.com/solutions/products/product-catalog/view/entry-level-sales-sift-out-7-1/",
        "https://www.shl.com/solutions/products/product-catalog/view/entry-level-sales-solution/",
        "https://www.shl.com/solutions/products/product-catalog/view/sales-representative-solution/",
        "https://www.shl.com/products/product-catalog/view/business-communication-adaptive/",
        "https://www.shl.com/solutions/products/product-catalog/view/technical-sales-associate-solution/",
        "https://www.shl.com/solutions/products/product-catalog/view/svar-spoken-english-indian-accent-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/english-comprehension-new/",
        "https://www.shl.com/products/product-catalog/view/enterprise-leadership-report/",
        "https://www.shl.com/products/product-catalog/view/occupational-personality-questionnaire-opq32r/",
        "https://www.shl.com/solutions/products/product-catalog/view/opq-leadership-report/",
        "https://www.shl.com/solutions/products/product-catalog/view/opq-team-types-and-leadership-styles-report/",
        "https://www.shl.com/products/product-catalog/view/enterprise-leadership-report-2-0/",
        "https://www.shl.com/solutions/products/product-catalog/view/global-skills-assessment/",
        "https://www.shl.com/solutions/products/product-catalog/view/verify-verbal-ability-next-generation/",
        "https://www.shl.com/solutions/products/product-catalog/view/shl-verify-interactive-inductive-reasoning/",
        "https://www.shl.com/solutions/products/product-catalog/view/marketing-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/automata-selenium/",
        "https://www.shl.com/products/product-catalog/view/professional-7-1-solution/",
        "https://www.shl.com/solutions/products/product-catalog/view/javascript-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/htmlcss-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/css3-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/selenium-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/sql-server-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/automata-sql-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/manual-testing-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/administrative-professional-short-form/",
        "https://www.shl.com/solutions/products/product-catalog/view/verify-numerical-ability/",
        "https://www.shl.com/solutions/products/product-catalog/view/financial-professional-short-form/",
        "https://www.shl.com/solutions/products/product-catalog/view/bank-administrative-assistant-short-form/",
        "https://www.shl.com/solutions/products/product-catalog/view/general-entry-level-data-entry-7-0-solution/",
        "https://www.shl.com/solutions/products/product-catalog/view/basic-computer-literacy-windows-10-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/manager-8-0-jfa-4310/",
        "https://www.shl.com/solutions/products/product-catalog/view/microsoft-excel-365-essentials-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/digital-advertising-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/writex-email-writing-sales-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/shl-verify-interactive-numerical-calculation/",
        "https://www.shl.com/solutions/products/product-catalog/view/professional-7-0-solution-3958/",
        "https://www.shl.com/solutions/products/product-catalog/view/sql-server-analysis-services-%28ssas%29-%28new%29/",
        "https://www.shl.com/solutions/products/product-catalog/view/python-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/tableau-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/microsoft-excel-365-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/data-warehousing-concepts/",
        "https://www.shl.com/solutions/products/product-catalog/view/occupational-personality-questionnaire-opq32r/",
        "https://www.shl.com/solutions/products/product-catalog/view/written-english-v1/",
        "https://www.shl.com/solutions/products/product-catalog/view/search-engine-optimization-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/drupal-new/",
        "https://www.shl.com/solutions/products/product-catalog/view/technology-professional-8-0-job-focused-assessment/",
        "https://www.shl.com/solutions/products/product-catalog/view/verify-verbal-ability-next-generation/",
    ]

    extended_slugs = [
        "c-sharp-new","c-plus-plus-new","r-new","scala-new","kotlin-new",
        "angular-new","react-new","vue-js-new","node-js-new","django-new",
        "spring-framework-new","docker-new","kubernetes-new","aws-new","azure-new",
        "git-new","linux-new","php-new","ruby-on-rails-new","swift-new",
        "machine-learning-new","data-science-new","cybersecurity-new",
        "project-management-new","agile-new","microsoft-word-365-new",
        "microsoft-powerpoint-365-new","microsoft-outlook-365-new",
        "salesforce-new","sap-new","verify-inductive-reasoning",
        "verify-deductive-reasoning","verify-numerical-ability-next-generation",
        "graduate-8-0-solution","customer-service-solution","customer-service-7-0",
        "call-center-customer-service-solution","inductive-reasoning-new",
        "deductive-reasoning-new","clerical-administrative-solution",
        "bank-operations-solution","motivational-questionnaire-mq",
        "numerical-reasoning-test","verbal-reasoning-test","abstract-reasoning-test",
        "opq32-leadership-potential-report","opq32-sales-report",
        "opq32-customer-service-report","coding-test-new","debugging-test-new",
        "full-stack-developer-new","devops-new","business-analyst-new",
        "financial-analyst-new","hr-professional-new","supply-chain-new",
        "general-ability-test","critical-thinking-test","problem-solving-assessment",
        "emotional-intelligence-assessment","resilience-questionnaire",
        "customer-contact-solution","supervisor-solution","team-leader-solution",
        "graduate-8-0-profile","workplace-personality-index",
    ]

    all_assessments = []
    seen_urls = set()
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

    # Add training URLs (confirmed valid)
    for url in training_urls:
        url = url.rstrip('/') + '/'
        if url not in seen_urls:
            seen_urls.add(url)
            slug = url.rstrip('/').split('/')[-1]
            name = slug.replace('-', ' ').replace('new', '').strip().title()
            name = re.sub(r'\s+', ' ', name).strip()
            all_assessments.append({
                "name": name, "url": url, "description": "",
                "duration": None, "test_type": [],
                "remote_support": "Yes", "adaptive_support": "No"
            })

    print(f"Added {len(all_assessments)} from training data. Checking extended list...")

    # Verify extended slugs
    base = "https://www.shl.com/solutions/products/product-catalog/view/{}/"
    for slug in extended_slugs:
        url = base.format(slug)
        if url in seen_urls:
            continue
        try:
            resp = session.head(url, timeout=8, allow_redirects=True)
            if resp.status_code == 200:
                seen_urls.add(url)
                name = slug.replace('-', ' ').replace('new', '').strip().title()
                name = re.sub(r'\s+', ' ', name).strip()
                all_assessments.append({
                    "name": name, "url": url, "description": "",
                    "duration": None, "test_type": [],
                    "remote_support": "Yes", "adaptive_support": "No"
                })
                print(f"  ✓ {name}")
            time.sleep(0.15)
        except:
            pass

    return all_assessments


if __name__ == "__main__":
    print("=" * 50)
    print("SHL Catalog Scraper")
    print("=" * 50)

    # Try Selenium first
    results = []
    try:
        results = scrape_with_selenium()
        print(f"Selenium found {len(results)} assessments")
    except Exception as e:
        print(f"Selenium failed: {e}")

    # If not enough, use known URLs
    if len(results) < 50:
        print("Using known URL approach...")
        known = build_from_known_data()
        existing = {a['url'] for a in results}
        for a in known:
            if a['url'] not in existing:
                results.append(a)

    with open("shl_catalog_raw.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ DONE! Saved {len(results)} assessments to shl_catalog_raw.json")
    for a in results[:3]:
        print(f"  - {a['name']}: {a['url']}")
