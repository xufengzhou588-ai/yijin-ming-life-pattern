(() => {
  const eventSchemaVersion = "analytics-events-v1";
  const allowedEvents = new Set([
    "onboarding_started",
    "onboarding_completed",
    "reading_generated",
    "today_viewed",
    "seal_selected",
    "muyu_started",
    "muyu_completed",
    "quest_action_completed",
    "weekly_review_viewed",
    "oracle_started",
    "oracle_saved",
    "paywall_viewed",
    "purchase_started",
    "purchase_completed",
    "subscription_restored"
  ]);
  const allowedMetadataKeys = new Set([
    "action_key",
    "duration_seconds",
    "entitlement_status",
    "language",
    "module",
    "plan_id",
    "product_id",
    "quest_id",
    "review_period",
    "seal_key",
    "source",
    "status",
    "surface",
    "time_accuracy",
    "true_solar_time",
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

  function safeMetadataValue(value) {
    if (value === undefined || value === null) return undefined;
    if (typeof value === "boolean") return value;
    if (typeof value === "number") return Number.isFinite(value) ? value : undefined;
    if (typeof value === "string") return value.trim().slice(0, 96);
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

  window.MINGAnalytics = {
    contract: {
      version: eventSchemaVersion,
      allowedEvents: Array.from(allowedEvents),
      allowedMetadataKeys: Array.from(allowedMetadataKeys),
      forbiddenMetadataKeys: Array.from(forbiddenMetadataKeys)
    },
    record(name, metadata, storageKey) {
      if (!allowedEvents.has(name)) return false;
      try {
        const events = window.MINGStorage.readJSON(storageKey, []);
        const next = [
          ...events.slice(-49),
          {
            name,
            schema_version: eventSchemaVersion,
            metadata: sanitizeMetadata(metadata),
            created_at: new Date().toISOString()
          }
        ];
        window.MINGStorage.writeJSON(storageKey, next);
        return true;
      } catch {
        // Analytics is best effort and must never block the reading flow.
        return false;
      }
    }
  };
})();
