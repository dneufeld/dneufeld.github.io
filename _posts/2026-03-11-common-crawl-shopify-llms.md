---
layout: post
title: "I Scanned 34.6 Billion Web Pages and Found Shopify Disappearing from Common Crawl"
permalink: /common-crawl-shopify-llms/
description: "I scanned 34.6 billion pages and found Common Crawl's Shopify coverage dropped sharply in late 2025."
image: /assets/common-crawl-shopify-card.png
---

*Disclosure: I'm a former Shopify employee and current shareholder. This is not financial advice.*

Some context on me: I left Shopify in late 2022 to be a full-time parent. After three years away from tech, I've been trying to get up to speed on everything that happened with AI. Rather than just reading about it, I decided to build something: a data pipeline that scans [Common Crawl](https://commoncrawl.org/) archives for Shopify stores, co-built with Claude.

This post is my best attempt to make sense of the data, not the last word on it. I may have overlooked something important. If you've worked on Common Crawl, seen a similar pattern elsewhere, or think I've got a better explanation staring me in the face, I'd like to hear it.

## The idea

Back in 2022, Stable Diffusion had just launched and the internet was losing its mind over AI-generated images. Two weeks later, Simon Willison [published an analysis](https://simonwillison.net/2022/Sep/5/laion-aesthetics-weeknotes/) of where its training images came from. `cdn.shopify.com` was the **4th largest source**: 241,000 images out of 12 million. Shopify product images were quietly a significant chunk of what taught the model to understand visual content.

That stuck with me. In late 2024, I tried building a Common Crawl pipeline using Cursor and [cc-pyspark](https://github.com/commoncrawl/cc-pyspark). That's when I found [FineWeb](https://huggingface.co/datasets/HuggingFaceFW/fineweb), 15 trillion tokens of filtered Common Crawl data, the #2 most liked dataset on HuggingFace. I wondered: how much of Common Crawl is Shopify? What would a Shopify-specific version of FineWeb look like? Could you build interesting things from it, like an e-commerce-focused LLM, product similarity analysis, or fraud ring detection?

Cursor was a cute party trick at the time. I fought with it for a week and didn't get far. Then a couple months ago, seeing people on X rave about the latest coding agents (Codex, Claude Code) convinced me it was time to try again. I made more progress in one evening than in that entire week in 2024, and everything clicked. I was hooked on slop.

Before any of that analysis, though, I needed to know what was actually in Common Crawl. So I built a scanner.

## The pipeline

Common Crawl stores its data in three formats. A single crawl has about 100,000 files of each, totaling several hundred terabytes.

```text
WARC (Web ARChive)            WAT (Web Archive Transformation)   WET (Web Extract Text)
Full HTTP responses           Extracted metadata                  Plain text only

+-----------------------+    +--------------------------+    +----------------------+
| HTTP/1.1 200 OK       |    | url: store.com/...       |    | Welcome to our       |
| X-ShopId: 12345       |    | status: 200              |    | store! We sell       |
| Content-Type: html    |    | headers:                 |    | handmade candles     |
|                       |    |   X-ShopId: 12345        |    | from organic...      |
| <html>                |    |   Content-Type: html     |    |                      |
| <head>...</head>      |    | links: [...]             |    | Featured:            |
| <body>                |    | meta: [...]              |    |   Lavender Dream     |
|   Full page HTML...   |    | warc_offset: 84231       |    |   Cedar & Sage       |
| </body></html>        |    | warc_length: 52418       |    |   ...                |
+-----------------------+    +--------------------------+    +----------------------+
~300 TB per crawl            ~50 GB per crawl              ~25 GB per crawl
```

The key design decision was splitting the work into two stages:

```text
Stage 1: WAT scan

+--------------------------+    +--------------------------+    +--------------------------+
| Common Crawl            | -> | Shopify Signal          | -> | Parquet Dataset         |
| WAT S3 bucket           |    | Detection               |    | + WARC offsets          |
| ~2.5B records / crawl   |    | ~100K files / crawl     |    | ~125M records / crawl  |
+--------------------------+    +--------------------------+    +--------------------------+

Stage 2: WARC fetch

+--------------------------+    +--------------------------+    +--------------------------+
| Parquet with            | -> | Byte-range fetch        | -> | Full HTML +             |
| WARC coordinates        |    | from Common Crawl's S3  |    | extracted fields        |
| offset + length         |    | skip 95% of data        |    | products, apps, etc.    |
+--------------------------+    +--------------------------+    +--------------------------+
                                                                                 |
                                                                                 v
                                                                  +--------------------------+
                                                                  | Host Crawl Summary       |
                                                                  | 1 row per host per crawl |
                                                                  +--------------------------+
```

**Why split it?** Cost. WAT files are ~50GB compressed per crawl, small enough to stream through entirely. WARC files are the full page content: ~300TB per crawl. Scanning WAT first lets us identify the ~5% of records that are Shopify, save their exact byte offsets, and then surgically fetch only those records from the WARC files later. Without this split, we'd need to download and scan hundreds of terabytes to find our needle.

The whole thing runs on EC2 spot instances in us-east-1 (same region as Common Crawl's S3 bucket, so data transfer is free). A single c6a.24xlarge (96 vCPUs) processes one crawl's 100,000 WAT files (~50 GB compressed) in about 7 hours (~4 files/sec), costing roughly $10 in spot compute. To backfill 14 crawls, I ran them in parallel across multiple instances. The full backfill ran for under $200 total.

The output is a set of Parquet datasets on S3, queryable with Athena:

```text
Dataset            | What it contains                                          | Rows         | Size
-------------------+------------------------------------------------------------+--------------+------------------------
WAT Store Registry | One row per Shopify page detected. Hostname, URL,          | 1.74B        | 1.88 TB
                   | confidence score, signals, shop ID, plus the WARC          |              |
                   | filename/offset/length needed to fetch full content later. |              |
                   | Partitioned by crawl.                                      |              |
Host Crawl Summary | One row per unique host per crawl. Aggregated confidence,  | ~13M         | ~200 MB
                   | record counts, infrastructure info (IP, data center,       |              |
                   | shard). Powers most of the analysis below.                 |              |
WARC Content       | Full HTML plus extracted fields (products, apps, theme     | ~168M/dense  | ~12 TB/dense
(in progress)      | info) for each Shopify page. Fetched via byte-range       | ~11M/sparse  | ~700 GB/sparse
                   | requests using the offsets from the WAT scan.              |              |
```

## The drop

Here's what each crawl produced:

```text
Crawl            | Month    | Pages scanned | Shopify hosts found
-----------------+----------+---------------+---------------------
CC-MAIN-2025-05  | Jan 2025 | 3.0B          | 1,174,823
CC-MAIN-2025-08  | Feb 2025 | 2.6B          | 1,183,142
CC-MAIN-2025-13  | Mar 2025 | 2.7B          | 1,217,124
CC-MAIN-2025-18  | Apr 2025 | 2.7B          | 1,234,359
CC-MAIN-2025-21  | May 2025 | 2.5B          | 1,241,117
CC-MAIN-2025-26  | Jun 2025 | 2.4B          | 1,222,303
CC-MAIN-2025-30  | Jul 2025 | 2.4B          | 1,301,076
CC-MAIN-2025-33  | Aug 2025 | 2.4B          | 1,298,478
CC-MAIN-2025-38  | Sep 2025 | 2.4B          | 1,293,986
CC-MAIN-2025-43  | Oct 2025 | 2.6B          | 1,305,319
CC-MAIN-2025-47  | Nov 2025 | 2.3B          |   530,237
CC-MAIN-2025-51  | Dec 2025 | 2.2B          |   511,680
CC-MAIN-2026-04  | Jan 2026 | 2.3B          |   475,236
CC-MAIN-2026-08  | Feb 2026 | 2.1B          |   451,255
```

January through October 2025, the numbers are stable: roughly 1.2-1.3 million unique Shopify hosts per crawl. I've been calling these the **Shopify-dense crawls**.

Then in November 2025, it falls off a cliff. Down to 530K, and continuing to decline through February 2026 to 451K. I've been calling these the **Shopify-sparse crawls**. That's a 65% drop in Shopify host coverage.

Note that the total pages scanned per crawl only dropped about 30% (from ~2.6B to ~2.1B). The Shopify-specific drop is much larger than the overall crawl reduction.

The two-stage pipeline split paid off here. A dense crawl has ~168M Shopify records to WARC-fetch (~12TB of content, ~$275 in compute, days of processing). A sparse crawl has ~11M records (~700GB, ~$15, a few hours). Knowing which was which before spending on WARC fetches saved a lot of money.

## This isn't new, and the break was abrupt

To check whether the dense pattern was normal or anomalous, I took the Shopify hosts my scanner found across the 14 crawls and looked them up in [Common Crawl's index](https://index.commoncrawl.org/) (ccindex) going back to 2023. ccindex has hostname-level data for all crawls, so I could check how many of my known Shopify hosts appeared in each historical crawl and how many pages CC had for them. (Selected crawls shown, roughly one per quarter.)

```text
Sparse-era rows start at CC-MAIN-2025-47.

Crawl            | Month    | Known Shopify hosts | Pages crawled | Pages/host
-----------------+----------+---------------------+---------------+-----------
CC-MAIN-2023-06  | Jan 2023 |             494,623 |   119,949,903 |       242
CC-MAIN-2023-40  | Sep 2023 |             569,910 |   152,527,949 |       268
CC-MAIN-2024-10  | Feb 2024 |             714,229 |   146,152,846 |       205
CC-MAIN-2024-30  | Jul 2024 |             904,687 |   129,811,540 |       144
CC-MAIN-2024-51  | Dec 2024 |           1,052,755 |   154,145,907 |       146
CC-MAIN-2025-05  | Jan 2025 |           1,076,271 |   194,497,145 |       181
CC-MAIN-2025-43  | Oct 2025 |           1,147,731 |   175,100,841 |       153
CC-MAIN-2025-47  | Nov 2025 |             438,066 |    13,968,912 |        32
CC-MAIN-2025-51  | Dec 2025 |             407,336 |    13,396,375 |        33
CC-MAIN-2026-04  | Jan 2026 |             370,762 |    14,249,308 |        38
```

The pattern was consistent for at least three years. Coverage of these hosts was steadily *growing*, from 495K in early 2023 to 1.15M by October 2025. Pages per host ranged from 140 to 270.

Then at CC-MAIN-2025-47, both metrics fell off a cliff simultaneously. Hosts dropped to 438K. Pages per host went from ~153 to ~32. This wasn't a gradual decline. Something specific changed.

## What happened to the 768K missing hosts?

768,000 hosts appeared in two or more dense crawls but zero sparse crawls. I wanted to know: did these stores actually go away, or did Common Crawl just stop visiting them?

I investigated in two stages. First, I cross-referenced the full population against Common Crawl's index to determine *why* each host was missing:

```text
Category                                 | Count   | %    | What it means
-----------------------------------------+---------+------+--------------------------------------------
CC stopped crawling entirely             | 723,181 | 94.2 | Not in CC's crawl at all
CC crawled, but Shopify not detected     |  35,375 |  4.6 | Possible detection gap or store changed
Root domain still present on other host  |   9,246 |  1.2 | Example: www.store.com survived, store.com
                                         |         |      | did not
```

94% of missing hosts simply aren't being crawled by Common Crawl anymore. The 4.6% "crawled but not detected" gap likely includes stores that were temporarily down during the crawl, migrated to headless frontends, or were crawled on a URL that doesn't carry Shopify signals.

Then I verified the 723K hosts that CC stopped crawling - not a sample, the full population. I ran DNS resolution on every host and followed up with HTTP probes on the ones that still pointed to Shopify's IP range:

```text
Category         | Count   | %    | Description
-----------------+---------+------+-----------------------------------------------
active_shopify   | 479,533 | 66.9 | Still on Shopify, CC just stopped crawling
migrated         |  63,159 |  8.8 | DNS points to non-Shopify IP
dead             |  56,459 |  7.9 | Domain expired, no DNS record
churned_404      |  40,558 |  5.7 | Deactivated store
churned_402      |  39,368 |  5.5 | Suspended (unpaid)
blocked          |  33,481 |  4.7 | 403 without Shopify headers
churned_other    |   2,767 |  0.4 | Other inactive states
inactive_shopify |   1,089 |  0.2 | Shopify IP, not serving
rate_limited     |     108 |  0.0 | Inconclusive (429/503)
```

**Two thirds of the "missing" hosts are still active Shopify stores.** They return 200s, serve Shopify headers, and are ready to sell — Common Crawl just stopped visiting them. The true churn (dead + migrated + suspended + deactivated) accounts for about 31% of the missing population, which is what you'd expect from normal store turnover over a few months.

## Who got dropped?

The missing hosts break down by type:

- **70.4%** bare apex domains (like `store.com`)
- **15.3%** `www.` custom domains
- **12.0%** subdomains (like `shop.brand.com`)
- **2.3%** `myshopify.com` subdomains

In the dense crawls, apex domains made up ~77% of Shopify hosts. In the sparse crawls, that shifted to ~63%, with `www.` variants holding up better, likely because they're more discoverable through link graphs.

I also checked the top 100 Tranco-ranked Shopify stores: 93 out of 99 appear in at least one sparse crawl. The big names (Fashion Nova, Skims, Kith, Allbirds) show up in nearly every crawl. CC's sparse crawls still prioritize popular sites.

The practical effect: the long tail got cut. Independent merchants with a custom domain and no massive backlink profile are the ones vanishing.

## The stores that survived got thinner

Even for stores that remained in the sparse crawls, coverage got much shallower:

```text
Records per host | Dense (Oct 2025) | Sparse (Nov 2025)
-----------------+------------------+-------------------
1 page           | ~15%             | ~52%
2-10 pages       | ~25%             | ~35%
11-100 pages     | ~30%             | ~12%
100+ pages       | ~30%             | ~1%
```

In dense crawls, Common Crawl would index many URLs per store: product pages, collection pages, locale variants (English, French, German versions of each page). In sparse crawls, over half the surviving stores have just a single page crawled. Most stores went from having their full catalog indexed to having one or two product pages.

## Thinking out loud

**How much does this matter for LLM training data?**

Common Crawl has been a foundational data source for LLMs. A [2024 Mozilla Foundation study](https://www.mozillafoundation.org/en/research/library/generative-ai-training-data/common-crawl/) found that at least 64% of 47 LLMs published between 2019-2023 used filtered Common Crawl data. The most popular open training datasets today are built directly from it:

- [**FineWeb**](https://huggingface.co/datasets/HuggingFaceFW/fineweb): 15T+ tokens from 96 CC snapshots. The #2 most liked dataset on HuggingFace.
- [**FineFineweb**](https://huggingface.co/datasets/m-a-p/FineFineweb): a quality-filtered derivative. The #5 most downloaded dataset on all of HuggingFace.
- [**RefinedWeb**](https://huggingface.co/datasets/tiiuae/falcon-refinedweb), **C4**, **OSCAR**, **SlimPajama**, **RedPajama**, **Dolma**: all Common Crawl derivatives.

FineWeb is already updated through CC-MAIN-2025-26 (a Shopify-dense crawl). When they incorporate the newer snapshots, those will be Shopify-sparse. Does that matter? I don't know. These datasets are enormous and Shopify is one slice of the web. But it's a commercially significant slice: Shopify powers roughly 10% of US e-commerce.

**Is losing CC coverage actually bad for merchants?**

There's a tension here between what's good for Shopify as a platform and what's good for individual merchants. Broad representation in training data means the AI's default mental model of "e-commerce" is Shopify-flavored. That's great for the platform. But for a small DTC brand, having their carefully crafted product descriptions absorbed into training data mostly just helps competitors generate similar copy. The merchant gets no attribution, no backlink, no visit. It's a bit like how Yelp restaurant reviews made Google better at answering restaurant questions without anyone needing to visit Yelp.

But that framing assumes discovery still works like search. It increasingly doesn't. We're not far from routinely purchasing through personal AI agents, whether that's dedicated shopping agents or just asking ChatGPT, Claude, or Gemini to find you something. If a merchant isn't in the model's training data, they may be invisible to this entire new discovery channel.

Shopify knows this. They've launched [Agentic Storefronts](https://www.shopify.com/news/winter-26-edition-agentic-storefronts) to connect merchants directly to ChatGPT, Perplexity, and Copilot. Their [GEO playbook](https://www.shopify.com/enterprise/blog/generative-engine-optimization) reports AI-driven traffic to Shopify is up 8x and orders up 15x since January 2025. Their CTO [Mikhail Parakhin](https://x.com/MParakhin/status/2028522963642028523) recently noted: "A product page can have every piece of information a buyer needs, but if it lives in JavaScript logic, an agent can't read it." These integrations solve real-time product data. But an agent still needs a reason to look at a store in the first place. Background knowledge, the kind that comes from pre-training on web data, matters.

So the same long-tail merchants who are disappearing from Common Crawl are the ones most at risk of being invisible to AI-powered shopping, and the ones least able to get discovered through brand recognition alone.

**Why did Common Crawl's coverage change?**

I don't know. Common Crawl hasn't publicly announced a methodology change. Their [published statistics](https://commoncrawl.github.io/cc-crawl-statistics/) show total page counts dropped ~30%, but the number of registered domains stayed roughly flat (~39M to ~37M), suggesting reduced crawl depth rather than reduced breadth. The abrupt break at CC-MAIN-2025-47 looks like a deliberate configuration change, not a gradual decline.

The timing is interesting. In November 2025, [The Atlantic reported](https://tech.slashdot.org/story/25/11/08/1930213/common-crawl-criticized-for-quietly-funneling-paywalled-articles-to-ai-developers) that Common Crawl was bypassing paywalls. Common Crawl [responded](https://commoncrawl.org/blog/setting-the-record-straight-common-crawls-commitment-to-transparency-fair-use-and-the-public-good). Whether the timing is coincidence or not, I can't say.

I may be missing something obvious here. If you see an error, have more context, or have a better explanation for the coverage shift, please open an issue in [dneufeld.github.io](https://github.com/dneufeld/dneufeld.github.io/issues) or get in touch.
