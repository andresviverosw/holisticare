import { useEffect, useState } from "react";
import {
  COLD_START_HINT_MS,
  COLD_START_HINT_TEXT,
  shouldShowColdStartHint,
} from "./coldStartFeedback";

/**
 * US-UX-COLDSTART-001 — delayed Spanish hint while an auth request is in flight.
 * @param {boolean} busy
 * @returns {{ showColdStartHint: boolean, coldStartHintText: string }}
 */
export function useColdStartHint(busy) {
  const [elapsedMs, setElapsedMs] = useState(0);

  useEffect(() => {
    if (!busy) {
      setElapsedMs(0);
      return undefined;
    }
    const started = Date.now();
    setElapsedMs(0);
    const id = window.setInterval(() => {
      setElapsedMs(Date.now() - started);
    }, 250);
    return () => window.clearInterval(id);
  }, [busy]);

  return {
    showColdStartHint: busy && shouldShowColdStartHint(elapsedMs, COLD_START_HINT_MS),
    coldStartHintText: COLD_START_HINT_TEXT,
  };
}
