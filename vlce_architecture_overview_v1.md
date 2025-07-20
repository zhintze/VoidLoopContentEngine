
# Void Loop Content Engine – Architecture Overview

## 1. User Input / account & Scheduling Setup

**Tools:**
- CLI Tool: Typer or Rich TUI
- Config Format: YAML or TOML (per account)

**User Actions:**
- `new account [name, site, social handles, keywords, tone, hashtags]`
- `schedule post [account, template, day, time]`
- `edit account`
- `list schedule`

**Used When:**
- Creating/editing account data
- Setting and reviewing content schedules
- Updating posting cadence per platform

---

## 2. Search Engine Trend Scanner

**Purpose:**  
Enhance content relevance with search trend data per account.

**Tools:**
- Google Trends API (`pytrends`)
- Bing Trends (scraped/API)
- Optional: Reddit, Pinterest

**Outputs:**
- Top related queries
- Rising/breakout terms
- Keyword heat over time
- Suggested subtopics

**Used When:**
- Pre-generation phase
- Updating prompt modifiers
- Suggesting daily hooks
- Flagging popular formats

**CLI Commands:**
- `scan trends [account]`
- `view trends [account]`
- `export trends [account]`

---

## 3. Content Generator Engine

**Features:**
- Template-agnostic GPT-based generation
- Integrates with trend scanner outputs
- Dynamically adjusts prompts per account/topic

---

## 4. Output Formatter

**Output Types:**
- Markdown (.md) for blogs
- Captions (.txt) for social posts
- JSON (optional debug/store)

**Used When:**
- Structuring post outputs
- Applying previews, metadata
- Organizing by folder/date/account/platform

---

## 5. Static Site Integration

**Tools:**
- Astro (default)
- Hugo (optional)

**Function:**
- Renders Markdown as static blog
- Applies tag/date/category routing
- Embeds SEO and image links

---

## 6. Social Media Posting Scheduler

**Language/Tools:**
- Python (`schedule` or `apscheduler`)
- Instagram Graph API
- Pinterest API / `pyppeteer` automation
- Optional: Buffer/Later

**Used When:**
- Posting at scheduled times
- Uploading formatted content
- Randomized timing to avoid bot patterns

---

## 7. Automation Runner

**Functions:**
- Orchestrates the entire flow

**CLI Commands:**
- `run all`
- `run account [name]`
- `test prompt [template, account]`
- `post now [account, template]`

---

## 8. account Library + Template Registry

**Storage:**
- `accounts/[account_name].toml`
- `templates/[template_name].j2`

**Used When:**
- Referencing tone, keywords, accounts
- Managing templates and prompt formats

---

## 9. Project Management + CI

**Tools:**
- GitHub (issues, branches, GitHub Actions)
- Taiga (stories, sprints)
- CI for prompt/template validation

---

## 10. Optional Future Modules

- Image Suggestions (DALL·E, stock APIs)
- Analytics Collector (performance scraping)
- Mobile Dashboard (Flask + Android)
- Human-Style Content Rewriter Toggle
