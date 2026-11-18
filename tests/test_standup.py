"""Plan 233 (ADR-0003): the standup engine. State, deltas, checkpoint replay, the window, facts.

The tool that writes report rows arrives in plan 235. These tests record a report the way the
tool will: compute the draft, then insert the row and move it to Approved through the
connection.
"""
from __future__ import annotations

import json
import random
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "plugins" / "tamheed" / "server"))

import standup as S  # noqa: E402
import standup_page as P  # noqa: E402
import standup_facts as F  # noqa: E402
import tamheed_server as srv  # noqa: E402

NEVER = (lambda text: False)


class EngineTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        srv.PACKAGE_ROOT = Path(self._tmp.name)
        srv.package_create("pkg", "Pkg", "rnd")
        self.conn = srv._CURRENT.conn
        self.n = 0

    def tearDown(self):
        if srv._CURRENT is not None:
            srv.package_close()
        self._tmp.cleanup()

    # ------------------------------------------------------------------ helpers

    def up(self, *rows):
        rows = [dict({"lifecycle_status": "Proposed"}, **r) if r["type"] == "decision"
                else r for r in rows]               # a decision is born Proposed, no default
        out = srv.entity_upsert(rows)
        self.assertTrue(out["ok"], out)

    def journal(self, text, kind="work-done"):
        self.assertTrue(srv.progress_update([{"entry": text, "event_type": kind}])["ok"])

    def tables(self):
        return srv.ENTITY_TABLES.values()

    def draft(self, start=None):
        base, kind, _note, err = S.select_base(self.conn, start)
        self.assertIsNone(err)
        return base, kind, S.compute(self.conn, self.tables(), base, kind)

    def record(self, start=None, offset="+03:00", ended="2026-11-16T06:00:00Z"):
        base, kind, out = self.draft(start)
        self.n += 1
        rid = f"RPT-{self.n:03d}"
        row = {"id": rid, "kind": kind, "seq": out["seq"],
               "base_report": (base or {}).get("id"),
               "checkpoint": int(out["checkpoint"]), "pe_to": out["pe_to"],
               "av_to": out["av_to"], "ended_at": ended, "utc_offset": offset,
               "state_digest": out["digest"], "state_delta": json.dumps(out["delta"]),
               "facts": "{}", "rule_colour": "green"}
        self.conn.execute(f"INSERT INTO standup_reports ({', '.join(row)}) VALUES"
                          f" ({', '.join('?' * len(row))})", list(row.values()))
        ok, why = S.verify(self.conn, row)
        self.assertTrue(ok, why)
        self.conn.execute(
            "UPDATE standup_reports SET narrative = '{\"headline\": \"h\"}', colour = 'green',"
            " recorded_by = 'human:op', operator_words = 'record it', recorded_at = ?,"
            " lifecycle_status = 'Approved' WHERE id = ?", (ended, rid))
        return rid, out

    # ------------------------------------------------------------------ the state

    def test_the_blocked_list_reads_the_far_end(self):
        """Plan 241 (the field's FB-020, R121, R129): the list read only the edge, so a met
        dependency still blocked its slice. A far end now blocks only while it is not
        settled, by one rule per family. Each far-end family is here, open and settled.
        A slice whose every blocker is settled is free to start (R130)."""
        self.up({"type": "phase", "id": "PH-1", "title": "P"},
                {"type": "slice", "id": "SL-001", "title": "Blocked", "phase_id": "PH-1"},
                {"type": "slice", "id": "SL-002", "title": "Free", "phase_id": "PH-1"})
        sev = {"severity": "low"}
        gate = {"type": "execution-gate", "gate_kind": "approval", "definition": "d"}
        pairs = [
            ({"type": "dependency", "id": "DEP-001", "title": "d"},
             {"type": "dependency", "id": "DEP-002", "title": "d",
              "lifecycle_status": "Implemented"}),
            ({"type": "assumption", "id": "ASM-001", "title": "a"},
             {"type": "assumption", "id": "ASM-002", "title": "a", "lifecycle_status": "Rejected"}),
            ({"type": "wbs-item", "id": "WBS-1.1", "title": "w", "slice_id": "SL-002"},
             {"type": "wbs-item", "id": "WBS-1.2", "title": "w", "slice_id": "SL-002",
              "lifecycle_status": "Implemented"}),
            ({"type": "execution-plan", "id": "EP-001", "slice_id": "SL-002", "plan": "p"},
             {"type": "execution-plan", "id": "EP-002", "slice_id": "SL-002", "plan": "p",
              "lifecycle_status": "Superseded"}),
            ({"type": "defect", "id": "DEF-001", "title": "x", **sev},
             {"type": "defect", "id": "DEF-002", "title": "x", "lifecycle_status": "Fixed", **sev}),
            ({"type": "deferred-work", "id": "DW-001", "title": "x", **sev},
             {"type": "deferred-work", "id": "DW-002", "title": "x", "lifecycle_status": "Done",
              **sev}),
            ({"type": "open-question", "id": "OQ-001", "title": "q"},
             {"type": "open-question", "id": "OQ-002", "title": "q", "resolution": "answered"}),
            ({"type": "decision", "id": "DEC-001", "title": "d"},
             {"type": "decision", "id": "DEC-002", "title": "d", "lifecycle_status": "Approved"}),
            ({"type": "risk", "id": "RISK-001", "title": "r"},
             {"type": "risk", "id": "RISK-002", "title": "r", "risk_state": "mitigated"}),
            (dict(gate, id="GATE-001"), dict(gate, id="GATE-002", outcome="Go")),
        ]
        for open_row, done_row in pairs:
            self.up(open_row, done_row)
        edge = {"type": "trace-edge", "relation": "blocked_by"}
        self.up(*[dict(edge, from_id="SL-001", to_id=row["id"]) for pair in pairs for row in pair])
        self.up(*[dict(edge, from_id="SL-002", to_id=done["id"]) for _, done in pairs])
        listed = F.blocked(self.conn)
        self.assertEqual(sorted(it["note"] for it in listed if it["id"] == "SL-001"),
                         sorted(f"blocked by {o['id']}" for o, _ in pairs))
        self.assertNotIn("SL-002", [it["id"] for it in listed])
        self.assertEqual(F.lifted(self.conn),
                         {"SL-002": sorted((d["id"] for _, d in pairs), key=F._key)})
        self.assertNotIn("NOPE-1", F.settled_ids(self.conn))     # a missing row never settles
        # R135: the readiness predicates decide two edge cases, and the docs state both
        self.up({"type": "open-question", "id": "OQ-003", "title": "q",
                 "lifecycle_status": "Deferred"},
                {"type": "risk", "id": "RISK-003", "title": "r", "lifecycle_status": "Obsolete"})
        done = F.settled_ids(self.conn)
        self.assertIn("OQ-003", done)              # a Deferred question lifts its block
        self.assertNotIn("RISK-003", done)         # a retired risk still `open` keeps blocking

    def test_state_skips_the_journal_verdicts_reports_and_edges(self):
        self.journal("did a thing")
        live, cols = S.state(self.conn, self.tables())
        for skipped in S.STATE_SKIP:
            self.assertNotIn(skipped, live)
            self.assertNotIn(skipped, cols)
        self.assertIn("decisions", cols)          # an empty family still has its columns

    def test_fingerprint_skips_nulls_and_last_referenced(self):
        row = {"id": "DEC-001", "title": "t", "rationale": None}
        self.assertEqual(S.fingerprint(row), S.fingerprint({"id": "DEC-001", "title": "t"}))
        self.assertEqual(S.fingerprint(row), S.fingerprint(dict(row, last_referenced="x")))
        self.assertNotEqual(S.fingerprint(row), S.fingerprint(dict(row, title="u")))

    def test_diff_then_apply_is_the_identity(self):
        rng = random.Random(233)
        for _ in range(200):
            def rand_state():
                return {t: {f"X-{i}": rng.choice(["a|1", "b|2", "a|3"])
                            for i in range(rng.randint(0, 6))}
                        for t in rng.sample(["t1", "t2", "t3"], rng.randint(0, 3))}
            base, live = rand_state(), rand_state()
            base = {t: m for t, m in base.items() if m}
            live = {t: m for t, m in live.items() if m}
            bc = {t: ["id", "a"] for t in base}
            lc = {t: ["id", rng.choice(["a", "b"])] for t in live}
            got, cols = S.apply(base, bc, S.diff(base, bc, live, lc))
            self.assertEqual(got, live)
            for t in lc:
                self.assertEqual(cols[t], lc[t])

    def test_an_unknown_delta_version_is_refused(self):
        with self.assertRaisesRegex(ValueError, "unknown to this engine"):
            S.apply({}, {}, {"v": 99})

    # ------------------------------------------------------------------ the chain

    def test_the_first_report_is_a_checkpoint_with_the_full_state(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "use SQLite"})
        _rid, out = self.record()
        self.assertTrue(out["first"])
        self.assertTrue(out["checkpoint"])
        self.assertTrue(out["delta"]["checkpoint"])
        self.assertIn("DEC-001", out["delta"]["set"]["decisions"])

    def test_replay_equals_each_drafts_state(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "a"})
        self.record()
        self.up({"type": "decision", "id": "DEC-002", "title": "b"})
        _rid, second = self.record()
        self.assertFalse(second["checkpoint"])
        self.assertEqual(set(second["delta"]["set"]["decisions"]), {"DEC-002"})
        replayed, _cols, broken = S.replay(S.chain(self.conn))
        self.assertIsNone(broken)
        self.assertEqual(S.digest(replayed), second["digest"])

    def test_replay_names_a_corrupted_middle_link(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "a"})
        self.record()
        self.up({"type": "decision", "id": "DEC-002", "title": "b"})
        self.record()
        self.up({"type": "decision", "id": "DEC-003", "title": "c"})
        self.record()
        self.conn.execute("PRAGMA writable_schema = 0")
        self.conn.execute("DROP TRIGGER trg_standup_reports_immutable")   # a hand edit of data/
        bad = json.dumps({"v": 1, "columns": {}, "set": {"decisions": {"DEC-002": "x|y"}},
                          "drop": {}})
        self.conn.execute("UPDATE standup_reports SET state_delta = ? WHERE id = 'RPT-002'",
                          (bad,))
        _st, _cols, broken = S.replay(S.chain(self.conn))
        self.assertEqual(broken, "RPT-002")
        base, kind, _n, _e = S.select_base(self.conn, None)
        out = S.compute(self.conn, self.tables(), base, kind)
        self.assertEqual(out["broken"], "RPT-002")
        self.assertTrue(out["checkpoint"])          # the next report re-baselines

    def test_every_30th_daily_report_is_a_checkpoint(self):
        flags = []
        for k in range(31):
            self.up({"type": "decision", "id": f"DEC-{k + 1:03d}", "title": "d"})
            _rid, out = self.record()
            flags.append(out["checkpoint"])
        self.assertEqual([k + 1 for k, f in enumerate(flags) if f], [1, 30])
        self.assertEqual(S.chain(self.conn)[0]["id"], "RPT-030")   # replay starts there
        replayed, _c, broken = S.replay(S.chain(self.conn))
        self.assertIsNone(broken)
        self.assertEqual(S.digest(replayed), out["digest"])

    # ------------------------------------------------------------------ moves

    def test_a_status_move_and_a_text_edit_are_told_apart(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "a"},
                {"type": "decision", "id": "DEC-002", "title": "b"})
        self.record()
        self.up({"type": "decision", "id": "DEC-001", "title": "a",
                 "lifecycle_status": "Approved"},
                {"type": "decision", "id": "DEC-002", "title": "b reworded"},
                {"type": "decision", "id": "DEC-003", "title": "born approved",
                 "lifecycle_status": "Approved"})
        _b, _k, out = self.draft()
        cls = out["cls"]
        self.assertEqual([(t, i, a, b) for t, i, a, b in cls["moved"]],
                         [("decisions", "DEC-001", "Proposed", "Approved")])
        self.assertEqual(cls["edited"], [("decisions", "DEC-002")])
        self.assertEqual(cls["new"], [("decisions", "DEC-003", "Approved")])
        decided = F.moved_to(cls, "decisions", F.S_DECIDED)
        self.assertEqual(sorted(i for i, *_ in decided), ["DEC-001", "DEC-003"])

    def test_a_column_set_change_pauses_edits_and_a_new_family_is_first_counted(self):
        base = {"decisions": {"DEC-001": "Proposed|aaa"}}
        live = {"decisions": {"DEC-001": "Proposed|bbb"}, "lessons": {"LL-001": "Proposed|c"}}
        cls = S.classify(base, {"decisions": ["id", "title"]}, live,
                         {"decisions": ["id", "title", "new_col"], "lessons": ["id"]})
        self.assertEqual(cls["edited"], [])
        self.assertEqual(cls["paused"], ["decisions"])
        self.assertEqual(cls["first_counted"], ["lessons"])
        self.assertEqual(cls["new"], [])

    # ------------------------------------------------------------------ the window

    def test_the_window_reads_a_PE_1x_id_without_raising(self):
        self.journal("first")
        self.assertTrue(srv.entity_upsert([{"type": "progress-entry", "id": "PE-1x",
                                            "entry": "odd id", "event_type": "note"}])["ok"])
        self.assertEqual(S.pe_max(self.conn), 1)
        ids = [e["id"] for e in S.window_entries(self.conn, 1, 1)]
        self.assertEqual(sorted(ids), ["PE-001", "PE-1x"])

    def test_a_rewound_journal_is_refused(self):
        self.journal("one")
        self.journal("two")
        self.record()
        self.conn.execute("DELETE FROM progress_entries WHERE id = 'PE-002'")
        base, kind, _n, _e = S.select_base(self.conn, None)
        out = S.compute(self.conn, self.tables(), base, kind)
        self.assertIn("moved backwards", out["error"])

    def test_the_record_row_is_not_listed_in_the_next_window(self):
        self.journal("work")
        rid, _out = self.record()
        self.conn.execute("INSERT INTO progress_entries (id, entry, actor, occurred_at)"
                          " VALUES ('PE-002', ?, 'system:standup-report', 'now')", (rid,))
        self.journal("more work")
        ids = [e["id"] for e in S.window_entries(self.conn, 2, S.pe_max(self.conn))]
        self.assertEqual(ids, ["PE-003"])

    def test_a_date_snaps_in_the_rows_own_offset(self):
        self.record(offset="+03:00", ended="2026-11-15T22:30:00Z")   # 16 Nov 01:30 local
        self.up({"type": "decision", "id": "DEC-001", "title": "a"})
        self.record(offset="+03:00", ended="2026-11-17T06:00:00Z")
        base, kind, note, err = S.select_base(self.conn, "2026-11-15")
        self.assertIsNone(err)
        self.assertIsNone(base)                    # 01:30 on the 16th is after the 15th
        self.assertEqual((kind, note), ("override", "2026-11-15"))
        base, kind, _n, _e = S.select_base(self.conn, "2026-11-16")
        self.assertEqual((base["id"], kind), ("RPT-001", "override"))
        base, kind, _n, _e = S.select_base(self.conn, "2026-11-30")
        self.assertEqual((base["id"], kind), ("RPT-002", "default"))
        self.assertEqual(S.select_base(self.conn, "15/11")[3],
                         "start is a date (YYYY-MM-DD) or a recorded report id (RPT-NNN)")

    def test_a_report_start_must_be_a_recorded_daily_report(self):
        self.record()
        self.assertEqual(S.select_base(self.conn, "RPT-001")[:2][1], "default")
        err = S.select_base(self.conn, "RPT-009")[3]
        self.assertIn("RPT-009 cannot start a window: it is not a row", err)

    def test_offsets_and_local_times(self):
        self.assertIsNotNone(S.parse_offset("+14:00"))
        self.assertIsNotNone(S.parse_offset("-12:00"))
        for bad in ("+15:00", "-13:00", "+03:10", "03:00", "", None):
            self.assertIsNone(S.parse_offset(bad), bad)
        self.assertEqual(S.shown("2026-11-16T06:05:00Z", "+03:00"),
                         "Mon 16 Nov 2026, 09:05 (UTC+03:00)")
        self.assertEqual(S.normal_offset("-00:00"), "+00:00")

    # ------------------------------------------------------------------ handoff, facts

    def test_handoff_sections_parse_by_heading(self):
        self.journal("1. **Resume at.** Finish WBS-002.\n2. **In flight.** none\n"
                     "3. **Awaiting the operator.** Approve DEC-001?\n  Pick a date.\n"
                     "4. **Verified facts.** gate ok\n5. **Do not carry.** old", kind="handoff")
        got = S.handoff_sections(self.conn)
        self.assertEqual(got["resume at"], ["Finish WBS-002."])
        self.assertEqual(got["awaiting the operator"], ["Approve DEC-001?", "Pick a date."])
        screened = F.needs(self.conn, got, "2026-11-16", lambda t: "Pick" in t, None)
        titles = [it["title"] for it in screened["awaiting_operator"]["items"]]
        self.assertEqual(titles, ["Approve DEC-001?", "withheld: read the latest handoff"])

    def test_given_rulings_never_read_as_requests(self):
        """Plan 250 (Jisr's FB-023, R13, D11): a line under "Awaiting the operator" is cut where
        a sentence starts with "Rulings given". The text before it stays, a line after it
        stays, and the other sections keep the phrase."""
        self.journal("1. **Resume at.** Finish WBS-002.\n"
                     "3. **Awaiting the operator.** Approve DEC-001? Rulings GIVEN this session:"
                     " DEC-002.\n"
                     "Rulings given this session: DEC-003, the date.\n"
                     "  Pick a date.\n"
                     "  Confirm LL-001. **Rulings given:** DEC-004.\n"
                     "  No rulings given yet on FB-001.\n"
                     "4. **Verified facts.** gate ok\n5. **Do not carry.** Rulings given: DEC-005",
                     kind="handoff")
        got = S.handoff_sections(self.conn)
        self.assertEqual(got["awaiting the operator"],
                         ["Approve DEC-001?", "Pick a date.", "Confirm LL-001.",
                          "No rulings given yet on FB-001."])
        self.assertEqual(got["do not carry"], ["Rulings given: DEC-005"])
        self.journal("RESUME AT: WBS-040.\nAWAITING THE OPERATOR: LL-168 (Proposed). The first"
                     " report. Rulings GIVEN this session: DEC-537, DEC-538.", kind="handoff")
        self.assertEqual(S.handoff_sections(self.conn)["awaiting the operator"],
                         ["LL-168 (Proposed). The first report."])


    def test_facts_lists_keep_every_item(self):
        """Plan 251 v2 (U8): no list is capped, a first report or a daily one."""
        self.up(*[{"type": "defect", "id": f"DEF-{k:03d}", "title": f"bug {k}",
                   "severity": "low"} for k in range(1, 41)])
        _b, _k, out = self.draft()
        self.record()
        self.up({"type": "defect", "id": "DEF-041", "title": "bug 41", "severity": "low"})
        _b, _k, out = self.draft()
        facts = F.build(self.conn, cls=out["cls"], live=out["live"], first=False, window=out,
                        today="2026-11-16", blocker_rules=[], screen=NEVER)
        opened = facts["challenges"]["defects_open"]
        self.assertEqual((len(opened["items"]), opened["total"]), (41, 41))
        self.assertIn("overall", facts)
        self.assertEqual(facts["overall"]["families"]["defects"], {"Open": 41})
        self.assertEqual(len(facts["overall"]["lists"]["defects"]), 41)

    def test_rule_colour(self):
        def sections(defects=(), rules=0, risks=0, overdue=0):
            items = [{"id": f"DEF-{k}", "note": sev} for k, sev in enumerate(defects)]
            return {"challenges": {"defects_open": {"items": items, "total": len(items)},
                                   "blocker_rules": {"items": [], "total": rules},
                                   "risks_high": {"items": [], "total": risks}},
                    "needs": {"questions_overdue": {"items": [], "total": overdue}}}
        self.assertEqual(F.rule_colour(sections())[0], "green")
        self.assertEqual(F.rule_colour(sections(defects=("low",)))[0], "green")
        self.assertEqual(F.rule_colour(sections(defects=("critical",)))[0], "red")
        self.assertEqual(F.rule_colour(sections(rules=1))[0], "green")   # SR51
        self.assertEqual(F.rule_colour(sections(risks=1))[0], "amber")
        self.assertEqual(F.rule_colour(sections(overdue=2)), ("amber",
                                                              ["2 overdue questions"]))
        self.assertEqual(F.rule_colour(sections(defects=("high",)))[1],
                         ["1 open critical or high defect"])

    def _row(self, rid, base, kind, out, **extra):
        return dict({"id": rid, "kind": kind, "seq": out["seq"], "base_report":
                     (base or {}).get("id"), "checkpoint": int(out["checkpoint"]),
                     "state_delta": json.dumps(out["delta"]), "state_digest": out["digest"]},
                    **extra)

    def test_an_override_verifies_and_never_enters_the_chain(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "a"})
        self.record()
        self.up({"type": "decision", "id": "DEC-002", "title": "b"})
        self.record()
        self.up({"type": "decision", "id": "DEC-003", "title": "c"})
        base, kind, out = self.draft("RPT-001")
        self.assertEqual((base["id"], kind, out["seq"], out["checkpoint"]),
                         ("RPT-001", "override", None, False))
        self.assertEqual(set(out["delta"]["set"]["decisions"]), {"DEC-002", "DEC-003"})
        self.assertEqual(S.verify(self.conn, self._row("RPT-003", base, kind, out)),
                         (True, None))
        self.assertEqual([r["id"] for r in S.chain(self.conn)], ["RPT-001", "RPT-002"])

    def test_an_override_over_a_broken_link_stores_the_full_state_and_verifies(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "a"})
        self.record()
        self.up({"type": "decision", "id": "DEC-002", "title": "b"})
        self.record()
        self.up({"type": "decision", "id": "DEC-003", "title": "c"})
        self.record()
        self.conn.execute("DROP TRIGGER trg_standup_reports_immutable")
        self.conn.execute("UPDATE standup_reports SET state_digest = 'bad' WHERE id = 'RPT-002'")
        base, kind, out = self.draft("RPT-002")
        self.assertEqual((kind, out["broken"]), ("override", "RPT-002"))
        self.assertTrue(out["delta"]["checkpoint"])
        self.assertEqual(S.verify(self.conn, self._row("RPT-004", base, kind, out)),
                         (True, None))

    def test_a_correction_keeps_its_place_and_verifies_after_the_old_row_moves(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "a"})
        self.record()
        self.up({"type": "decision", "id": "DEC-002", "title": "b"})
        self.record()
        old = dict(zip(("seq", "base_report", "checkpoint", "state_delta", "state_digest"),
                       self.conn.execute(
                           "SELECT seq, base_report, checkpoint, state_delta, state_digest"
                           " FROM standup_reports WHERE id = 'RPT-002'").fetchone()))
        row = dict(old, id="RPT-003", supersedes="RPT-002", kind="default")
        self.assertEqual(S.verify(self.conn, row), (True, None))
        cols = ", ".join(old)
        self.conn.execute(f"INSERT INTO standup_reports (id, kind, supersedes, {cols}, pe_to,"
                          " av_to, ended_at, utc_offset, facts, rule_colour) SELECT 'RPT-003',"
                          f" 'default', 'RPT-002', {cols}, pe_to, av_to, ended_at, utc_offset,"
                          " facts, rule_colour FROM standup_reports WHERE id = 'RPT-002'")
        self.conn.execute("UPDATE standup_reports SET lifecycle_status = 'Superseded'"
                          " WHERE id = 'RPT-002'")
        self.assertEqual(S.verify(self.conn, row), (True, None))
        self.conn.execute(
            "UPDATE standup_reports SET narrative = 'n', colour = 'green', recorded_by ="
            " 'human:op', operator_words = 'w', recorded_at = 't', lifecycle_status ="
            " 'Approved' WHERE id = 'RPT-003'")
        self.assertEqual([r["id"] for r in S.chain(self.conn)], ["RPT-001", "RPT-003"])
        replayed, _c, broken = S.replay(S.chain(self.conn))
        self.assertIsNone(broken)
        self.assertEqual(S.digest(replayed), old["state_digest"])

    def test_verify_catches_drift_since_the_draft(self):
        self.record()
        self.up({"type": "decision", "id": "DEC-001", "title": "a"})
        base, kind, out = self.draft()
        row = {"id": "RPT-002", "base_report": base["id"], "checkpoint": 0,
               "state_delta": json.dumps(out["delta"]), "state_digest": out["digest"]}
        self.assertEqual(S.verify(self.conn, row), (True, None))
        self.assertFalse(S.verify(self.conn, dict(row, state_digest="0" * 64))[0])



