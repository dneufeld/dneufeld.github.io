---
layout: post
title: "Building a Common Crawl Search Engine in a Day with Turbopuffer"
permalink: /common-crawl-search-turbopuffer/
description: "A recipe-style build log for parsing Common Crawl WET files, indexing them into turbopuffer, shipping a web UI, and benchmarking the first million documents."
image: /assets/fuguhocho-sushi-desktop.png
---

I wanted to see what I could get done in a day with zero prior experience building a search engine, Codex handling the plumbing, and Claude Design helping turn the result into something you could actually use.

The answer, at least for a prototype: a working pipeline, a usable UI, and enough measurements to know what to improve next.

<figure>
  <img src="../assets/fuguhocho-sushi-desktop.png" alt="Fugu Hocho search UI showing Common Crawl results for sushi">
  <figcaption>The one-day search UI, pointed at a pinned Common Crawl slice. The live version is at <a href="https://fuguhocho.com/?q=sushi">fuguhocho.com/?q=sushi</a>.</figcaption>
</figure>

In a day, I got from public Common Crawl WET files to a working search UI at `fuguhocho.com`, with AWS spot workers indexing plaintext web pages into turbopuffer, SQS handling the work queue, Cloudflare serving the frontend, and a benchmark harness collecting query latencies.

This was an educational outing as much as an implementation project. I do not have deep search-engine experience. The point was to learn by building the smallest honest version of the thing, then let the benchmark data tell me where my assumptions were wrong.

This is the nerdier and more useful thing first: a recipe for building the pipeline, plus the early numbers and mistakes.

## The shape of the thing

Common Crawl publishes web data in a few formats. For a first search prototype, WET is the easy mode: extracted plaintext from crawled pages.

```text
Common Crawl WET files
plain text web pages
        |
        v
Python parser
language filter, schema mapping, deterministic IDs
        |
        v
SQS work queue
one WET path per message
        |
        v
EC2 spot workers in us-east-1
download, parse, batch, write
        |
        v
turbopuffer namespace
BM25 full-text search over `text`
        |
        v
Cloudflare Worker
fuguhocho.com search UI
```

The design goal was boring infrastructure:

- No Kubernetes.
- No autoscaling group.
- No bespoke scheduler.
- Spot instances are disposable.
- SQS is the source of truth for unfinished work.
- S3 stores the run artifacts.
- turbopuffer owns the search backend.

That is the right amount of machinery for a proof of concept. More orchestration would have slowed the first version down. Less orchestration would have made spot interruptions and retries harder to reason about.

One important caveat: turbopuffer's own performance guidance recommends keeping namespaces small when you can do so without routinely querying across many of them. Smaller namespaces should be faster to query and index. I still started with a single namespace because I wanted the first version to be understandable before adding query fanout, result merging, reciprocal rank fusion, and all the other machinery that arrives the moment "one index" becomes "many indexes."

So the single-namespace design is not the final architecture. It is the first controlled baseline.

## The dataset

I pinned one Common Crawl snapshot: `CC-MAIN-2026-17`.

For Phase 1, I built deterministic WET-file prefix slices:

| Slice | Manifest | Status |
|---|---|---|
| `~1M` docs | `manifests/cc-main-2026-17-wet-125.txt` | complete |
| `~10M` docs | `manifests/cc-main-2026-17-wet-1250.txt` | in progress |

The 1M manifest is a strict prefix subset of the 10M manifest, which makes scale comparisons easier. This is reproducible, but not perfect. For a more rigorous future benchmark, I would switch to URL-hash nested slices so the benchmark is less sensitive to Common Crawl file ordering.

The first document schema stayed minimal:

| Field | Purpose |
|---|---|
| `id` | deterministic UUID for idempotent upserts |
| `url` | result URL |
| `domain` | domain filter |
| `crawl_id` | crawl provenance |
| `wet_path` | source WET file |
| `wet_record_index` | source record offset within the WET file |
| `language` | Common Crawl identified language |
| `text_bytes` | body size metric |
| `content_digest` | source digest |
| `text` | BM25 full-text field |

The effective turbopuffer full-text config, captured from namespace metadata:

