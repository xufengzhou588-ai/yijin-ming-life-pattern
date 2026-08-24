window.MINGStorage = {
  readJSON(key, fallback) {
    try {
      const value = localStorage.getItem(key);
      return value ? JSON.parse(value) : fallback;
    } catch {
      return fallback;
    }
  },
  writeJSON(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }
};
