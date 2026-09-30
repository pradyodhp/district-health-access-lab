import { defineConfig } from '@playwright/test';

// Primary-journey E2E against the real FastAPI app serving the production build.
// Requires: ../web/dist build (npm run build) and the backend deps installed.
export default defineConfig({
  testDir: '.',
  timeout: 60000,
  retries: 0,
  use: { baseURL: 'http://127.0.0.1:8000', headless: true },
  webServer: {
    command: 'cd .. && python3 -m uvicorn health_access.api:app --app-dir src --host 127.0.0.1 --port 8000',
    url: 'http://127.0.0.1:8000/health',
    reuseExistingServer: false,
    timeout: 30000,
  },
});
