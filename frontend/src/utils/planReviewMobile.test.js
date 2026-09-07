import { describe, expect, it } from "vitest";
import {
  decisionActionButtonClassName,
  decisionActionsRowClassName,
  decisionGateShellClassName,
  planReviewPagePaddingClassName,
} from "./planReviewMobile.js";

describe("US-MOB-003 planReviewMobile helpers", () => {
  it("stacks decision actions for thumb reach", () => {
    const row = decisionActionsRowClassName();
    expect(row).toContain("flex-col");
    expect(row).toContain("sm:flex-row");
    expect(row).toContain("w-full");
  });

  it("makes decision buttons full-width and taller on mobile", () => {
    const cls = decisionActionButtonClassName("btn-primary");
    expect(cls).toContain("btn-primary");
    expect(cls).toContain("w-full");
    expect(cls).toContain("min-h-11");
  });

  it("uses sticky dock below md and static card from md up", () => {
    const shell = decisionGateShellClassName();
    expect(shell).toContain("fixed");
    expect(shell).toContain("bottom-0");
    expect(shell).toContain("md:static");
    expect(shell).toContain("border-yellow-200");
  });

  it("adds mobile bottom padding when gate is visible", () => {
    expect(planReviewPagePaddingClassName(true)).toContain("pb-48");
    expect(planReviewPagePaddingClassName(true)).toContain("md:pb-8");
    expect(planReviewPagePaddingClassName(false)).not.toContain("pb-48");
  });
});
