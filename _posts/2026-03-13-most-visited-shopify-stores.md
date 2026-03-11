---
layout: post
title: "The Most-Visited Shopify Stores Aren't the Ones You Think"
permalink: /most-visited-shopify-stores/
description: "Ranking Shopify-native domains by Tranco reveals major Indian and Pakistani merchants that Western web rankings largely miss."
---

*Disclosure: I'm a former Shopify employee and current shareholder. This is not financial advice.*

In my [last post]({% post_url 2026-03-12-biggest-websites-shopify %}) I showed that the biggest *brands* using Shopify are hiding on subdomains - X, Walmart, Stanford, the European Space Agency. But those are subdomain matches: the brand runs its own site and tucks Shopify onto `shop.brand.com`. The Shopify store isn't the main attraction.

A different question: which Shopify stores get the most actual user traffic? Where the store IS the whole website?

I expected Fashion Nova, Allbirds, maybe Kylie Cosmetics. I was wrong.

## The top 50

I took the 14,500 domains where a Shopify store is the entire website and ranked them by [Tranco](https://tranco-list.eu/), a research-grade popularity ranking that combines DNS traffic (Cloudflare Radar, Cisco Umbrella), real browser usage (Chrome UX Report), and passive DNS (Farsight), averaged over 30 days.

Method in brief: this is the subset of detected Shopify hosts where the storefront appears to be the primary site on that domain, not a Shopify store tucked under a larger non-Shopify parent. I used Tranco for the initial ranking, then pulled the underlying source lists to see whether the South Asian result was broad-based or driven by one component.

Here are the top 50:

| # | Domain | Tranco rank | Region |
|--:|--------|----------:|--------|
| 1 | wyze.com | 5,052 | US |
| 2 | nanit.com | 6,083 | US |
| 3 | jbhifi.com.au | 6,712 | Australia |
| 4 | comfrt.com | 6,840 | US |
| 5 | august.com | 8,589 | US |
| 6 | boat-lifestyle.com | 8,913 | **India** |
| 7 | linksys.com | 9,432 | US |
| 8 | stylo.pk | 9,668 | **Pakistan** |
| 9 | limelight.pk | 9,737 | **Pakistan** |
| 10 | zellbury.com | 9,758 | **Pakistan** |
| 11 | discoverpilgrim.com | 9,824 | **India** |
| 12 | fashionnova.com | 9,909 | US |
| 13 | donorbox.org | 11,094 | US |
| 14 | harpercollins.com | 11,330 | US |
| 15 | myfonts.com | 11,696 | US |
| 16 | giva.co | 12,500 | **India** |
| 17 | nishatlinen.com | 12,717 | **Pakistan** |
| 18 | sensibo.com | 13,373 | Israel |
| 19 | nixplay.com | 13,542 | US |
| 20 | worldofbooks.com | 15,242 | UK |
| 21 | aloyoga.com | 16,396 | US |
| 22 | flyingtiger.com | 16,957 | Denmark |
| 23 | ezlo.com | 18,705 | US |
| 24 | brilliant.tech | 18,771 | US |
| 25 | lockly.com | 19,071 | US |
| 26 | society6.com | 19,196 | US |
| 27 | nightcafe.studio | 19,660 | US |
| 28 | 32degrees.com | 20,667 | US |
| 29 | westside.com | 20,692 | **India** |
| 30 | ackermans.co.za | 21,494 | South Africa |
| 31 | libas.in | 21,502 | **India** |
| 32 | nzxt.com | 21,559 | US |
| 33 | forever21.com | 21,817 | US |
| 34 | campusshoes.com | 21,991 | **India** |
| 35 | pepstores.com | 22,008 | South Africa |
| 36 | gibson.com | 22,276 | US |
| 37 | peachmode.com | 22,295 | **India** |
| 38 | deodap.in | 22,324 | **India** |
| 39 | reebok.com | 22,326 | US |
| 40 | palmonas.com | 22,490 | **India** |
| 41 | edenrobe.com | 22,512 | **Pakistan** |
| 42 | ethnc.com | 22,776 | **India** |
| 43 | cabaia.fr | 22,904 | France |
| 44 | littleboxindia.com | 22,976 | **India** |
| 45 | outfitters.com.pk | 22,980 | **Pakistan** |
| 46 | redtape.com | 23,054 | **India** |
| 47 | saya.pk | 23,212 | **Pakistan** |
| 48 | beechtree.pk | 23,331 | **Pakistan** |
| 49 | uaudio.com | 23,777 | US |
| 50 | stanley1913.com | 24,146 | US |

Fashion Nova is #12. Alo Yoga is #21. The names most people associate with Shopify are there. But roughly half the top 50 are South Asian brands — Pakistani and Indian fashion, footwear, and lifestyle companies. If you're in Western tech, you've probably never heard of any of them.

## Is the ranking wrong?

My first reaction was skepticism. Tranco is a composite - maybe one of its sources has a bias toward South Asian domains? I downloaded the four individual rankings that feed into Tranco and cross-referenced them.

| Source | What it measures | How it ranks |
|--------|-----------------|-------------|
| [CrUX](https://developer.chrome.com/docs/crux) (Chrome UX Report) | Actual page loads from opted-in Chrome users | Bucketed (top 5K, 10K, 50K, etc.) |
| [Cloudflare Radar](https://radar.cloudflare.com/domains) | DNS queries to Cloudflare's 1.1.1.1 resolver | Bucketed |
| [Cisco Umbrella](https://umbrella-static.s3-us-west-1.amazonaws.com/index.html) | DNS queries to OpenDNS resolvers | Exact rank, top 1M |
| [Majestic Million](https://majestic.com/reports/majestic-million) | Referring subnets (inbound backlinks) | Exact rank, top 1M |

Here's how the South Asian domains compare to Western brands across all five sources:

| Domain | Tranco | CrUX | CF Radar | Umbrella | Majestic |
|--------|-------:|-----:|---------:|---------:|---------:|
| **stylo.pk** | 9,668 | **5,000** | <200,000 | - | 461,491 |
| **limelight.pk** | 9,737 | **10,000** | <200,000 | - | 709,590 |
| **zellbury.com** | 9,758 | **5,000** | <100,000 | - | 739,546 |
| **nishatlinen.com** | 12,717 | **5,000** | >200,000 | - | 730,606 |
| **saya.pk** | 23,212 | **5,000** | <200,000 | - | - |
| fashionnova.com | 9,909 | 10,000 | <20,000 | 49,883 | 16,963 |
| aloyoga.com | 16,396 | 50,000 | <20,000 | 60,358 | 22,090 |
| wyze.com | 5,052 | 100,000 | <5,000 | 3,529 | 30,653 |

Two completely different patterns.

**Western brands** show up consistently across all sources. Fashion Nova is top 10K-50K on every ranking. Wyze is top 5K on Cloudflare, 3,500 on Umbrella. They're visible everywhere you look.

**South Asian brands** show up on CrUX only. Stylo.pk is in the top 5,000 on Chrome browser usage but doesn't appear at all in Umbrella's top million. Majestic ranks Nishat Linen at 730,606 — a site that Chrome says is more visited than Alo Yoga.

Out of 475 South Asian domains in our dataset, only 5 (1%) appear in Cisco Umbrella's top million. But 466 (98%) appear in CrUX. For non-South Asian domains, those numbers are 15% and 82%.

## The traffic is real

CrUX is the most direct signal here. It measures actual page loads from opted-in Chrome users, so it avoids the resolver-adoption issues in DNS-based rankings and the link-graph bias in backlink-based ones. It is still Chrome-only and opt-in, but for this question it is much closer to user behavior than the other sources.

The reason these brands are mostly invisible on everything else:

- **Cisco Umbrella** runs on OpenDNS resolvers, which have negligible adoption in South Asia
- **Majestic** measures backlinks from the broader web — South Asian shopping sites have almost no inbound links from English-language websites
- **Cloudflare Radar** (1.1.1.1) is popular in South Asia for general DNS, but individual shopping sites don't generate enough query volume to crack its rankings

CrUX is the only source in this comparison that consistently captures what people in India and Pakistan are doing in their browsers. And what it shows is meaningful traffic to these Shopify stores.

## What these stores actually are

These aren't scrappy DTC startups. Here's who's in the top 50:

### Pakistan

| Domain | Brand | What they do | Scale |
|--------|-------|-------------|-------|
| stylo.pk | **Stylo** | Women's footwear and accessories | 250+ stores across 100+ cities. Founded 1974. On Shopify Plus. |
| limelight.pk | **Limelight** | Eastern and Western apparel | ~85 stores. Grew from a single Lahore boutique in 2010. |
| zellbury.com | **Zellbury** | Affordable fashion ("Real Fashion, Real Prices") | 50+ stores. Founded 2016. Backed by Al-Rahim Textile Group. |
| nishatlinen.com | **Nishat Linen** | Fabrics, garments, home decor | Part of **Nishat Group**, Pakistan's largest conglomerate (~$2.1B group sales). Owned by Pakistan's first Forbes billionaire. Listed on Pakistan Stock Exchange. |
| saya.pk | **Saya** | Premium women's wear | Backed by Al Razzaq Fibres, a major textile supplier. Also has a US-facing store (sayausa.com). |
| beechtree.pk | **BeechTree** | Women's ready-to-wear | ~20 stores. Strong online presence relative to physical footprint. |
| outfitters.com.pk | **Outfitters** | Western casual wear for youth | 100+ company-owned stores (no franchises). Also runs "Ethnic by Outfitters." |
| edenrobe.com | **Edenrobe** | Men's and women's apparel | 70+ stores. Founded 1988. One of few brands in this group with significant men's wear. |

These eight Pakistani brands operate over 650 physical retail stores between them. Several are backed by Pakistan's largest textile conglomerates — companies that manufacture the fabrics, then sell direct to consumers through Shopify-powered storefronts.

### India

| Domain | Brand | What they do | Scale |
|--------|-------|-------------|-------|
| boat-lifestyle.com | **boAt** | Audio products, wearables | India's #1 wearable brand (27-29% market share). ~$370M revenue. IPO approved at >$1.5B valuation. |
| discoverpilgrim.com | **Pilgrim** | Vegan beauty and skincare | ~$50M revenue, 5x growth in two years. VC-backed. |
| giva.co | **GIVA** | Silver and lab-grown diamond jewelry | ~$60M revenue, 100+ stores. Premji Invest (Wipro founder) is an investor. |
| westside.com | **Westside** | Private-label fashion | **Tata Group** brand. Parent Trent Limited: ~$2B revenue, 248 stores. Listed on NSE/BSE. |
| libas.in | **Libas** | Women's ethnic and fusion wear | ~$73M revenue. Bootstrapped to $60M+ before taking any outside capital. |
| campusshoes.com | **Campus** | Sports and athleisure footwear | ~$200M revenue, 250+ stores, 17% of India's branded sports footwear market. Publicly listed (2022 IPO). |
| redtape.com | **Red Tape** | Footwear and apparel | ~$240M revenue, 390+ stores. Publicly listed, ~$800M market cap. |
| littleboxindia.com | **Littlebox** | Gen Z ultra-fast fashion | Founded 2022 in Guwahati (Northeast India). Featured on Shark Tank India. 104% YoY growth. |

Three of these are publicly listed on Indian stock exchanges. One is part of the Tata Group. boAt alone has an approved IPO targeting a $1.5 billion valuation — larger than many publicly traded Western DTC brands. Westside's parent company Trent added 280+ stores in a single year.

## Beyond South Asia

The South Asian cluster is the most dramatic, but the pattern extends to other regions. In our top 1,000 exact matches:

| Region | Shopify stores | Examples |
|--------|---------------|----------|
| UK | 17 | Disturbia, Fenwick, Pink Boutique |
| Australia | 12 | JB Hi-Fi, Culture Kings, The Good Guys |
| South Africa | 12 | Ackermans, Edgars, Legit |
| France | 9 | Cabaïa, Pimkie, Beauté Privée |
| Germany | 8 | More Nutrition, Westwing, Hobbii |
| Brazil | 6 | Stanley 1913 BR, Insider Store |
| Mexico | 6 | Cuadra, New Era MX, Waldo's |
| Japan | 3 | Chiikawa Market, Converse JP |

Shopify's merchant base is genuinely global. But you'd never know it from Western-centric ranking systems.

## What this tells us about measuring the web

Web popularity rankings have a structural blind spot. Three of Tranco's four sources are DNS-based, and DNS resolver adoption varies dramatically by region. One source is backlink-based, and backlinks reflect the English-language web's link structure. In this comparison, CrUX is the only source that directly measures what users do in their browsers regardless of geography.

The result: a Pakistani footwear chain with 250 physical stores and 50 years of history is invisible to most ranking systems. A Tata Group subsidiary with $2 billion in revenue doesn't show up on Cisco Umbrella. India's largest wearable brand, preparing for a billion-dollar IPO, has no Majestic backlink profile to speak of.

These stores aren't undiscovered. They serve hundreds of millions of people. They're just invisible to the tools most English-speaking analysts use to measure the web.

If you're building on web ranking data — for research, for SEO analysis, for understanding market share — and you're not checking CrUX alongside DNS and backlink signals, you're missing a significant chunk of the internet's commercial activity.

---

## Next angle

One follow-up question worth measuring: performance. As far as I know, Shopify still doesn't operate database regions outside the US. These South Asian stores serve overwhelmingly domestic customers - Pakistani shoppers buying from Pakistani merchants, Indian shoppers buying from Indian brands. Every storefront request round-trips to North America. CrUX includes Core Web Vitals (LCP, FID, CLS) broken down by origin. Pulling CrUX performance data for these stores and comparing it against US-based Shopify stores would quantify how much the single-region architecture costs merchants in South Asia. Shopify's CDN and edge caching help with static assets, but checkout, cart, and dynamic pages still hit the origin.