GOLDEN = REPO_ROOT / "tests" / "standup_golden"
REGEN = "--regen" in sys.argv


class PageTest(unittest.TestCase):
    """Plan 234: the page is a pure function of its row, inside the review page's frame."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        srv.PACKAGE_ROOT = Path(self._tmp.name)
        with mock.patch.object(srv, "_now", return_value="2026-11-15T05:00:00Z"):
            srv.package_create("pkg", "Payments revamp", "rnd")
        self.conn = srv._CURRENT.conn

    def tearDown(self):
        if srv._CURRENT is not None:
            srv.package_close()
        self._tmp.cleanup()

    def up(self, *rows):
        rows = [dict({"lifecycle_status": "Proposed"}, **r) if r["type"] == "decision"
                else r for r in rows]
        out = srv.entity_upsert(rows)
        self.assertTrue(out["ok"], out)

    def page(self, narrative=None, *, kind_start=None, row_extra=None, exempt=None,
             reasons=()):
        base, kind, snapped, err = S.select_base(self.conn, kind_start)
        self.assertIsNone(err)
        out = S.compute(self.conn, srv.ENTITY_TABLES.values(), base, kind)
        facts = F.build(self.conn, cls=out["cls"], live=out["live"], first=out["first"],
                        window=out, today="2026-11-16", blocker_rules=[], screen=NEVER)
        colour, why = F.rule_colour(facts)
        row = dict({"id": "RPT-001", "kind": kind, "utc_offset": "+03:00",
                    "ended_at": "2026-11-16T06:05:00Z", "state_digest": out["digest"],
                    "rule_colour": colour, "lifecycle_status": "Draft"}, **(row_extra or {}))
        meta = P.meta(row, package="Payments revamp", base=base, birth="2026-11-15",
                      window=out, snapped=snapped, rule_reasons=reasons or why)
        first = out["first"] if exempt is None else exempt
        return P.fit(meta, facts, narrative, exempt=first)

    NARRATIVE = {"headline": "The export works end to end. One defect blocks the release.",
                 "did": "We finished the export (WBS-001).",
                 "challenges": "The login defect is open (DEF-001).",
                 "next": "We fix the defect first.", "plan": "Fix DEF-001, then release.",
                 "colour": "amber", "colour_reason": "One open high defect."}

    def seed(self):
        self.up({"type": "wbs-item", "id": "WBS-001", "title": "Export to CSV",
                 "lifecycle_status": "Implemented"},
                {"type": "defect", "id": "DEF-001", "title": "Login fails on Safari",
                 "severity": "high"},
                {"type": "decision", "id": "DEC-001", "title": "Use SQLite for the cache"})

    def golden(self, name, page):
        path = GOLDEN / f"{name}.html"
        if REGEN:
            GOLDEN.mkdir(exist_ok=True)
            path.write_text(page, encoding="utf-8", newline="\n")
        self.assertEqual(page, path.read_text(encoding="utf-8"), f"{name}: run with --regen")

    def test_the_first_and_a_daily_page_match_their_goldens(self):
        self.seed()
        page, _words = self.page(self.NARRATIVE)
        self.golden("first", page)
        self.assertEqual(page, self.page(self.NARRATIVE)[0])       # same row, same bytes
        self.conn.execute(
            "INSERT INTO standup_reports (id, kind, seq, lifecycle_status, checkpoint, pe_to,"
            " av_to, ended_at, utc_offset, state_digest, state_delta, facts, narrative,"
            " rule_colour, colour, recorded_by, operator_words, recorded_at) VALUES"
            " ('RPT-001', 'default', 1, 'Approved', 1, ?, 0, '2026-11-16T06:05:00Z', '+03:00',"
            " ?, ?, '{}', '{}', 'amber', 'amber', 'human:op', 'record it',"
            " '2026-11-16T06:10:00Z')",
            (S.pe_max(self.conn), *self._first_state()))
        self.up({"type": "wbs-item", "id": "WBS-002", "title": "Import from CSV",
                 "lifecycle_status": "Review"},
                {"type": "decision", "id": "DEC-001", "title": "Use SQLite for the cache",
                 "lifecycle_status": "Approved"})
        daily, _w = self.page(self.NARRATIVE, row_extra={"id": "RPT-002",
                                                        "ended_at": "2026-11-17T06:05:00Z"})
        self.golden("daily", daily)
        self.assertIn("claimed done", daily)
        self.assertIn("waiting for approval → approved", daily)

    def _first_state(self):
        live, cols = S.state(self.conn, srv.ENTITY_TABLES.values())
        return S.digest(live), json.dumps(S.full(live, cols))


    def test_the_page_runs_one_script_named_by_its_hash_and_links_nowhere(self):
        """Plan 251 v2 (U1, ADR-0005): one script, its SHA-256 in the content policy, no other
        script, no inline handler, no outward link."""
        import base64
        import hashlib
        self.seed()
        page, _w = self.page(self.NARRATIVE)
        source = (REPO_ROOT / "plugins/tamheed/server/standup.js").read_text(encoding="utf-8")
        digest = base64.b64encode(hashlib.sha256(source.encode("utf-8")).digest()).decode()
        self.assertIn(f"script-src 'sha256-{digest}'; base-uri 'none'; form-action 'none'",
                      page)
        self.assertEqual(page.count("<script"), 1)
        self.assertIn(f"<script>{source}</script>", page)
        self.assertIsNone(re.search(r"\son[a-z]+=", page))
        self.assertIsNone(re.search(r"(?:href|src)=\"(?!#)", page))

    def test_hostile_text_renders_as_text(self):
        self.up({"type": "decision", "id": "DEC-001",
                 "title": '<img src=x onerror=alert(1)>"quoted"'})
        evil = dict(self.NARRATIVE, did="<script>alert(2)</script> & more",
                    headline="<b>bold</b>", next="<i>n</i>", plan="<u>p</u>",
                    colour_reason="<s>r</s>")
        page, _w = self.page(evil)
        for raw in ("<b>bold", "<i>n", "<u>p", "<s>r"):
            self.assertNotIn(raw, page)
        odd, _w = self.page(dict(self.NARRATIVE, colour=["red"]))   # never a crash
        self.assertIn("Proposed overall:", odd)
        self.assertNotIn("<img src=x", page)
        self.assertNotIn("<script>alert(2)", page)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;&quot;quoted&quot;", page)
        self.assertIn("&lt;script&gt;alert(2)&lt;/script&gt; &amp; more", page)


    def test_nothing_shrinks_and_long_lists_fold_after_eight(self):
        """Plan 251 v2 (U8): no word budget, no shrinking. A list shows 8 items, then a fold."""
        self.up(*[{"type": "defect", "id": f"DEF-{k:03d}", "title": f"Defect {k} renamed",
                   "severity": "medium"} for k in range(1, 151)])
        page, words = self.page(self.NARRATIVE)
        self.assertEqual(words, P.visible_words(page))
        self.assertNotIn("more in the record", page)
        self.assertIn("142 more</summary>", page)
        self.assertFalse(hasattr(P, "ENGINE_BUDGET"))

    def test_the_first_report_is_exempt_and_complete(self):
        self.up(*[{"type": "wbs-item", "id": f"WBS-{k:03d}", "title": f"Done task {k}",
                   "lifecycle_status": "Implemented"} for k in range(1, 121)])
        page, _w = self.page(self.NARRATIVE)
        for k in (1, 60, 120):
            self.assertIn(f"WBS-{k:03d}", page)
        self.assertNotIn("more in the record", page)
        self.assertIn("Where we stand", page)


    def test_one_glossary_names_only_the_terms_and_kinds_on_the_page(self):
        """Plan 251 v2 (request item 9): ONE glossary, the state words, the terms and the kinds
        of row the page shows."""
        self.up({"type": "wbs-item", "id": "WBS-001", "title": "Export",
                 "lifecycle_status": "Implemented"})
        page, _w = self.page(None)
        self.assertEqual(page.count('id="glossary"'), 1)
        self.assertNotIn('id="terms"', page)
        self.assertNotIn('id="families"', page)
        terms = re.findall(r"<dt>([^<]+)</dt>", page.split('id="glossary"')[1])
        self.assertIn("task (WBS-)", terms)
        self.assertIn("done earlier", terms)
        self.assertNotIn("waiver (WVR-)", terms)

    def test_times_show_in_the_rows_offset_and_the_words_never_show(self):
        self.seed()
        page, _w = self.page(self.NARRATIVE, row_extra={
            "lifecycle_status": "Approved", "recorded_by": "human:op",
            "recorded_at": "2026-11-16T06:10:00Z", "operator_words": "SECRET WORDS",
            "colour": "amber"})
        self.assertIn("Mon 16 Nov 2026, 09:05 (UTC+03:00)", page)
        self.assertIn("Recorded by human:op on Mon 16 Nov 2026, 09:10 (UTC+03:00)", page)
        self.assertNotIn("SECRET WORDS", page)
        self.assertNotIn("Draft: not recorded yet", page)


    def test_one_colour_statement_and_the_rule_beside_it(self):
        """Plan 251 v2 (U11): one statement; the default rule's colour only when it differs."""
        self.up({"type": "defect", "id": "DEF-001", "title": "x", "severity": "critical"})
        words = dict(self.NARRATIVE, colour="amber", colour_reason="Fix under way.")
        page, _w = self.page(words)
        self.assertIn("<strong>Proposed overall: At risk.</strong> Fix under way.", page)
        self.assertIn("By the default rule it would be off track", page)
        page, _w = self.page(dict(words, colour="red"))
        self.assertNotIn("By the default rule", page)

    def test_the_visible_counter_skips_closed_folds_but_reads_their_summary(self):
        page = ("<html><head><title>t t t</title><style>a b</style></head><body>"
                "<p>one two</p><details><summary>three</summary><p>hidden words</p>"
                "<details><summary>nested</summary></details></details>"
                "<details open><summary>four</summary><p>five</p></details></body></html>")
        self.assertEqual(P.visible_text(page).split(), ["one", "two", "three", "four", "five"])


