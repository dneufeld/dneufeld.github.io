---
layout: post
title: "The Most-Visited Shopify Stores Aren't the Ones You Think"
permalink: /most-visited-shopify-stores/
description: "A Tranco overlay on 1.3 million Shopify hosts reveals two different Shopify worlds: big brands quietly using Shopify on subdomains, and a surprisingly global exact-match ranking led by Indian and Pakistani brands."
image: /assets/most-visited-shopify-stores-card.png
---

*Disclosure: I'm a former Shopify employee and current shareholder. This is not financial advice.*

In the [first post]({% post_url 2026-03-11-common-crawl-shopify-llms %}), I used Common Crawl to build a host-level dataset of Shopify stores. For this follow-up, I wanted to answer a narrower question: what happens when you overlay a popularity ranking on top of one representative dense crawl?

I joined roughly 1.3 million Shopify hosts from **CC-MAIN-2025-43**, the last dense crawl, against the [Tranco top 1M](https://tranco-list.eu/) domain ranking. The result split into two very different patterns:

- `exact` matches, where the Shopify store is the ranked domain itself
- `subdomain` matches, where a larger site tucks Shopify onto `shop.brand.com`, `store.brand.com`, or similar

The subdomain matches are the familiar "big brands quietly using Shopify" story. The exact matches tell a different story: once you sort Shopify-native domains by traffic, a surprising number of the top-ranked stores are Indian and Pakistani brands that barely register on more Western-centric rankings.

## The overlay

[Tranco](https://tranco-list.eu/) is a research-oriented popularity ranking. It aggregates several independent sources and smooths them over time, which makes it more useful for this kind of comparison than any single traffic list.

Shopify hosts came from the same pipeline as post 1: archived Common Crawl WAT responses, scanned for Shopify-specific DNS and HTTP signals. For the Tranco overlap, I used the single crawl partition **CC-MAIN-2025-43**, normalized hostnames by stripping `www.`, and joined them against Tranco in two ways:

```text
Shopify hosts (1.3M)          Tranco top 1M
from CC-MAIN-2025-43          domain rankings
       │                            │
       ▼                            │
  normalize domains                 │
  (strip www., filter noise)        │
       │                            │
       └──────────┬─────────────────┘
                  │
            join on domain
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
   exact match         subdomain match
  (host = domain)    (host under domain)
```

Noise domains such as `myshopify.com`, `cloudfront.net`, and generic suffix traps like `uk.com` were filtered out before looking at the overlap.

## Two match types

```text
Exact match                          Subdomain match

fashionnova.com ──── Shopify         delta.com ──── Delta's main site
                                       └── shop.delta.com ──── Shopify
The store IS the domain.             The store lives on a subdomain.
Shopify-native storefront.           Bigger site, smaller Shopify surface.
```

This distinction matters because Tranco ranks the parent domain. If `shop.delta.com` is on Shopify, Tranco is telling us Delta is a very popular website, not that its merch store alone drives that rank.

Still, the contrast is sharp enough to be useful:

| Tranco tier | Exact matches | Subdomain matches |
|-------------|---------------|-------------------|
| Top 1,000 | 0 | 30 |
| Top 10,000 | 12 | 220 |
| Top 100,000 | 907 | 1,763 |

The first exact match does not appear until **Wyze at Tranco #5,052**. At the very top of the web, Shopify mostly shows up as commerce infrastructure hidden inside larger sites.

## Subdomain matches: Shopify inside bigger sites

Sorted by Tranco rank, the upper end of the overlap is dominated by subdomain matches:

| Tranco rank | Org | Sector | Shopify host |
|-------------|-----|--------|--------------|
| 58 | X | Tech/platform | `shop.x.com` |
| 175 | SoundCloud | Media/platform | `store.soundcloud.com` |
| 203 | Forbes | Media | `licensingstore.forbes.com` |
| 271 | Wikimedia | Nonprofit | `store.wikimedia.org` |
| 312 | Nature | Publishing | `shop.nature.com` |
| 360 | Stanford | University | `store.stanford.edu` |
| 450 | Walmart | Retail | `beautybox.walmart.com` |
| 699 | Ring (Amazon) | Consumer electronics | `eu.ring.com` |
| 758 | Xbox | Gaming | `gear.xbox.com` |
| 860 | Figma | Software | `store.figma.com` |
| 1,997 | Ford | Automotive | `merchandise.ford.com` |
| 2,012 | NBA | Sports | `balstore.nba.com` |
| 2,461 | Node.js | Open source | `store.nodejs.org` |
| 3,086 | Delta Air Lines | Travel | `shop.delta.com` |
| 3,178 | NYC.gov | Government | `a856-citystore.nyc.gov` |

This is the part that changes the usual mental model. If you start from "famous Shopify brands," you think Fashion Nova or Allbirds. If you start from a popularity-ranked host overlay, you run into X, Walmart, Stanford, Delta, and Wikimedia.

But that is only half the story.

## Exact-match domains: a very different top 50

I then took the `exact` side of the same overlap and sorted it by Tranco rank. These are domains where the Shopify storefront appears to be the primary site on the ranked domain:

| # | Domain | Tranco rank | Region |
|--:|--------|------------:|--------|
| 1 | `wyze.com` | 5,052 | US |
| 2 | `nanit.com` | 6,083 | US |
| 3 | `jbhifi.com.au` | 6,712 | Australia |
| 4 | `comfrt.com` | 6,840 | US |
| 5 | `august.com` | 8,589 | US |
| 6 | `boat-lifestyle.com` | 8,913 | India |
| 7 | `linksys.com` | 9,432 | US |
| 8 | `stylo.pk` | 9,668 | Pakistan |
| 9 | `limelight.pk` | 9,737 | Pakistan |
| 10 | `zellbury.com` | 9,758 | Pakistan |
| 11 | `discoverpilgrim.com` | 9,824 | India |
| 12 | `fashionnova.com` | 9,909 | US |
| 13 | `donorbox.org` | 11,094 | US |
| 14 | `harpercollins.com` | 11,330 | US |
| 15 | `myfonts.com` | 11,696 | US |
| 16 | `giva.co` | 12,500 | India |
| 17 | `nishatlinen.com` | 12,717 | Pakistan |
| 18 | `sensibo.com` | 13,373 | Israel |
| 19 | `nixplay.com` | 13,542 | US |
| 20 | `worldofbooks.com` | 15,242 | UK |
| 21 | `aloyoga.com` | 16,396 | US |
| 22 | `flyingtiger.com` | 16,957 | Denmark |
| 23 | `ezlo.com` | 18,705 | US |
| 24 | `brilliant.tech` | 18,771 | US |
| 25 | `lockly.com` | 19,071 | US |
| 26 | `society6.com` | 19,196 | US |
| 27 | `nightcafe.studio` | 19,660 | US |
| 28 | `32degrees.com` | 20,667 | US |
| 29 | `westside.com` | 20,692 | India |
| 30 | `ackermans.co.za` | 21,494 | South Africa |
| 31 | `libas.in` | 21,502 | India |
| 32 | `nzxt.com` | 21,559 | US |
| 33 | `forever21.com` | 21,817 | US |
| 34 | `campusshoes.com` | 21,991 | India |
| 35 | `pepstores.com` | 22,008 | South Africa |
| 36 | `gibson.com` | 22,276 | US |
| 37 | `peachmode.com` | 22,295 | India |
| 38 | `deodap.in` | 22,324 | India |
| 39 | `reebok.com` | 22,326 | US |
| 40 | `palmonas.com` | 22,490 | India |
| 41 | `edenrobe.com` | 22,512 | Pakistan |
| 42 | `ethnc.com` | 22,776 | India |
| 43 | `cabaia.fr` | 22,904 | France |
| 44 | `littleboxindia.com` | 22,976 | India |
| 45 | `outfitters.com.pk` | 22,980 | Pakistan |
| 46 | `redtape.com` | 23,054 | India |
| 47 | `saya.pk` | 23,212 | Pakistan |
| 48 | `beechtree.pk` | 23,331 | Pakistan |
| 49 | `uaudio.com` | 23,777 | US |
| 50 | `stanley1913.com` | 24,146 | US |

Fashion Nova is #12. Alo Yoga is #21. Some familiar Shopify names are near the top, but others land much further down the exact-match list: Kith is #72, ColourPop is #265, and Kylie Cosmetics is #664. The overall shape is still different from the Shopify canon most Western tech readers have in their heads. Indian and Pakistani domains show up over and over again.

## Is this a Tranco artifact?

That was my first reaction too.

Tranco is a composite ranking, so I pulled the underlying source lists and compared a handful of South Asian domains against better-known Western brands:

| Domain | Tranco | CrUX | CF Radar | Umbrella | Majestic |
|--------|-------:|-----:|---------:|---------:|---------:|
| `stylo.pk` | 9,668 | 5,000 | <200,000 | - | 461,491 |
| `limelight.pk` | 9,737 | 10,000 | <200,000 | - | 709,590 |
| `zellbury.com` | 9,758 | 5,000 | <100,000 | - | 739,546 |
| `nishatlinen.com` | 12,717 | 5,000 | >200,000 | - | 730,606 |
| `saya.pk` | 23,212 | 5,000 | <200,000 | - | - |
| `fashionnova.com` | 9,909 | 10,000 | <20,000 | 49,883 | 16,963 |
| `aloyoga.com` | 16,396 | 50,000 | <20,000 | 60,358 | 22,090 |
| `wyze.com` | 5,052 | 100,000 | <5,000 | 3,529 | 30,653 |

Two different patterns show up immediately.

Western brands are visible across multiple sources. Fashion Nova, Alo Yoga, and Wyze appear in DNS-based rankings, backlink-based rankings, and Tranco.

The South Asian domains mostly do not. They show up strongly in **CrUX**, the Chrome UX Report, but barely register in Umbrella, Cloudflare Radar, or Majestic.

Across the exact-match dataset behind this analysis, that pattern is broad:

- 98% of South Asian domains appear in CrUX, versus 82% of non-South Asian domains
- 1% of South Asian domains appear in Umbrella, versus 15% of non-South Asian domains

So this does not look like one weird domain slipping through. It looks like a real traffic pattern that only one source consistently captures.

## Why CrUX matters here

CrUX is probably the most direct signal in the mix. It measures real page loads from opted-in Chrome users. That makes it closer to user behavior than resolver-specific DNS data or Western-web backlink graphs, but it also makes it explicitly Chrome-centric rather than web-wide. Because so much ecommerce traffic is mobile, browser mix matters a lot here: markets with heavy Chrome-on-Android usage can show up more clearly, while Safari-heavy or app-heavy shopping behavior can be undercounted. With that caveat, it still helps explain the gap:

- **Cisco Umbrella** depends on OpenDNS resolver usage, which is weak in South Asia
- **Majestic** measures backlinks, and backlinks reflect the English-language web's link structure more than actual shopping traffic
- **Cloudflare Radar** is useful for broad DNS demand, but smaller shopping sites may not generate enough query volume to rank well there

If a domain is heavily used by shoppers in India or Pakistan, CrUX is far more likely to see it than a Western-centric resolver or backlink index.

## What these stores actually are

These are not a bunch of random long-tail boutiques. A few examples:

### Pakistan

| Domain | Brand | Why it matters |
|--------|-------|----------------|
| `stylo.pk` | Stylo | 250+ stores across 100+ cities, founded in 1974 |
| `limelight.pk` | Limelight | ~85 stores grown from a single Lahore boutique |
| `zellbury.com` | Zellbury | 50+ stores, backed by Al-Rahim Textile Group |
| `nishatlinen.com` | Nishat Linen | Part of Nishat Group, one of Pakistan's largest conglomerates |
| `outfitters.com.pk` | Outfitters | 100+ company-owned stores across Pakistan |

### India

| Domain | Brand | Why it matters |
|--------|-------|----------------|
| `boat-lifestyle.com` | boAt | India's #1 wearable brand, IPO approved |
| `giva.co` | GIVA | 100+ stores, major venture backing |
| `westside.com` | Westside | Tata Group retail brand, parent company Trent at roughly $2B revenue |
| `campusshoes.com` | Campus | Publicly listed, 250+ stores |
| `redtape.com` | Red Tape | Publicly listed, roughly 390+ stores |

That is why the list matters. These are not obscure curiosities. They are large consumer brands, public companies, and retail chains with meaningful physical footprints and revenue.

The South Asian cluster is the most striking part of the table, but it is not the only one. Australia, South Africa, France, Denmark, and the UK all show up too. Shopify's exact-match footprint is more global than the familiar US DTC story suggests.

## What this says about measuring the web

The combined picture is the useful part.

- At the top of Tranco, Shopify often shows up on subdomains of already-large brands and institutions
- In the exact-match ranking, the Shopify-native domains skew much more international than the usual Western brand narrative suggests

That does **not** mean Tranco is a proxy for GMV, and it does not mean every exact match is a perfect representation of a company's whole business. But it does show that two different "Shopify stories" are hiding inside the same overlap:

- Shopify as hidden commerce infrastructure for large parent brands
- Shopify as the primary storefront for a surprisingly global set of merchants, including a strong Indian and Pakistani cluster

If you only look at case studies or well-known Western DTC brands, you miss both.

## Caveats

- This analysis uses **CC-MAIN-2025-43**, the last dense crawl, not a multi-crawl union
- Tranco ranks **traffic**, not revenue, GMV, or strategic importance
- CrUX is Chrome-centric, not browser-neutral. On a mobile-heavy web, differences in Chrome, Safari, and in-app shopping behavior can create real visibility gaps.
- `exact` versus `subdomain` is a hostname classification, not a perfect statement about every page on a domain
- Headless or heavily customized Shopify storefronts are a known weak spot. If the frontend hides enough Shopify-specific DNS or HTTP signals, this host-level method can under-detect them or miss them entirely. That may help explain why some expected brands, such as Gymshark, do not appear here.
- Domain normalization here strips `www.`, but does not do full PLD extraction for every ccTLD edge case

## Reproducing the overlap

These tables come from the Tranco overlap script, which defaults to `CC-MAIN-2025-43`:

```bash
python scripts/analyze_tranco_overlap.py --summary-only
python scripts/analyze_tranco_overlap.py --match-type subdomain --clean --top 500
python scripts/analyze_tranco_overlap.py --match-type exact --top 100
```
