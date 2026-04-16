import assert from "node:assert/strict";
import test from "node:test";

import {
  formatModerationLabel,
  getProfileStatusMeta,
  getReportEmptyState,
  getReportStatusMeta,
  getVerificationStatusMeta,
  isHiddenProfile,
} from "../src/lib/admin-moderation-display";

test("formats moderation labels from stored enum values", () => {
  assert.equal(formatModerationLabel("under_review"), "Under Review");
  assert.equal(formatModerationLabel("fake_profile"), "Fake Profile");
});

test("uses distinct report status badge metadata", () => {
  assert.equal(getReportStatusMeta("open").label, "Open");
  assert.match(getReportStatusMeta("open").badgeClass, /amber/);
  assert.equal(getReportStatusMeta("resolved").label, "Resolved");
  assert.match(getReportStatusMeta("resolved").badgeClass, /green/);
});

test("marks hidden profiles clearly for admin views", () => {
  const meta = getProfileStatusMeta("hidden");

  assert.equal(meta.label, "Hidden");
  assert.match(meta.badgeClass, /stone-900/);
  assert.match(meta.helper, /browse/i);
  assert.equal(isHiddenProfile("hidden"), true);
  assert.equal(isHiddenProfile("published"), false);
});

test("uses clear verification decision badge metadata", () => {
  assert.equal(getVerificationStatusMeta("approved").label, "Approved");
  assert.match(getVerificationStatusMeta("approved").badgeClass, /green/);
  assert.equal(getVerificationStatusMeta("rejected").label, "Rejected");
  assert.match(getVerificationStatusMeta("rejected").badgeClass, /red/);
});

test("returns filter-specific report empty state copy", () => {
  assert.deepEqual(getReportEmptyState("open"), {
    title: "No open reports",
    description: "New reports that still need moderator attention will appear here.",
  });
  assert.deepEqual(getReportEmptyState("all"), {
    title: "No reports found",
    description: "Reports will appear here as members submit them.",
  });
});
