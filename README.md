# B2B SaaS Cold Outreach Research

## Project Goal

This repository supports research into B2B SaaS cold outreach experts. The aim is to collect, organize, and analyze public expert content so it can later be distilled into a practical outbound playbook.

## Research Methodology

The research process is intentionally source-first:

1. Identify credible cold outreach experts, operators, and practitioners.
2. Collect public educational content from LinkedIn, YouTube, and other relevant sources.
3. Store raw or lightly formatted material in the appropriate research folders.
4. Track source links and context in `research/sources.md`.
5. Analyze recurring principles, frameworks, tactics, examples, and objections.

No collected expert content has been added yet.

## Repository Structure

```text
research/
  sources.md
  linkedin-posts/
  youtube-transcripts/
  other/

scripts/
  youtube_collector.py
  linkedin_formatter.py

data/
```

- `research/sources.md`: Index of experts, source links, and collection notes.
- `research/linkedin-posts/`: Future storage for collected LinkedIn post text.
- `research/youtube-transcripts/`: Future storage for YouTube transcript exports.
- `research/other/`: Future storage for articles, newsletters, podcast notes, or other source types.
- `scripts/youtube_collector.py`: Placeholder for YouTube transcript collection tooling.
- `scripts/linkedin_formatter.py`: Placeholder for formatting LinkedIn research exports.
- `data/`: Future location for structured datasets created from the research.

## How Content Is Collected

Content should be collected from public sources and stored with enough context to preserve attribution. Each source should include the expert name, platform, URL, date collected, and brief notes about why it is relevant.

YouTube transcripts will be stored under `research/youtube-transcripts/`. LinkedIn posts will be stored under `research/linkedin-posts/`. Any source that does not fit those categories can be stored under `research/other/`.

## Future Goal

The long-term goal is to turn expert knowledge into an outbound playbook for B2B SaaS teams. After enough source material is collected, the research can be synthesized into repeatable guidance for positioning, prospecting, message writing, personalization, follow-up, objection handling, and campaign iteration.