| Parameter | Value |
|---|---|
| Tokenizer | `word_v3` |
| Language | `english` |
| Stemming | `true` |
| Stopword removal | `false` |
| ASCII folding | `false` |
| BM25 `k1` | `1.2` |
| BM25 `b` | `0.75` |
| BM25 `k3` | `8.0` |

That metadata capture matters. Benchmark configs are what you intended to test. Backend metadata is what you actually tested.

## Local smoke test

The first target was not "index the web." It was "can I parse one shard and get a real search result?"

```bash
uv run fugu ingest-local \
  --manifest manifests/cc-main-2026-12-wet-10.txt \
  --namespace fugu-wet-10-smoke \
  --run-id wet-10-smoke
```

Ten WET files produced 82,546 primary-English documents from 196,129 WET records.

That run caught two useful things immediately:

- Mixed-language WET headers need careful handling.
- The first BM25 query can be much slower than repeated warm queries.

That second point matters for benchmarks. Cold and warm numbers should not be averaged together because they describe different user experiences and different backend states.

## Moving to AWS

Common Crawl data lives in S3, so the workers run in `us-east-1` to avoid cross-region transfer costs.

The initial EC2 shape was:

- S3 bucket for source bundles and run artifacts.
- Secrets Manager for the turbopuffer API key.
- EC2 instance profile with scoped S3, SQS, and Secrets Manager access.
- Spot instances that self-terminate when done.
- SQS queue for work distribution.

Representative launch command:

```bash
uv run fugu-fleet \
  --bucket fugu-benchmarks-545048695557 \
  --manifest manifests/cc-main-2026-17-wet-125.txt \
  --branch main \
  --upload-source-bundle \
  --run-id phase1-1m-native-v1-20260507a \
  --namespace fugu-phase1-1m-native-v1-20260507a \
  --workers 2 \
  --instance-type c7a.large \
  --instance-type c6a.large \
  --instance-type m7a.large \
  --instance-type m6a.large \
  --work-mode sqs \
  --write-rate-limit-seconds 1 \
  --document-id-format uuid \
  --sqs-visibility-timeout-seconds 1800 \
  --index-timeout-seconds 43200
```

The important part is the queue design:

```text
SQS work queue
125 WET messages for the 1M run
        |
        +-- worker 0 pulls a WET file
        +-- worker 1 pulls a WET file
        +-- ...

SQS write-token queue
one shared token for the namespace
        |
        v
only one write proceeds at a time
```

Why serialize writes? Because the first bigger attempt showed turbopuffer write backpressure. The correct response was not "launch more instances and hope." The better response was to make backpressure explicit, preserve queue state, and collect enough metrics to tune batch size and worker count. It also made it obvious that I still had a lot to learn about turbopuffer write efficiency: batch sizing, concurrent writes, namespace layout, and which limits matter in practice.

## Reconciliation

If you want benchmark numbers to mean anything, you need to know whether you indexed the corpus you think you indexed.

The reconciler checks:

- Every manifest WET file has a completion record.
- No WET file completed twice.
- `records_kept == rows_written`.
- Missing work remains visible in SQS instead of silently disappearing.

```bash
uv run fugu-reconcile \
  --manifest manifests/cc-main-2026-17-wet-125.txt \
  --run-id phase1-1m-native-v1-20260507a \
  --bucket fugu-benchmarks-545048695557
```

For the clean 1M run:

| Metric | Value |
|---|---:|
| WET files completed | 125 |
| Records seen | 2,710,645 |
| Records kept | 1,128,727 |
| Rows written | 1,128,727 |
| Write batches | 125 |
| Write retries | 18 |
| Missing WET files | 0 |
| Duplicate WET files | 0 |

turbopuffer namespace metadata reported 1,128,727 rows and 7.92 GB logical bytes.

## The web UI

The UI is intentionally thin:

- Cloudflare Worker.
- Static frontend assets.
- `/api/search` endpoint.
- Query string in, top 10 BM25 results out.
- Links back to the original URLs.

The first version asks turbopuffer to return the full `text` field for each result and then truncates it in the browser. That is wasteful, but useful as a baseline because it matches what the first UI actually shipped.

Once you measure it, you can improve it without lying to yourself.

