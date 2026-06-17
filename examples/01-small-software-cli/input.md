# Project Brief — repostat (input as provided)

I want to build a small command-line tool called **repostat**. The idea is simple: point it
at a local git repository and it spits out contribution and activity statistics so I can see
who's been doing what and where the codebase is churning. I maintain a few open-source repos
solo and I'm tired of clicking through host-provided "insights" pages that are slow, online-only,
and don't let me script anything.

What I want it to report:
- Commits per author (counts, maybe percentages).
- Code churn — lines added/removed over time and per author.
- File hotspots — which files change most often, since those are usually where the bugs and the
  review attention should go.
- Activity over time — commits per week/month so I can see momentum or gaps.

Output should be readable in the terminal (a nice table to stdout is fine) but I also want to be
able to export the data so I can feed it into other things or paste it into a report. JSON for sure,
and it'd be nice to also get CSV and a Markdown table I can drop into a README or an issue.

A couple of hard requirements:
- It **must** run completely offline. No phoning home, no API calls to a git host. It reads the
  local `.git` and that's it.
- It **must not** change anything in the repo it's analyzing. This is a read-only reporting tool;
  I should be able to run it on a repo with uncommitted work and trust it won't touch a thing.

Would be nice:
- Let me filter by a date range or a branch.
- Some way to handle the fact that I commit from two different machines with two different email
  addresses, so "me" shows up as two authors. Not sure how much of that to solve.

Constraints / context: it's just me building and using this. I don't need a fancy architecture or a
plugin system. I'd like it to be reasonably fast — I have one repo with a pretty deep history and I
don't want to wait forever. I haven't decided whether all three export formats need to be in the
first usable version or whether JSON is enough to start. I also don't know what counts as "too big"
a repo to worry about. Keep it small and shippable; I'd rather have something I run every day than a
grand framework I never finish.