SRC = {"source_kind": "clarification", "source_span": "test"}


class TreeTest(unittest.TestCase):
    """Plan 251 (R1-R12, D1-D10): the plan tree, the current slice in the agent's words, the
    cited titles and the families, through the tool as the field calls it."""

    WORDS = {"headline": "The export moves. Nothing blocks it.",
             "did": "We started the export of SL-002 and wrote the rows.",
             "challenges": "No defect is open.", "next": "We finish the export (SL-002).",
             "colour": "green", "slice_now": "SL-002", "slice_next": "SL-003",
             "slice": "The export slice writes tasks to a CSV file. The rows are written."}

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        srv.PACKAGE_ROOT = Path(self._tmp.name)
        srv.package_create("demo", "Demo", "rnd")
        self.conn = srv._CURRENT.conn
        task = lambda i, title, **kw: dict({"type": "wbs-item", "id": i, "title": title,
                                            "lifecycle_status": "Approved"}, **SRC, **kw)
        self.up({"type": "phase", "id": "PH-1", "title": "Groundwork", "sort_order": 1,
                 "lifecycle_status": "Approved", **SRC},
                {"type": "phase", "id": "PH-2", "title": "First release", "sort_order": 2,
                 "lifecycle_status": "Approved", **SRC},
                {"type": "phase", "id": "PH-3", "title": "Later", "sort_order": 3,
                 "lifecycle_status": "Approved", **SRC},
                {"type": "milestone", "id": "MS-1", "title": "Demo day", "phase_id": "PH-2",
                 "due": "2026-12-01"})
        self.up(*[{"type": "slice", "id": i, "title": t, "phase_id": ph, "sort_order": k,
                   "lifecycle_status": "Approved"} for i, t, ph, k in (
                      ("SL-001", "Setup", "PH-1", 1), ("SL-002", "Export", "PH-2", 1),
                      ("SL-003", "Import", "PH-2", 2), ("SL-004", "Reports", "PH-3", 1))])
        self.up({"type": "requirement", "id": "FR-001", "kind": "functional",
                 "title": "Export to CSV", "statement": "The user exports tasks.", **SRC},
                {"type": "acceptance-criterion", "id": "AC-001", "title": "The CSV opens",
                 "statement": "Given tasks, when exported, then the file opens.",
                 "requirement_id": "FR-001", "slice_id": "SL-002", "lifecycle_status":
                 "Approved"},
                task("WBS-1", "Export group", slice_id="SL-002", phase_id="PH-2"),
                task("WBS-1.1", "Write rows", parent_id="WBS-1", slice_id="SL-002",
                     phase_id="PH-2"),
                task("WBS-1.2", "Quote cells", parent_id="WBS-1", slice_id="SL-002",
                     phase_id="PH-2"),
                task("WBS-2", "Set up the repository", slice_id="SL-001", phase_id="PH-1"),
                task("WBS-3", "A chore with no slice", phase_id="PH-2"),
                task("WBS-4", "An old task outside the plan"))
        for table, i in (("wbs_items", "WBS-2"), ("slices", "SL-001"), ("phases", "PH-1")):
            self.conn.execute(f"UPDATE {table} SET lifecycle_status = 'Implemented'"
                              " WHERE id = ?", (i,))

    def tearDown(self):
        if srv._CURRENT is not None:
            srv.package_close()
        self._tmp.cleanup()

    def up(self, *rows):
        out = srv.entity_upsert(list(rows))
        self.assertTrue(out["ok"], [it for it in out["items"] if not it.get("ok")])

    def confirm(self, **kw):
        return dict({"operator_confirm": True, "by": "human:op", "words": "record it",
                     "colour": "green", "slice_now": "SL-002", "slice_next": "SL-003"}, **kw)

    def first(self):
        self.assertTrue(srv.standup_report(utc_offset="+03:00")["ok"])
        self.assertTrue(srv.standup_report(narrative=self.WORDS)["ok"])
        out = srv.standup_report(action="record", confirm=self.confirm())
        self.assertTrue(out["ok"], out)

    def facts(self) -> dict:
        return json.loads(self.conn.execute("SELECT facts FROM standup_reports WHERE"
                                            " lifecycle_status = 'Draft'").fetchone()[0])

    def page(self) -> str:
        return (srv.PACKAGE_ROOT / "demo" / "reports" / "draft.html").read_text(encoding="utf-8")

    def test_the_draft_suggests_the_slices_and_keeps_the_tree_out_of_the_result(self):
        out = srv.standup_report(utc_offset="+03:00")
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["plan_summary"]["suggest"], {"now": "SL-002", "next": "SL-003"})
        self.assertNotIn("plan", out["facts"])
        self.assertNotIn("names", out["facts"])
        self.assertLess(len(json.dumps(out)), 40_000)
        tree = self.facts()["plan"]
        self.assertEqual([p["id"] for p in tree["phases"]], ["PH-1", "PH-2", "PH-3"])
        ph2 = tree["phases"][1]
        self.assertEqual([s["id"] for s in ph2["slices"]], ["SL-002", "SL-003"])
        self.assertEqual([m["id"] for m in ph2["milestones"]], ["MS-1"])
        self.assertEqual([t["id"] for t in ph2["loose"]], ["WBS-3"])
        group = ph2["slices"][0]["tasks"][0]
        self.assertEqual([c["id"] for c in group["children"]], ["WBS-1.1", "WBS-1.2"])
        self.assertEqual([t["id"] for t in tree["outside"]["tasks"]], ["WBS-4"])
        self.assertFalse(tree["marks"])                     # a first report tags nothing


    def test_the_agent_states_the_slices_and_the_tool_checks_them(self):
        srv.standup_report(utc_offset="+03:00")
        words = {k: v for k, v in self.WORDS.items() if not k.startswith("slice")}
        for bad, needle in ((words, "slice_now names the current slice"),
                            (dict(self.WORDS, slice_now="SL-001"), "slice_now names"),
                            (dict(self.WORDS, slice_next="SL-002"), "slice_next names"),
                            (dict(self.WORDS, slice=""), "slice is empty"),
                            (dict(self.WORDS, _names={}), "narrative:")):
            out = srv.standup_report(narrative=bad)
            self.assertFalse(out["ok"], bad)
            self.assertIn(needle, out["error"])
        before = self.facts()
        self.assertTrue(srv.standup_report(narrative=self.WORDS)["ok"])
        self.assertEqual(self.facts(), before)              # the facts never change
        said = json.loads(self.conn.execute("SELECT narrative FROM standup_reports").fetchone()[0])
        self.assertEqual(said["_names"]["SL-002"], "Export")
        page = self.page()
        self.assertIn('<span class="state s-now">now</span>', page)
        did = page.split('id="did"')[1].split("</section>")[0]
        self.assertEqual(did.count("“Export”"), 1)          # the first mention only
        self.assertIn("What we are working on now", page)
        self.assertIn("The export slice writes tasks", page)

    def test_the_confirm_carries_the_slices_the_words_state(self):
        srv.standup_report(utc_offset="+03:00")
        srv.standup_report(narrative=self.WORDS)
        for bad in (self.confirm(slice_now=None), self.confirm(slice_next="SL-004")):
            bad = {k: v for k, v in bad.items() if v is not None}
            out = srv.standup_report(action="record", confirm=bad)
            self.assertFalse(out["ok"], bad)
            self.assertIn("Confirm the slices the page shows", out["error"])
        self.assertTrue(srv.standup_report(action="record", confirm=self.confirm())["ok"])


    def test_a_second_report_states_this_windows_work_and_opens_only_its_branches(self):
        self.first()
        self.up({"type": "wbs-item", "id": "WBS-1.1", "substitute": {"lifecycle_status":
                                                                        ["Approved", "Review"]}},
                {"type": "wbs-item", "id": "WBS-1.2", "substitute": {"lifecycle_status":
                                                                        ["Approved", "Review"]}})
        self.conn.execute("UPDATE wbs_items SET lifecycle_status = 'Implemented'"
                          " WHERE id = 'WBS-1.2'")
        out = srv.audit_record([{"ac_id": "AC-001", "verdict": "Met", "verified_by": "human",
                                 "verification_method": "manual",
                                 "evidence": "opened the file"}])
        self.assertTrue(out["ok"], out)
        srv.progress_update([{"entry": "Wrote the rows of the export.", "event_type":
                              "work-done", "subject_id": "WBS-1.1", "actor": "agent:t"}])
        self.assertTrue(srv.standup_report()["ok"])
        self.assertTrue(srv.standup_report(narrative=self.WORDS)["ok"])
        facts = self.facts()
        self.assertEqual(facts["touched"], ["WBS-1.1"])
        page = self.page()
        tree = page.split('id="tree"')[1].split("</section>")[0]
        state = {i: s for s, i in re.findall(r'data-state="([a-z-]+)" data-phase="[^"]*"'
                                             r' data-text="[^"]* ([a-z]+-[0-9.]+)"', tree)}
        self.assertEqual(state["wbs-1.1"], "claimed-window")
        self.assertEqual(state["wbs-1.2"], "done-window")
        self.assertEqual(state["ac-001"], "done-window")
        self.assertIn('data-phase="PH-2" open><summary>', tree)          # news opens it
        self.assertIn('data-phase="PH-1"><summary>', tree)               # no news: closed
        self.assertNotIn("Tasks claimed done", page)
        self.assertIn("Work done in this slice: 1 journal entry, 1 in this window", page)

    def test_every_row_carries_its_state_kind_and_phase_for_the_filters(self):
        """Plan 251 v2 (U2): the filters read data attributes; each item row has all three."""
        srv.standup_report(utc_offset="+03:00")
        page = self.page()
        tree = page.split('id="tree"')[1].split("</section>")[0]
        rows = re.findall(r'<(?:div|details) class="row[^"]*" data-row data-item ([^>]*)>', tree)
        self.assertTrue(rows)
        for attrs in rows:
            self.assertRegex(attrs, r'data-kind="(task|check|milestone)"')
            self.assertRegex(attrs, r'data-state="[a-z-]+"')
            self.assertIn("data-phase=", attrs)
        self.assertIn('id="tree-controls" hidden', page)          # the script shows them

    def test_a_report_without_a_tree_refuses_the_slice_keys(self):
        self.assertIsNone(srv._standup_slice_error({}, {"colour": "green"}))
        self.assertIn("no open slice", srv._standup_slice_error({}, {"slice_now": "SL-002"}))

    def test_a_row_of_6_7_0_prints_the_five_lists_and_6_7_0_draws_a_new_row(self):
        srv.standup_report(utc_offset="+03:00")
        srv.standup_report(narrative=self.WORDS)
        row = dict(zip(srv._STANDUP_ROW, self.conn.execute(
            f"SELECT {', '.join(srv._STANDUP_ROW)} FROM standup_reports").fetchone()))
        old = dict(row, facts=json.dumps({k: v for k, v in json.loads(row["facts"]).items()
                                          if k not in ("plan", "names")}))
        page, _w = srv._standup_page(old, draft=True)
        text = Path(page).read_text(encoding="utf-8")
        self.assertIn("Tasks done", text)
        self.assertNotIn('id="plan"', text)
        # The page code of v6.7.0, frozen byte for byte (blob afc4702, `git show
        # v6.7.0:plugins/tamheed/server/standup_page.py`): CI checks out no tags, so the test
        # reads a copy and never skips.
        source = (REPO_ROOT / "tests" / "standup_legacy" / "standup_page_670.py").read_text(
            encoding="utf-8")
        import types
        legacy = types.ModuleType("standup_page_670")
        legacy.__dict__["__file__"] = str(REPO_ROOT / "plugins" / "tamheed" / "server"
                                          / "standup_page.py")
        exec(compile(source, "standup_page_670", "exec"), legacy.__dict__)
        facts, said = json.loads(row["facts"]), json.loads(row["narrative"])
        meta = legacy.meta(row, package="Demo", base=None, birth=None,
                           window=facts["view"]["window"])
        html, _w = legacy.fit(meta, facts, said, exempt=True)   # the way back draws it
        self.assertIn("Tasks done", html)


    def test_every_family_has_plain_words_and_the_page_defines_only_its_own(self):
        import standup_families as FAM
        registry = {srv.ENTITY_TABLES[t]: prefix for t, _l, prefix, _c in
                    srv.BASELINE_ENTITY_TYPES}
        self.assertEqual({k: v[0] for k, v in FAM.FAMILIES.items()}, registry)
        srv.standup_report(utc_offset="+03:00")
        srv.standup_report(narrative=self.WORDS)
        terms = re.findall(r"<dt>([^<]+)</dt>", self.page().split('id="glossary"')[1])
        self.assertIn("slice (SL-)", terms)
        self.assertIn("acceptance check (AC-)", terms)
        self.assertNotIn("waiver (WVR-)", terms)

    def test_titles_are_cut_at_eight_words_and_escaped(self):
        cite = P.Cite({"SL-9": "one two three four five six seven eight nine",
                       "DEF-1": "<b>bold</b>"})
        self.assertEqual(P.short("one two three four five six seven eight nine"),
                         "one two three four five six seven eight …")
        html = cite.html("See [SL-9], SL-9 again and DEF-1; SL-10 names nothing.")
        self.assertIn("“one two three four five six seven eight …” <span class=\"ref\">SL-9"
                      "</span>, <span class=\"ref\">SL-9</span> again", html)
        self.assertIn("&lt;b&gt;bold&lt;/b&gt;", html)
        self.assertIn("SL-10 names nothing", html)


    def test_the_blocked_and_next_states_and_a_check_without_a_result(self):
        self.up({"type": "open-question", "id": "OQ-001", "title": "Which date format?",
                 "question": "Which date format does the export use?", **SRC},
                {"type": "trace-edge", "from_id": "WBS-1.2", "relation": "blocked_by",
                 "to_id": "OQ-001"})
        srv.standup_report(utc_offset="+03:00")
        srv.standup_report(narrative=self.WORDS)
        tree = self.page().split('id="tree"')[1].split("</section>")[0]
        self.assertRegex(tree, r'data-state="blocked"[^>]*wbs-1.2"')
        self.assertRegex(tree, r'data-state="not-checked"[^>]*ac-001"')
        self.assertIn("no result yet", tree)

    def test_a_report_after_a_broken_chain_tags_nothing(self):
        out = S.compute(self.conn, srv.ENTITY_TABLES.values(), None, "default")
        facts = F.build(self.conn, cls=out["cls"], live=out["live"], first=False,
                        window=dict(out, broken="RPT-001"), today="2026-11-16",
                        blocker_rules=[], screen=NEVER)
        self.assertFalse(facts["plan"]["marks"])

    def test_a_correction_keeps_the_tree_and_takes_the_slice_keys(self):
        self.first()
        out = srv.standup_report(supersede="RPT-001")
        self.assertTrue(out["ok"], out)
        self.assertNotIn("_names", out["corrects_narrative"])      # the agent can reuse it
        self.assertTrue(srv.standup_report(narrative=out["corrects_narrative"])["ok"])
        self.assertIn("plan", self.facts())
        self.assertTrue(srv.standup_report(action="record", confirm=self.confirm())["ok"])

    def test_journal_lines_cite_their_rows_but_the_slice_fold_does_not(self):
        srv.progress_update([{"entry": "Wrote the rows for SL-002 and FR-001.", "event_type":
                              "work-done", "subject_id": "WBS-1.1", "actor": "agent:t"}])
        srv.standup_report(utc_offset="+03:00")
        srv.standup_report(narrative=self.WORDS)
        page = self.page()
        journal = page.split("From the journal")[1].split("</ul>")[0]
        self.assertIn('“Export to CSV” <span class="ref">FR-001</span>', journal)
        fold = page.split("Work done in this slice")[1].split("</details>")[0]
        self.assertIn("Wrote the rows for SL-002 and FR-001.", fold)       # small ids only
        self.assertNotIn("“", fold)


    def test_tasks_follow_the_natural_id_order(self):
        self.up(*[{"type": "wbs-item", "id": f"WBS-1.{k}", "title": f"step {k}",
                   "parent_id": "WBS-1", "slice_id": "SL-002", "phase_id": "PH-2",
                   "lifecycle_status": "Approved", **SRC} for k in (10, 3)])
        srv.standup_report(utc_offset="+03:00")
        kids = [c["id"] for c in self.facts()["plan"]["phases"][1]["slices"][0]["tasks"][0]
                ["children"]]
        self.assertEqual(kids, ["WBS-1.1", "WBS-1.2", "WBS-1.3", "WBS-1.10"])


    def test_the_kinds_come_from_the_rows_never_from_the_page_text(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "Hash files with SHA-256 at"
                 " UTC-05:00", "lifecycle_status": "Proposed", **SRC})
        srv.standup_report(utc_offset="-05:00")
        srv.standup_report(narrative=self.WORDS)
        terms = " ".join(re.findall(r"<dt>([^<]+)</dt>", self.page().split('id="glossary"')[1]))
        self.assertNotIn("SHA-", terms)
        self.assertNotIn("UTC-", terms)

    def test_the_draft_result_stays_small_on_a_large_package(self):
        self.up(*[{"type": "wbs-item", "id": f"WBS-7.{k}", "title": f"A long task title"
                   f" number {k} of the large import plan", "slice_id": "SL-003",
                   "phase_id": "PH-2", "lifecycle_status": "Proposed", **SRC}
                  for k in range(1, 401)])
        out = srv.standup_report(utc_offset="+03:00")
        self.assertTrue(out["ok"], out)
        self.assertLess(len(json.dumps(out)), 40_000)
        self.assertGreater(len(self.conn.execute("SELECT facts FROM standup_reports")
                               .fetchone()[0]), 40_000)               # the row keeps all


    def test_the_page_follows_the_os_and_the_switch_works_without_the_script(self):
        """The OS colours by default; the switch is CSS (it works with the script off); the
        script only remembers the choice, and a stored value outside the three is ignored."""
        srv.standup_report(utc_offset="+03:00")
        page = self.page()
        self.assertIn('<input type="radio" name="theme" id="theme-auto" checked>', page)
        css = P.CSS_PATH.read_text(encoding="utf-8")
        self.assertIn("@media (prefers-color-scheme: dark)", css)
        self.assertLess(css.index("@media (prefers-color-scheme: dark)"),
                        css.index(":root:has(#theme-dark:checked)"))
        self.assertIn(".theme, #tree-controls { display: none !important; }", css)
        js = (REPO_ROOT / "plugins/tamheed/server/standup.js").read_text(encoding="utf-8")
        self.assertIn("const CHOICES = ['auto', 'light', 'dark'];", js)
        self.assertIn("if (CHOICES.includes(stored))", js)
        self.assertNotIn("innerHTML", js)
        self.assertNotIn("fetch(", js)

    def test_an_id_inside_a_rows_own_title_shows_its_name_on_hover(self):
        self.up({"type": "decision", "id": "DEC-001", "title": "Ship SL-003 after AC-001",
                 "lifecycle_status": "Proposed", **SRC})
        srv.standup_report(utc_offset="+03:00")
        page = self.page()
        self.assertIn('Ship <abbr title="Import">SL-003</abbr> after <abbr title="The CSV'
                      ' opens">AC-001</abbr>', page)


    def test_no_budget_no_page_warning_and_the_description_fits(self):
        self.assertFalse(hasattr(P, "ENGINE_BUDGET"))
        self.assertFalse(hasattr(srv, "_STANDUP_PAGE_WARN"))
        self.assertLessEqual(len(srv._STANDUP_DESC), srv._DESCRIPTION_CAP)
    def test_one_state_per_row_in_the_approved_order(self):
        """Plan 251 v2 (U10, V1, V3): the state table."""
        ctx = {"slice": "SL-1", "now": "SL-1", "next": "SL-2", "touched": {"T-9"},
               "first": False}
        rs = lambda item, kind="task", **kw: F.row_state(item, kind, dict(ctx, **kw))  # noqa
        self.assertEqual(rs({"id": "T-1", "status": "Implemented", "tag": "done"}),
                         "done-window")
        self.assertEqual(rs({"id": "T-1", "status": "Review", "tag": "claimed"}),
                         "claimed-window")
        self.assertEqual(rs({"id": "T-1", "status": "Implemented"}), "done-earlier")
        self.assertEqual(rs({"id": "T-1", "status": "Approved", "tag": "blocked"}), "blocked")
        self.assertEqual(rs({"id": "T-1", "status": "Review"}), "in-progress")
        self.assertEqual(rs({"id": "T-9", "status": "Approved"}, slice="SL-7"), "in-progress")
        self.assertEqual(rs({"id": "T-1", "status": "Proposed"}), "next")
        self.assertEqual(rs({"id": "T-1", "status": "Proposed"}, first=True), "in-progress")
        self.assertEqual(rs({"id": "T-1", "status": "Proposed"}, slice="SL-2"), "next")
        self.assertEqual(rs({"id": "T-1", "status": "Proposed"}, slice="SL-5"), "not-started")
        self.assertEqual(rs({"id": "T-1", "status": "Deferred"}), "postponed")
        self.assertEqual(rs({"id": "A-1", "tag": "done", "result": "Met"}, "check"),
                         "done-window")
        self.assertEqual(rs({"id": "A-1", "result": "Met"}, "check"), "done-earlier")
        self.assertEqual(rs({"id": "A-1", "result": "Partial"}, "check"), "failed")
        self.assertEqual(rs({"id": "A-1", "result": "Pending"}, "check"), "not-checked")
        # D-T1: with no next slice, a task with no slice is never "next"
        self.assertEqual(rs({"id": "T-1", "status": "Proposed"}, slice=None, next=None),
                         "not-started")

    def test_every_view_agrees_on_the_counts(self):
        """The cards, the chips and the rows read one state function."""
        self.first()
        self.up({"type": "wbs-item", "id": "WBS-1.2", "substitute": {"lifecycle_status":
                                                                        ["Approved", "Review"]}})
        srv.standup_report()
        srv.standup_report(narrative=self.WORDS)
        page = self.page()
        tree = page.split('id="tree"')[1].split("</section>")[0]
        rows = re.findall(r'data-item data-kind="(task|check)" data-state="([a-z-]+)"', tree)
        chips = dict(re.findall(r'data-value="([a-z-]+)" aria-pressed="false">[^<]*'
                                r'<span class="n">(\d+)</span>', page))
        for state, n in chips.items():
            self.assertEqual(sum(1 for _k, s in rows if s == state), int(n), state)
        card = re.search(r'Done this window</div><div class="value">(\d+)<', page).group(1)
        self.assertEqual(int(card), sum(1 for _k, s in rows if s == "done-window"))

    def test_the_sections_come_in_order_and_record_details_are_folded(self):
        srv.standup_report(utc_offset="+03:00")
        srv.standup_report(narrative=self.WORDS)
        page = self.page()
        order = re.findall(r'<section class="card" id="([a-z]+)"', page)
        self.assertEqual(order, ["summary", "needs", "plan", "did", "now", "next", "challenges",
                                 "glossary", "record"])
        self.assertIn('id="record"><details class="fold">', page)

    def test_a_first_report_shows_the_overall_picture_only(self):
        srv.standup_report(utc_offset="+03:00")
        srv.standup_report(narrative=self.WORDS)
        page = self.page()
        self.assertIn("This is the first report", page)
        self.assertNotIn("Done this window</div>", page)
        self.assertNotIn("<h3>In this window</h3>", page)
        self.assertNotIn('data-value="done-window"', page)
        self.assertEqual(self.facts()["touched"], [])

    def test_the_draft_result_leaves_the_tree_and_the_registers_in_the_row(self):
        out = srv.standup_report(utc_offset="+03:00")
        for key in ("plan", "names", "kinds", "touched", "overall"):
            self.assertNotIn(key, out["facts"])
        self.assertIn("overall", self.facts())


if __name__ == "__main__":
    unittest.main(argv=[a for a in sys.argv if a != "--regen"], verbosity=2)
