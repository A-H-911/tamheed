# Sample package — invalid fixture

This package is identical in shape to the valid fixture but carries **seeded
defects** so the validator's critical gates have something to catch. Each
defect is annotated in the file where it lives. The test suite asserts that the
validator flags every one of them.

Seeded defects:

- G-IDS: a dangling cross-reference (`DEC-099`, never defined) and a malformed
  identifier (`FR-7`).
- G-DEC-STATUS: a decision row with an empty status.
- G-REQ-SRC: a functional requirement with an empty source.
- G-COMPLETE: an unfinished marker and a placeholder token left in the charter.
- G-TRACE: an MVP requirement missing its test link.

(The literal trigger tokens live in the annotated artifacts, not here, so each
finding points at the file that owns the defect.)
