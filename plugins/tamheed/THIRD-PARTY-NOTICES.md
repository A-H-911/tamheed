# Third-party notices

The Tamheed bundle is stdlib-only Python and carries no runtime dependency beyond the `mcp` SDK
the server fetches. One module is a port of third-party code and keeps its license here.

## `server/ste_lint.py`

A port of `scripts/ste-lint.py` from [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill)
(`master` at commit `7d4a135`, 2026-09-08). The rule regexes for semicolons, phrasal verbs,
marketing adjectives, nominalizations, passive voice and compound tenses, the Markdown table
handling and the dangling-conjunction check come from that file. Tamheed added the paragraph
join, the frontmatter and Python-literal extractors, the vocabulary tables, the Arabic rules and
the allow marker. The `plain-english` skill's text is Tamheed's own and cites the same project.

```text
MIT License

Copyright (c) 2026 Dustin Yuchen Teng

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

ASD-STE100 itself (the specification and its dictionary) is the property of the AeroSpace and
Defence Industries Association of Europe. Nothing of it is reproduced here. The structural rules
are paraphrased from the public description of the standard.
