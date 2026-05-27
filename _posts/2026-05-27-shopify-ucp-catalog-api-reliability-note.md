---
layout: post
title: "A Small UCP Catalog API Reliability Note"
permalink: /shopify-ucp-catalog-api-reliability-note/
description: "A short public journal note about a reproducible Shopify UCP Catalog API 500, backend timeout-shaped errors, and why agent-facing APIs need clean reliability boundaries."
image: /assets/shopify-ucp-reliability-card.svg
---

*Disclosure: I'm a former Shopify employee and current shareholder. This is not financial advice. I also reported the behavior described below to Shopify before publishing.*

I've been having a blast vibecoding on top of Shopify UCP and the Catalog APIs. I've been building a bunch of little prototypes against both the global catalog and individual merchant catalogs, and it is honestly a little wild that these APIs exist and are this easy to build on.

That is part of why this edge case stuck with me. The surface is powerful enough to unlock a whole new class of commerce experiences, so the boring reliability details suddenly feel a lot more important. Agent-facing APIs invite automated clients by design. Clean errors, bounded query shapes, and predictable backend resource controls are not glamorous, but they matter.

This came out of poking at Shopify's newly announced UCP / agentic commerce surface. The launch was publicly discussed by Shopify, including Ilya Grigorik's announcement post on X:

<blockquote class="twitter-tweet">
  <a href="https://twitter.com/igrigorik/status/2056417991693312370">Ilya Grigorik's UCP announcement on X</a>
</blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
<noscript>
  <p><a href="https://x.com/igrigorik/status/2056417991693312370">Ilya Grigorik's UCP announcement on X</a></p>
</noscript>

## Disclosure

Before publishing this note, I shared the behavior with Shopify in two ways:

1. I reported it through Shopify's security bug bounty program.
2. I also disclosed it privately via DMs.

Shopify reviewed the bug bounty submission and closed it as not a valid security vulnerability.

That is fine. I am not publishing this as a confirmed vulnerability, exploit, or proof of practical denial of service. I'm publishing it as a small reliability and API-hardening observation around a new agentic commerce surface.

## Minimal reproduction

Single request observed against a Shopify storefront UCP MCP endpoint:

```bash
curl -sS -w '\nHTTP_STATUS=%{http_code}\nTIME_TOTAL=%{time_total}\n' \
  -X POST 'https://fnova.myshopify.com/api/ucp/mcp' \
  -H 'content-type: application/json' \
  -H 'accept: application/json' \
  --data @fnova-dress-limit-200.json
```

Request body:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": "fnova-dress-limit-200-repro",
  "params": {
    "name": "search_catalog",
    "arguments": {
      "meta": {
        "ucp-agent": {
          "profile": "https://shopify.dev/ucp/agent-profiles/2026-04-08/valid-with-capabilities.json"
        }
      },
      "catalog": {
        "query": "dress",
        "context": {
          "address_country": "US",
          "currency": "USD",
          "intent": "Shopping this merchant's catalog for products matching the buyer query."
        },
        "pagination": {
          "limit": 200
        }
      }
    }
  }
}
```

Observed response:

```text
HTTP 500
~3.07s total time

