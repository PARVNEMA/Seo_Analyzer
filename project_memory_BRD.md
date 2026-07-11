Business Requirements Document
AI-Powered SEO Testing & Optimization Tool
Version 1.0
Prepared for: Portfolio / Personal Project
Date: July 2026
1. Introduction
This document describes what needs to be built for an AI-powered SEO Testing and Optimization Tool. It explains the problem the tool solves, who will use it, what it should do, and what it should not do. This is meant to be a practical build guide, not just a theory document — every feature listed here is something a real user would actually use.
1.1 Purpose of this document
To clearly define the scope, features, and technical direction of the project before development starts, so that time is spent building the right things in the right order.
1.2 Background
Most website owners and content creators know SEO matters but don't have the time, budget, or expertise to run full audits manually. Existing tools (Ahrefs, SEMrush, Surfer SEO) are powerful but expensive and often overwhelming. This project builds a focused, AI-driven alternative that automates the analysis and gives direct, actionable suggestions instead of just raw data.
2. Project Overview
Project Name: AI SEO Optimizer
Project Type: Web application (portfolio project / personal SaaS tool)
Primary Tech Stack: FastAPI (backend), LangChain + LangGraph (AI orchestration), Google Gemini (LLM), Scrapy/Playwright (crawling), Next.js/React (frontend), PostgreSQL (database)
Target Users: Bloggers, small business owners, freelance content writers, and developers who want to check and improve the SEO of their own web pages
2.1 Problem Statement
Website owners often publish content without knowing whether it's actually optimized for search engines. They don't know what competitors are doing better, whether their technical setup is hurting rankings, or what specific changes would help. Manual SEO audits take hours and require expertise most people don't have.
2.2 Proposed Solution
A web application where a user submits a URL or piece of content and receives an automated, AI-generated SEO report covering technical health, on-page optimization, content quality, and competitor comparison — along with specific, prioritized fixes, not just scores.
3. Objectives
Automate SEO analysis that normally requires manual expert review
Give specific, actionable suggestions — not vague scores with no explanation
Compare a page against real competitor pages ranking for the same keyword
Allow natural-language questions about a site's own SEO data
Keep the tool usable for one page as well as an entire website
Build using an agentic AI pipeline (LangGraph) so the analysis can branch and adapt depending on what's found — not a single dumb prompt
4. Scope
4.1 In Scope (MVP + core phases)
Single-page SEO analysis (on-page + technical + readability)
AI-generated title, meta description, and content suggestions
Keyword research and search-intent classification
Competitor content comparison for a given keyword
Full-site crawling with a prioritized fix list
Natural language chat interface over a user's own crawled site data
Dashboard showing SEO health score with history/trend over time
4.2 Out of Scope (for now)
Paid backlink data (Ahrefs/Moz/SEMrush APIs) — expensive, can be mocked or added later
Actual publishing/CMS integration (WordPress auto-publish, etc.)
Paid ad campaign management (Google Ads / PPC) — this tool is organic search only
Multi-language SEO support in v1 (English content only to start)
5. Users & Stakeholders
User Type
What they need
Content Writer / Blogger
Wants quick feedback on a draft before publishing
Small Business Owner
Wants to know why their site isn't showing up on Google
Freelance/Agency SEO person
Wants to run audits faster across multiple client sites
You (Developer)
Wants a strong, real-world portfolio project showing full-stack + agentic AI skills
6. Functional Requirements
Grouped by module. Each module maps to one part of the system.
6.1 Module 1 — URL / Content Input
Feature
What it does
Priority
Submit a URL
User pastes a live URL; system crawls and fetches the page content
Must-have
Submit raw content
User pastes draft text/HTML directly, no live URL needed
Must-have
Target keyword input
User specifies the keyword/topic they're trying to rank for
Must-have
6.2 Module 2 — Technical SEO Audit
Feature
What it does
Priority
Page speed check
Pulls Core Web Vitals (LCP, CLS, INP) via Google PageSpeed Insights API
Must-have
Mobile-friendliness check
Flags if page isn't responsive/mobile-ready
Must-have
Broken link scan
Crawls internal/external links on the page, flags 404s
Must-have
Sitemap & robots.txt check
Confirms these exist and are configured correctly
Should-have
Schema markup detector
Checks for existing structured data (JSON-LD), flags if missing
Should-have
HTTPS/security check
Flags if page isn't served over HTTPS
Nice-to-have
6.3 Module 3 — On-Page Content Analysis
Feature
What it does
Priority
Title tag analysis
Checks length, keyword presence, generates 2-3 improved alternatives
Must-have
Meta description analysis
Checks length/CTR appeal, generates AI alternatives
Must-have
Header structure check
Verifies logical H1-H6 hierarchy, flags missing/duplicate H1
Must-have
Keyword density check
Flags keyword stuffing or under-optimization
Must-have
Readability score
Flesch-Kincaid or similar score with plain-language explanation
Must-have
Image alt-text checker
Flags images missing alt attributes, suggests alt text
Should-have
Internal linking suggestions
AI recommends which of the user's own pages to link to, and anchor text
Nice-to-have
6.4 Module 4 — AI Content Intelligence (core differentiator)
Feature
What it does
Priority
Search intent classifier
LLM labels the page/keyword as informational, transactional, navigational, or commercial
Must-have
Content gap analysis
Scrapes top 5 ranking pages for the keyword, LLM lists what subtopics/questions the user's content is missing
Must-have
AI content rewrite suggestions
Rewrites weak paragraphs to naturally include target keywords while keeping the original tone
Must-have
People-Also-Ask extractor
Pulls real PAA questions for the keyword and drafts short answers + FAQ schema
Should-have
E-E-A-T signal scorer
Flags whether content shows real expertise/experience (author bio, citations, first-hand language)
Should-have
Content brief generator
From just a keyword, generates a full brief: word count target, headers to cover, questions to answer
Nice-to-have
6.5 Module 5 — Keyword & Competitor Research
Feature
What it does
Priority
Keyword suggestions
Given a seed keyword, suggests related/semantic keywords via SerpAPI + LLM
Must-have
Competitor SERP scrape
Fetches and parses top-ranking pages for a given keyword using Scrapy/Playwright
Must-have
Side-by-side comparison
Shows user's page vs competitors on word count, headers, keyword usage
Must-have
SERP feature detector
Flags if the keyword has a featured snippet/video result and how to target it
Nice-to-have
6.6 Module 6 — Site-Wide Crawl & Reporting
Feature
What it does
Priority
Full-site crawl
Scrapy-based crawler maps all pages, respects robots.txt
Must-have
Prioritized action list
Ranks all found issues by impact vs effort across the whole site
Must-have
SEO health score
Single 0-100 score per page and site-wide, explained in plain language
Must-have
Historical tracking
Stores past scans, shows score trend over time per page
Should-have
Cannibalization detector
Flags when 2+ of the user's own pages target the same keyword
Nice-to-have
6.7 Module 7 — Natural Language Query Interface
Feature
What it does
Priority
Chat over site data
User asks questions like "which pages have weak meta descriptions?" in plain English
Should-have
Report Q&A
User asks follow-up questions about a specific generated report
Should-have
6.8 Module 8 — Dashboard & Reports
Feature
What it does
Priority
Report dashboard
Visual summary of scores, issues, and suggestions per page
Must-have
Export report
Download report as PDF for sharing with clients/team
Should-have
Before/after comparison
Re-scan after fixes applied, shows what improved
Nice-to-have
7. Non-Functional Requirements
Performance: A single-page analysis should complete in under 30 seconds; full-site crawl can run asynchronously in the background
Scalability: Backend should handle multiple concurrent scan jobs using background tasks/queues (e.g. Celery or FastAPI BackgroundTasks)
Reliability: Crawling must respect robots.txt and rate-limit requests to avoid getting blocked or hammering target sites
Usability: Reports must be understandable by a non-technical user, not just raw data dumps
Cost control: LLM calls should be batched/cached where possible since Gemini API calls have a cost per token
Security: User-submitted URLs must be validated to prevent SSRF (server-side request forgery) attacks during crawling
8. Technical Approach
8.1 Architecture Summary
Frontend (Next.js/React) sends a request to the FastAPI backend. The backend triggers a LangGraph workflow, which orchestrates multiple steps: crawling, technical audit, content analysis, keyword research, and competitor comparison. Each step is a node in the graph, and the graph can branch based on what it finds (for example, skip competitor analysis if no keyword was provided). Gemini is called at each AI-reasoning step through LangChain, using Pydantic schemas to keep responses structured. Final results are aggregated and stored, then returned to the frontend as a report.
8.2 Why LangGraph (not just LangChain chains)
Most steps in this pipeline depend on what the previous step found — that's conditional branching, not a straight line. For example: if the technical audit finds the page is fine but content is thin, the workflow should route to content-gap analysis; if technical issues are severe, it should prioritize those first. LangGraph is built for exactly this — state that persists across steps and conditional routing between nodes. Simple LangChain chains are used inside individual nodes (e.g., generating a meta description) where the input/output shape is fixed and no branching is needed.
8.3 Key Tools & Their Role
Tool
Role in the system
FastAPI
Backend API layer, handles requests, background jobs, and serves results
LangGraph
Orchestrates the multi-step SEO audit workflow with conditional branching
LangChain
Wraps individual LLM calls with structured (Pydantic) outputs inside each node
Google Gemini
The underlying LLM used for all reasoning/generation tasks
Scrapy
Crawls full websites, respects robots.txt, handles link discovery
Playwright
Renders JavaScript-heavy pages that Scrapy alone can't read
Google PageSpeed Insights API
Provides real Core Web Vitals data (free)
SerpAPI / Google Custom Search API
Fetches live search results for keyword/competitor research
PostgreSQL
Stores scan history, reports, and score trends
Next.js / React
Frontend dashboard and report UI
9. Data Requirements
Store: submitted URLs, crawled page content, generated reports, scores, and timestamps (for trend tracking)
Store: user accounts (if multi-user), linked to their submitted sites/pages
Cache: PageSpeed and SERP API responses briefly to avoid repeat calls for the same URL/keyword
No storage of sensitive personal data required for MVP
10. Assumptions & Constraints
Assumes users submit publicly accessible URLs (not password-protected pages)
Assumes free-tier API limits (PageSpeed, SerpAPI, Gemini) are sufficient for portfolio/demo usage — paid tiers needed for real production scale
Backlink/domain authority data is out of scope unless a paid API is added later
English-language content only in v1
11. Success Metrics
A single-page scan completes and returns a usable report in under 30 seconds
Content gap analysis correctly identifies at least 3 relevant missing subtopics for a given keyword, verified manually
Site-wide crawl correctly finds and prioritizes real issues on a live personal/test site
Report suggestions are specific enough that a user could apply them without needing to look anything up elsewhere
12. Suggested Build Phases
Phase
What gets built
Phase 1
Single-page analyzer: on-page + technical audit + AI title/meta suggestions (no LangGraph yet, simple chains)
Phase 2
Add keyword research + search intent classification
Phase 3
Introduce LangGraph: connect audit + content analysis + keyword modules with conditional routing
Phase 4
Competitor scraping (Scrapy/Playwright) + content gap analysis
Phase 5
Full-site crawl + prioritized action list + health score with history
Phase 6
Dashboard polish, PDF export, natural-language query interface over site data
13. Glossary
Term
Meaning
SEO
Search Engine Optimization — improving a site to rank higher in unpaid search results
SERP
Search Engine Results Page — the page Google shows after a search
Core Web Vitals
Google's page speed/experience metrics (LCP, CLS, INP)
E-E-A-T
Experience, Expertise, Authoritativeness, Trustworthiness — Google's content quality signals
PAA
People Also Ask — the expandable question box shown in Google search results
Schema markup
Structured data (JSON-LD) that helps search engines understand page content
Cannibalization
When multiple pages on the same site compete for the same keyword