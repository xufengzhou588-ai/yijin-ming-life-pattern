window.MINGAnalytics = {
  record(name, metadata, storageKey) {
    try {
      const events = window.MINGStorage.readJSON(storageKey, []);
      const next = [
        ...events.slice(-49),
        {
          name,
          metadata: Object.fromEntries(Object.entries(metadata).filter(([, value]) => value !== undefined)),
          created_at: new Date().toISOString()
        }
      ];
      window.MINGStorage.writeJSON(storageKey, next);
    } catch {
      // Analytics is best effort and must never block the reading flow.
    }
  }
};
