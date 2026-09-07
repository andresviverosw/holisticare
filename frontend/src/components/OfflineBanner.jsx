import { useEffect, useState } from "react";
import {
  OFFLINE_UNAVAILABLE_MESSAGE,
  shouldShowOfflineBanner,
} from "../utils/pwaConfig";

/** US-MOB-002 — deterministic offline/unavailable messaging (no blank shell). */
export default function OfflineBanner() {
  const [offline, setOffline] = useState(() =>
    shouldShowOfflineBanner({
      onLine: typeof navigator !== "undefined" ? navigator.onLine : true,
    }),
  );

  useEffect(() => {
    function sync() {
      setOffline(shouldShowOfflineBanner({ onLine: navigator.onLine }));
    }
    window.addEventListener("online", sync);
    window.addEventListener("offline", sync);
    return () => {
      window.removeEventListener("online", sync);
      window.removeEventListener("offline", sync);
    };
  }, []);

  if (!offline) return null;

  return (
    <div
      role="status"
      data-testid="offline-banner"
      className="border-b border-amber-300 bg-amber-50 px-4 py-2 text-sm text-amber-950"
    >
      {OFFLINE_UNAVAILABLE_MESSAGE}
    </div>
  );
}
