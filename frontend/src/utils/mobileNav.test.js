import { describe, expect, it } from "vitest";
import {
  MOBILE_NAV_BREAKPOINT_PX,
  isMobileNavViewport,
  nextMobileNavOpen,
} from "./mobileNav";

describe("mobileNav (US-MOB-001)", () => {
  it("treats viewports under the md breakpoint as mobile nav", () => {
    expect(MOBILE_NAV_BREAKPOINT_PX).toBe(768);
    expect(isMobileNavViewport(360)).toBe(true);
    expect(isMobileNavViewport(767)).toBe(true);
    expect(isMobileNavViewport(768)).toBe(false);
    expect(isMobileNavViewport(1024)).toBe(false);
  });

  it("toggles drawer open state and forces closed when leaving mobile", () => {
    expect(nextMobileNavOpen({ currentlyOpen: false, toggle: true })).toBe(true);
    expect(nextMobileNavOpen({ currentlyOpen: true, toggle: true })).toBe(false);
    expect(nextMobileNavOpen({ currentlyOpen: true, forceClosed: true })).toBe(false);
  });
});
