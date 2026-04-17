import { describe, expect, it } from "vitest";
import {
  mergeRecentPatientList,
  RECENT_PATIENTS_MAX,
} from "./recentPatients";

describe("mergeRecentPatientList", () => {
  it("prepends new entry and caps length", () => {
    const base = Array.from({ length: RECENT_PATIENTS_MAX }, (_, i) => ({
      id: `00000000-0000-4000-8000-${String(i).padStart(12, "0")}`,
      label: `p${i}`,
      savedAt: "2020-01-01T00:00:00.000Z",
    }));
    const next = mergeRecentPatientList(base, {
      id: "11111111-1111-4111-8111-111111111111",
      label: "new",
    });
    expect(next).toHaveLength(RECENT_PATIENTS_MAX);
    expect(next[0].id).toBe("11111111-1111-4111-8111-111111111111");
    expect(next[0].label).toBe("new");
  });

  it("moves existing id to front instead of duplicating", () => {
    const list = [
      { id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", label: "a", savedAt: "t1" },
      { id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb", label: "b", savedAt: "t2" },
    ];
    const next = mergeRecentPatientList(list, {
      id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
      label: "b updated",
    });
    expect(next).toHaveLength(2);
    expect(next[0].id).toBe("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb");
    expect(next[0].label).toBe("b updated");
  });

  it("ignores invalid uuid", () => {
    const list = [{ id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", label: "a", savedAt: "t" }];
    expect(mergeRecentPatientList(list, { id: "not-uuid" })).toEqual(list);
  });
});