## Query benchmark

The benchmark harness writes raw JSONL, Parquet, namespace metadata, candidate config, and markdown summaries:

```bash
uv run fugu-query-benchmark \
  --candidate benchmark-candidates/phase1/tpuff-1m-native-v1-fulltext.json \
  --namespace fugu-phase1-1m-native-v1-20260507a \
  --run-id phase1-1m-native-v1-fulltext-20260507a
```

The first query set is tiny, only five queries repeated 30 times each. This is not enough for relevance claims. It is enough to catch latency shape and API-return mistakes.

The current UI behavior returns full text:

| Query | p50 client ms | p90 client ms | p99 client ms | Max client ms | Returned bytes |
|---|---:|---:|---:|---:|---:|
| `cats` | 39.0 | 46.2 | 348.1 | 469 | 197,773 |
| `climate_change` | 45.0 | 55.2 | 407.9 | 550 | 233,556 |
| `machine_learning` | 45.0 | 50.0 | 792.3 | 1,091 | 299,153 |
| `open_source_database` | 39.0 | 68.2 | 317.7 | 409 | 104,926 |
| `search_engine` | 38.0 | 47.4 | 553.4 | 746 | 143,427 |

Then I ran the same namespace with metadata-only results:

| Query | p50 client ms | p90 client ms | p99 client ms | Max client ms | Returned bytes |
|---|---:|---:|---:|---:|---:|
| `cats` | 32.0 | 38.0 | 48.0 | 50 | 2,318 |
| `climate_change` | 31.0 | 36.0 | 36.7 | 37 | 2,888 |
| `machine_learning` | 31.0 | 39.0 | 74.8 | 82 | 2,393 |
| `open_source_database` | 31.0 | 36.3 | 45.0 | 47 | 2,353 |
| `search_engine` | 30.0 | 37.1 | 58.9 | 67 | 2,332 |

The takeaway is not mysterious: returning 196 KB of text is slower than returning 2.5 KB of metadata. In this small run, metadata-only roughly halved mean client latency and made the tail much less exciting.

The next UI profile should return stored snippets, not full bodies. Search results need enough text to be useful, not the full document body.

## What surprised me

### EC2 was mostly bored

My prior Common Crawl work was a [Shopify scanner](https://dneufeld.github.io/common-crawl-shopify-llms/) where horizontal scaling was essential. More workers meant more WAT files scanned in parallel, and the bottleneck was mostly local parsing and S3 throughput. I came into this project assuming the same shape would apply here.

That assumption was wrong, or at least incomplete. The early larger runs used `m7a.xlarge` instances, but host profiles showed low CPU and memory utilization. With a single namespace and explicit write backpressure, local compute was not the bottleneck.

That is my naive first-pass understanding of turbopuffer, not a claim about a turbopuffer deficiency. The one-day MVP used the simplest architecture I could reason about. The next layer of work is to understand turbopuffer write efficiency better: larger batches, concurrent writes, namespace layout, and when a multi-namespace fanout design is worth the added query complexity.

For the next clean runs, I moved down to `*.large` spot instances. If the backend write path is limiting throughput, extra local vCPUs are not the first thing to optimize.

### More workers do not automatically mean more throughput

More instances help when the bottleneck is parsing, downloading, or independent namespace writes.

More instances do not help much when every worker is politely waiting to write into the same namespace. That is why the queue design matters: it lets workers come and go safely, but it does not pretend one namespace has infinite write concurrency.

### Batch size matters

One WET file per write was simple and correct, but underused turbopuffer's documented write batch cap. The next iteration coalesces multiple WET files into larger writes, targeting 256 MB while staying under the 512 MB request cap.

That is the kind of optimization worth making after the baseline works. Before that, it is easy to optimize the wrong part of the pipeline.

## Next

The immediate next steps:

- Finish the clean 10M namespace and run the same query benchmark.
- Re-run ingestion with coalesced writes and compare docs/sec, retries, and wall-clock time.
- Add a snippet-return search profile.
- Turn the raw benchmark artifacts into charts.
- Keep every run reproducible enough that future-me cannot hand-wave past present-me's mistakes.

That last one is the real benchmark harness.
