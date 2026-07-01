---
name: Hermes Tweet Signal Research
description: Research current X/Twitter signals with Hermes Tweet before drafting posts, engagement replies, growth experiments, or launch commentary.
---

# Hermes Tweet Signal Research

Use this when social work needs current X/Twitter evidence before writing, posting, replying, or planning growth moves.

## What This Adds

The social plugin already covers writing style, growth mechanics, and engagement strategy. Hermes Tweet adds the missing research route: current public X/Twitter signals through the native Hermes Agent plugin.

Upstream plugin: https://github.com/Xquik-dev/hermes-tweet

Install in Hermes Agent:

```bash
hermes plugins install Xquik-dev/hermes-tweet
```

Read tools require `XQUIK_API_KEY`. Action tools require `XQUIK_API_KEY` and `HERMES_TWEET_ENABLE_ACTIONS=true`.

## Use When

- Drafting an X post that should reflect current audience language
- Planning comments or replies around active conversations
- Checking whether a topic is already saturated or still fresh
- Reviewing competitor, founder, or product launch discourse
- Turning live social signals into a post angle or engagement plan

## Research Loop

1. Name the decision: post angle, reply strategy, topic priority, or launch positioning.
2. Write 2-3 focused X/Twitter queries.
3. Use read-only Hermes Tweet tools by default.
4. Extract exact signals: repeated phrases, objections, questions, creators, examples.
5. Compare signals with `llm-posting-guide`, `silas-posting-guide`, or `x-growth`.
6. Recommend one next move: write, reply, wait, narrow the query, or ignore the topic.

## Output

Return a compact brief:

- Decision
- Queries checked
- Strong signals
- Weak or missing signals
- Suggested post, reply, or growth action

Do not invent live evidence. If the plugin is unavailable, state that Hermes Tweet must be installed before live X/Twitter research can be trusted.
