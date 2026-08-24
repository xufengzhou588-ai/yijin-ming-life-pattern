window.MINGApi = {
  async fetchJson(url, options = {}, retries = 1) {
    let lastError;
    for (let attempt = 0; attempt <= retries; attempt += 1) {
      try {
        const response = await fetch(url, options);
        const payload = await response.json();
        return { response, payload };
      } catch (error) {
        lastError = error;
        if (attempt < retries) {
          await new Promise((resolve) => window.setTimeout(resolve, 500));
        }
      }
    }
    throw lastError;
  }
};
