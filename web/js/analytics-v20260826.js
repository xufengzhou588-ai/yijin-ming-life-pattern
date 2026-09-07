(() => {
  const eventSchemaVersion = "analytics-events-v2";
  const installIdStorageKey = "ming.analytics.installId.v1";
  const sequenceStorageKey = "ming.analytics.sequence.v1";
  const disabledStorageKey = "ming.analytics.disabled.v1";
  const sentMarkerStorageKey = "ming.analytics.sentMarkers.v1";
  const sessionIdStorageKey = "ming.analytics.sessionId.v1";
  const uploadEndpoint = "/api/analytics/events";
  const maxQueuedEvents = 200;
  const maxFlushBatchSize = 25;
  const allowedEvents = new Set([
    "first_open",
    "onboarding_started",
    "onboarding_completed",
    "free_entitlement",
    "reading_generated",
    "today_viewed",
    "seal_selected",
    "muyu_started",
    "muyu_completed",
    "quest_action_completed",
    "weekly_review_viewed",
    "oracle_started",
    "oracle_saved",
    "paywall_view",
    "paywall_viewed",
    "purchase_start",
    "purchase_started",
    "purchase_success",
    "purchase_completed",
    "purchase_failure",
    "purchase_cancel",
    "restore",
    "subscription_restored",
    "pro_gate_denied",
    "experiment_exposure"
  ]);
  const allowedMetadataKeys = new Set([
    "action_key",
    "app_build",
    "cancel_reason",
    "duration_seconds",
    "entitlement_status",
    "entitlement_tier",
    "error_code",
    "experiment_key",
    "failure_stage",
    "language",
    "module",
    "plan_id",
    "placement",
    "product_id",
    "quest_id",
    "reason",
    "review_period",
    "seal_key",
    "source",
    "status",
    "storekit_environment",
    "surface",
    "time_accuracy",
    "true_solar_time",
    "variant",
    "week_index"
  ]);
  const forbiddenMetadataKeys = new Set([
    "birth_date",
    "birth_datetime",
    "birth_time",
    "body",
    "city",
    "content",
    "country",
    "display_name",
    "journal",
    "latitude",
    "longitude",
    "name",
    "payload",
    "question",
    "region",
    "report",
    "result",
    "text",
    "timezone"
  ]);
  const throttledEvents = new Map([
    ["paywall_view", 30],
    ["pro_gate_denied", 30],
    ["experiment_exposure", 300],
    ["restore", 30]
  ]);
  const lastRecordedAtByKey = new Map();
  let flushTimer = null;
  let flushInFlight = false;

  function safeMetadataValue(value) {
    if (value === undefined || value === null) return undefined;
    if (typeof value === "boolean") return value;
    if (typeof value === "number") return Number.isFinite(value) ? value : undefined;
    if (typeof value === "string") {
      const trimmed = value.trim();
      if (/@/.test(trimmed)) return undefined;
      if (/\b\d{4}-\d{2}-\d{2}\b/.test(trimmed)) return undefined;
      return trimmed.slice(0, 96);
    }
    return undefined;
  }

  function sanitizeMetadata(metadata = {}) {
    return Object.fromEntries(
      Object.entries(metadata)
        .filter(([key]) => allowedMetadataKeys.has(key) && !forbiddenMetadataKeys.has(key))
        .map(([key, value]) => [key, safeMetadataValue(value)])
        .filter(([, value]) => value !== undefined && value !== "")
    );
  }

  function uuid() {
    if (window.crypto?.randomUUID) return window.crypto.randomUUID();
    const bytes = new Uint8Array(16);
    if (window.crypto?.getRandomValues) {
      window.crypto.getRandomValues(bytes);
    } else {
      for (let index = 0; index < bytes.length; index += 1) bytes[index] = Math.floor(Math.random() * 256);
    }
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;
    const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
    return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
  }

  function getOrCreateStoredID(storage, key) {
    try {
      const existing = storage.getItem(key);
      if (/^[0-9a-f-]{36}$/i.test(existing || "")) return existing;
      const next = uuid();
      storage.setItem(key, next);
      return next;
    } catch {
      return uuid();
    }
  }

  function anonymousInstallID() {
    return getOrCreateStoredID(window.localStorage, installIdStorageKey);
  }

  function anonymousSessionID() {
    return getOrCreateStoredID(window.sessionStorage, sessionIdStorageKey);
  }

  function nextSequence() {
    try {
      const next = Number.parseInt(localStorage.getItem(sequenceStorageKey) || "0", 10) + 1;
      localStorage.setItem(sequenceStorageKey, String(next));
      return next;
    } catch {
      return 0;
    }
  }

  function stableHash(value) {
    let hash = 2166136261;
    for (let index = 0; index < value.length; index += 1) {
      hash ^= value.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return hash >>> 0;
  }

  function releaseChannel() {
    const params = new URLSearchParams(window.location.search);
    const channel = params.get("release_channel") || params.get("channel");
    if (channel === "testflight" || params.get("testflight") === "1") return "testflight";
    if (channel === "app_store") return "app_store";
    if (window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost") return "local";
    return "web";
  }

  function regionScope(channel = releaseChannel()) {
    if (channel !== "testflight") return "not_testflight";
    const locale = navigator.language || "";
    let timezone = "";
    try {
      timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
    } catch {
      timezone = "";
    }
    const hasUSLocaleHint = /^en-US\b/i.test(locale);
    const hasUSTimezoneHint = /^America\//.test(timezone) || timezone === "Pacific/Honolulu";
    return hasUSLocaleHint || hasUSTimezoneHint ? "us_testflight" : "non_us_testflight";
  }

  function experimentAssignment(experimentKey = "us_testflight_paywall_copy") {
    const installID = anonymousInstallID();
    const bucket = stableHash(`${installID}:${experimentKey}`) % 100;
    return {
      key: experimentKey,
      variant: bucket < 50 ? "control" : "value_stack",
      bucket
    };
  }

  function isDisabled() {
    try {
      if (window.MING_ANALYTICS_DISABLED === true) return true;
      if (localStorage.getItem(disabledStorageKey) === "1") return true;
    } catch {
      return true;
    }
    return navigator.doNotTrack === "1" || window.doNotTrack === "1";
  }

  function sentMarkers() {
    return window.MINGStorage.readJSON(sentMarkerStorageKey, {});
  }

  function markOncePerInstall(eventKey) {
    try {
      const markers = sentMarkers();
      if (markers[eventKey]) return false;
      markers[eventKey] = new Date().toISOString();
      window.MINGStorage.writeJSON(sentMarkerStorageKey, markers);
      return true;
    } catch {
      return false;
    }
  }

  function shouldThrottle(name, metadata, options) {
    const seconds = options.throttleSeconds ?? throttledEvents.get(name) ?? 0;
    if (!seconds) return false;
    const key = `${name}:${JSON.stringify(metadata)}`;
    const now = Date.now();
    const previous = lastRecordedAtByKey.get(key) || 0;
    if (now - previous < seconds * 1000) return true;
    lastRecordedAtByKey.set(key, now);
    return false;
  }

  function buildEvent(name, metadata) {
    const channel = releaseChannel();
    const experiment = experimentAssignment();
    return {
      event_id: uuid(),
      schema_version: eventSchemaVersion,
      name,
      created_at: new Date().toISOString(),
      anonymous_install_id: anonymousInstallID(),
      anonymous_session_id: anonymousSessionID(),
      sequence: nextSequence(),
      release_channel: channel,
      region_scope: regionScope(channel),
      experiment,
      metadata
    };
  }

  function enqueue(storageKey, event) {
    const events = window.MINGStorage.readJSON(storageKey, []);
    const next = [...events, event].slice(-maxQueuedEvents);
    window.MINGStorage.writeJSON(storageKey, next);
  }

  function scheduleFlush(storageKey) {
    if (flushTimer || flushInFlight || window.location.protocol === "file:") return;
    flushTimer = window.setTimeout(() => {
      flushTimer = null;
      flush(storageKey);
    }, 50);
  }

  async function flush(storageKey) {
    if (flushInFlight || isDisabled()) return false;
    const events = window.MINGStorage.readJSON(storageKey, []);
    const batch = events.slice(0, maxFlushBatchSize);
    if (!batch.length) return true;
    flushInFlight = true;
    try {
      const response = await fetch(uploadEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ schema_version: eventSchemaVersion, events: batch }),
        credentials: "same-origin",
        keepalive: true
      });
      if (!response.ok) return false;
      const payload = await response.json().catch(() => ({ ok: true }));
      if (!payload.ok) return false;
      const sentIDs = new Set(batch.map((event) => event.event_id));
      const current = window.MINGStorage.readJSON(storageKey, []);
      window.MINGStorage.writeJSON(storageKey, current.filter((event) => !sentIDs.has(event.event_id)));
      return true;
    } catch {
      return false;
    } finally {
      flushInFlight = false;
    }
  }

  window.MINGAnalytics = {
    contract: {
      version: eventSchemaVersion,
      allowedEvents: Array.from(allowedEvents),
      allowedMetadataKeys: Array.from(allowedMetadataKeys),
      forbiddenMetadataKeys: Array.from(forbiddenMetadataKeys)
    },
    experiment: experimentAssignment,
    isDisabled,
    flush,
    record(name, metadata = {}, storageKey, options = {}) {
      if (!allowedEvents.has(name)) return false;
      if (isDisabled()) return false;
      const sanitizedMetadata = sanitizeMetadata(metadata);
      const eventKey = `${name}:${JSON.stringify(sanitizedMetadata)}`;
      if (options.oncePerInstall && !markOncePerInstall(eventKey)) return false;
      if (shouldThrottle(name, sanitizedMetadata, options)) return false;
      try {
        enqueue(storageKey, buildEvent(name, sanitizedMetadata));
        scheduleFlush(storageKey);
        return true;
      } catch {
        // Analytics is best effort and must never block the reading flow.
        return false;
      }
    }
  };
})();
