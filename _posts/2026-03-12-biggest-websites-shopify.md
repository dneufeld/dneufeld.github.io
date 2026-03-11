---
layout: post
title: "The Biggest Websites in the World Are Quietly Using Shopify"
permalink: /biggest-websites-use-shopify/
---

*Disclosure: I'm a former Shopify employee and current shareholder. This is not financial advice.*

If you ask someone to name a Shopify store, they'll probably say Fashion Nova, Kylie Cosmetics, or Allbirds. Brands that grew up on the platform. The Shopify success story has always been about DTC: scrappy founders building a brand, picking a theme, and going direct to consumers.

That story is real. But it's incomplete.

I cross-referenced 1.3 million Shopify stores (detected by [scanning Common Crawl]({% post_url 2026-03-11-common-crawl-shopify-llms %})) against the [Tranco top 1M](https://tranco-list.eu/) website ranking list. What I found: Shopify's biggest footprint isn't DTC brands running their whole business on it. It's Fortune 500 companies, government agencies, universities, and media outlets running Shopify stores on subdomains of their main sites, often with zero public acknowledgment.

## The ranking and the join

[Tranco](https://tranco-list.eu/) is a research-grade domain popularity ranking. It aggregates data from multiple sources — DNS traffic (Cloudflare Radar, Cisco Umbrella), real browser usage (Chrome UX Report), and passive DNS (Farsight) — and averages over 30 days to reduce volatility. Alexa rankings shut down in 2022, and single-source lists like Similarweb are easy to game. Tranco was built specifically to address this for academic research, and it's become the standard ranking list in security and web measurement papers.

I joined Tranco's top 1 million domains against the 1.3 million unique Shopify hosts my scanner found across 14 Common Crawl crawls. The join worked two ways: **exact matches** where the Shopify host matches the Tranco domain directly (e.g., `fashionnova.com`), and **subdomain matches** where a Shopify host sits under a Tranco domain (e.g., `shop.delta.com` under `delta.com`). After filtering noise domains (myshopify.com, cloudfront.net, generic ccTLD-like domains like uk.com), two very different patterns emerged.

## Two ways to use Shopify

```
Exact match                          Subdomain match

fashionnova.com ──── Shopify         delta.com ──── Delta's own infra
                                       └── shop.delta.com ──── Shopify
The store IS the domain.
Shopify-native DTC brand.            The store is tucked on a subdomain.
                                     Invisible unless you check headers.
```

**Exact matches** are what most people think of. The Shopify store IS the website. `fashionnova.com`, `allbirds.com`, `kyliecosmetics.com`. These are Shopify-native brands.

**Subdomain matches** are different. A major brand runs its primary site on its own infrastructure, but tucks a Shopify store onto `shop.brand.com` or `merch.brand.com`. The parent domain ranks high on Tranco. The Shopify store inherits that domain authority while being nearly invisible to anyone not looking at HTTP headers.

Here's how those two patterns break down across Tranco rankings:

| Tranco tier | Exact matches | Subdomain matches |
|-------------|--------------|-------------------|
| Top 1,000 | 0 | 30 |
| Top 10,000 | 12 | 220 |
| Top 100,000 | 907 | 1,763 |

Zero. Not a single Shopify-native brand cracks the top 1,000 most popular websites. But 30 of the top 1,000 websites run Shopify stores on their subdomains. At the top of the web, Shopify is everywhere and nowhere: powering commerce for massive brands while remaining invisible to the typical "who uses Shopify?" conversation.

## The names

You may already know some of these. Shopify has public case studies for a few, and some are findable on BuiltWith if you know where to look. But most have no public association with Shopify at all.

### Tech and platforms

| Tranco rank | Brand | Shopify store |
|-------------|-------|---------------|
| 58 | **X (Twitter)** | shop.x.com |
| 758 | **Xbox** | gear.xbox.com |
| 834 | **OnlyFans** | store.onlyfans.com |
| 860 | **Figma** | store.figma.com |
| 874 | **Kick** | shop.kick.com |
| 1,952 | **Miro** | shop.miro.com |
| 2,154 | **Semrush** | merch.semrush.com |
| 2,461 | **Node.js** | store.nodejs.org |
| 2,988 | **Postman** | store.postman.com |


### Consumer electronics

| Tranco rank | Brand | Shopify store |
|-------------|-------|---------------|
| 326 | **Xiaomi** | spare-parts.mi.com |
| 699 | **Ring (Amazon)** | eu.ring.com, en-uk.ring.com, jp.ring.com (15 regional stores) |
| 3,062 | **MSI** | us-store.msi.com, de-store.msi.com (10 regional stores) |
| 3,074 | **Panasonic** | shop.panasonic.com |

### Media and publishing

| Tranco rank | Brand | Shopify store |
|-------------|-------|---------------|
| 175 | **SoundCloud** | store.soundcloud.com |
| 203 | **Forbes** | licensingstore.forbes.com |
| 312 | **Nature** | shop.nature.com (6 regional stores) |
| 455 | **Fox News** | shop.foxnews.com |
| 735 | **New York Post** | shop.nypost.com |
| 761 | **LA Times** | store.latimes.com |
| 1,921 | **IGN** | store.ign.com |
| 2,671 | **New Scientist** | shop.newscientist.com |
| 3,496 | **HBO** | shop.hbo.com |

### Universities

| Tranco rank | Brand | Shopify store |
|-------------|-------|---------------|
| 360 | **Stanford** | store.stanford.edu (3 stores) |
| 565 | **UC Berkeley** | gardenshop.berkeley.edu |
| 1,759 | **UT Austin** | utlinestore.utexas.edu |
| 1,809 | **UC San Diego** | rentals.ucsd.edu (3 stores) |
| 3,571 | **U of Waterloo** | wstore.uwaterloo.ca |

### Government and nonprofits

| Tranco rank | Brand | Shopify store |
|-------------|-------|---------------|
| 271 | **Wikimedia** | store.wikimedia.org |
| 678 | **UNESCO** | shop.unesco.org |
| 1,604 | **EFF** | shop.eff.org |
| 2,260 | **Signal** | shop.signal.org |
| 2,851 | **UNDP** | shop.undp.org |
| 3,040 | **American Cancer Society** | shop.cancer.org (4 stores) |
| 3,178 | **NYC.gov** | a856-citystore.nyc.gov |
| 3,306 | **European Space Agency** | shop.esa.int |

### Retail, airlines, and automotive

| Tranco rank | Brand | Shopify store |
|-------------|-------|---------------|
| 450 | **Walmart** | beautybox.walmart.com |
| 719 | **Home Depot** | homedecoratorscabinetry.homedepot.com |
| 1,997 | **Ford** | merchandise.ford.com, dealermerch.ford.com |
| 3,086 | **Delta Airlines** | shop.delta.com |
| 3,275 | **Honeywell** | safety-training.honeywell.com |

### Entertainment and sports

| Tranco rank | Brand | Shopify store |
|-------------|-------|---------------|
| 442 | **Duolingo** | store.duolingo.com |
| 846 | **Merriam-Webster** | shop.merriam-webster.com |
| 868 | **Discogs** | merch.discogs.com |
| 1,785 | **Hulu** | shop.hulu.com |
| 2,012 | **NBA** | balstore.nba.com |
| 2,028 | **Blizzard** | gear.blizzard.com |

## Meanwhile, the DTC brands

The stores most people associate with Shopify are further down the popularity rankings than you might expect:

| Tranco rank | Brand |
|-------------|-------|
| 5,052 | Wyze |
| 9,432 | Linksys |
| 9,909 | Fashion Nova |
| 11,330 | HarperCollins |
| 16,396 | Alo Yoga |
| 19,196 | Society6 |
| 21,559 | NZXT |
| 21,817 | Forever 21 |
| 22,276 | Gibson |
| 22,326 | Reebok |
| 24,146 | Stanley |
| 26,268 | Steve Madden |
| 26,414 | Everlane |
| 26,540 | David's Bridal |
| 26,635 | Decathlon |
| 26,757 | McCormick |
| 26,952 | The Body Shop |
| 28,767 | Skims |
| 28,901 | Kith |
| 36,713 | Allbirds |
| 37,414 | Away |
| 38,382 | Glossier |
| 39,006 | Casper |
| 57,795 | ColourPop |
| 61,246 | Harry's |
| 86,617 | Kylie Cosmetics |
| 100,482 | Brooklinen |

Fashion Nova, arguably Shopify's most famous store, ranks #9,909. Meanwhile, 30 brands above rank #1,000 are running Shopify on subdomains. The platform's actual reach into the biggest websites in the world is an order of magnitude higher than the DTC narrative suggests.

## What this means

Shopify's public story is about empowering entrepreneurs. Their investor materials highlight merchant count and GMV growth. But the data shows a parallel enterprise story that's much less visible: the world's biggest brands using Shopify as invisible commerce infrastructure.

This matters for how you think about the platform. When Ring (Amazon) runs 15 regional stores on Shopify, that's not a DTC play. It's a Fortune 500 company choosing Shopify as its global commerce backend for a product line. When Ford runs separate dealer merch and employee merch stores, that's enterprise procurement. When the European Space Agency, NYC.gov, and the UNDP all independently land on Shopify, that's a signal about where institutional commerce defaults are heading.