Internal error calling tool search_catalog:
3024: Query execution was interrupted, maximum statement execution time exceeded (trilogy_read_row)
```

## Why it caught my attention

There are two separate issues here.

First, the API returns a raw-ish infrastructure flavored error. `trilogy_read_row` looks like an implementation detail escaping through the API boundary.

Second, a cheap client request appears to drive backend database work until a statement timeout interrupts it.

That does not automatically mean "DoS." It does mean the API may be letting expensive query shapes get too far downstream before rejecting them.

Even if there is no security impact here, the baseline behavior is still surprising. A public UCP API can be made to return an improperly handled 500 with a simple request, and the error appears to expose database-layer implementation detail. For a newly promoted agentic commerce API, that is worth fixing even if it never becomes more than a reliability bug.

## An agent-specific wrinkle

One agent-specific wrinkle: my coding agent did not immediately know what to do with this.

It saw a valid-looking UCP tool call return a JSON-RPC internal error and initially treated it like an ordinary tool failure to route around. The database timeout detail was not part of the UCP contract, and it took human steering to frame it correctly: Shopify was returning the 500, the timeout was server-side, it was reproducible, and a database implementation detail appeared to be leaking through the API boundary.

The practical issue was not just recognizing the error. I also had to steer the agent toward bisecting the request shape that triggered it. In this case, the failure was sensitive to the requested pagination limit, but the "safe" limit was not a fixed number across shops or queries. Some requests worked at higher limits, while others failed at lower ones depending on the merchant catalog and query.

That matters when you are prototyping on top of an agent-first API. A human can look at this and say, "back off the limit, binary search the working range, cache the result, and treat this as a server-side guardrail." An agent may just see a transient tool failure, retry the same shape, or add brittle one-off handling.

In my prototypes, the workaround became programmatic: lower the requested limit when the Storefront UCP endpoint returned this timeout-shaped 500, retry with a smaller page size, and avoid assuming that one globally safe limit exists.

That is a new-ish wrinkle for agent-facing APIs. Error payloads are not just for humans reading curl output anymore. Agents will consume them and decide whether to retry, fan out, back off, degrade gracefully, or report a bug. Muddy error boundaries can produce muddy agent behavior.

## Napkin math

Assume one request causes about 3 seconds of backend MySQL read/query time.

```text
backend query time = number of requests * 3 seconds
```

| Requests | Approx backend query time created | Equivalent |
|---:|---:|---:|
| 100 | 300 seconds | 5 minutes |
| 1,000 | 3,000 seconds | 50 minutes |
| 10,000 | 30,000 seconds | 8.3 hours |
| 100,000 | 300,000 seconds | 83.3 hours |
| 1,000,000 | 3,000,000 seconds | 34.7 days |

That table is intentionally crude. It does not mean this amount of work would all hit one database, one shard, one replica, or one resource pool. Shopify's public engineering writing makes it clear this is not a small database setup. They have written about hundreds of MySQL shards, writers with five or more replicas, thousands of database VMs, KateSQL on GKE, and large MySQL instances. One KateSQL post mentions an 80GB InnoDB buffer pool during debugging.

I also assume Shopify has other load shedding, circuit breakers, throttles, and isolation mechanisms that would prevent this from turning into a practical DoS. The interesting part, at least to me, is what you might start thinking about once you know a public agent-facing API can reliably reach a 3-second MySQL query execution timeout.

The real question is where this work lands.

```text
single shop endpoint?
  -> one merchant-specific read replica?
  -> a shared storefront catalog service?
  -> global catalog infrastructure?
  -> a sharded index path?
```

From the outside, I do not know.

If the request is isolated to a large read-replica pool with strict rate limits, this may just be ugly error handling. If requests can be spread across many storefronts, or if many shops converge onto a smaller shared backend path, the resource asymmetry becomes more interesting.

I do not think the public evidence is enough to call this a security vulnerability. My read is simpler: this is not a smoking gun, but it is a weird edge in a shiny new API surface.

Agentic commerce APIs invite automated clients by design. That makes boring reliability controls matter a lot: clean errors, bounded query shapes, early rejection, rate limiting, tenant isolation, and careful resource accounting.

If anyone has a benign way to reason about whether this is merely messy error handling or something with real resource-amplification potential, I'd be interested.

## References

- [Ilya Grigorik announcement post](https://x.com/igrigorik/status/2056417991693312370)
- [Shopify UCP product page](https://www.shopify.com/ucp)
- [Shopify, "Building the Universal Commerce Protocol"](https://shopify.engineering/UCP)
- [Shopify, "The agentic commerce platform"](https://www.shopify.com/news/ai-commerce-at-scale)
- [Shopify, "Upgrading MySQL at Shopify"](https://shopify.engineering/upgrading-mysql-shopify)
- [Shopify, "Debugging Systems in the Cloud: MySQL, Kubernetes, and Cgroups"](https://shopify.engineering/debugging-systems-cloud-mysql-kubernetes-cgroups)
- [Shopify, "Horizontally Scaling the Rails Backend of Shop App with Vitess"](https://shopify.engineering/horizontally-scaling-the-rails-backend-of-shop-app-with-vitess)
