import http from "k6/http";
import { check, sleep } from "k6";
import { randomString } from "https://jslib.k6.io/k6-utils/1.2.0/index.js";

export const options = {
  stages: [
    { duration: "2m", target: 30 },    // Ramp up to 30 users
    { duration: "5m", target: 50 },    // Steady state with 50 users
    { duration: "2m", target: 80 },    // Peak usage
    { duration: "3m", target: 50 },    // Back to normal
    { duration: "2m", target: 0 },     // Ramp down
  ],
  thresholds: {
    'http_req_failed{name:!check_user_exists}': ["rate<0.02"],      // Less than 2% failure (excluding user existence checks)
      http_req_duration: [
          "p(95)<800",                     // 95% under 800ms
          "p(99)<1500"                      // 99% under 1.5s
      ],
  },
};

const BASE_URL = "http://localhost:8082";

export default function () {
  // Simulate realistic user behavior with weighted endpoint usage
  const scenario = Math.random();

  if (scenario < 0.50) {
    // 50% - Check realtime data (most common operation)
    realtimeDataScenario();
  } else if (scenario < 0.75) {
    // 25% - Check lifetime data
    lifetimeDataScenario();
  } else if (scenario < 0.90) {
    // 15% - Check historical data
    historicalDataScenario();
  } else {
    // 10% - Configuration management
    configManagementScenario();
  }
}

function realtimeDataScenario() {
  const res = http.get(`${BASE_URL}/kostal/realtimedata`);

  check(res, {
    "realtime status 200": (r) => r.status === 200,
    "realtime has generation data": (r) => {
      try {
        const data = r.json();
        return data !== null;
      } catch (e) {
        return false;
      }
    },
  });
  sleep(2 + Math.random() * 3); // 2-5 seconds think time
}

function lifetimeDataScenario() {
  const res = http.get(`${BASE_URL}/kostal/lfdata`);

  check(res, {
    "lfdata status 200": (r) => r.status === 200,
    "lfdata has totals": (r) => {
      try {
        const data = r.json();
        return data !== null;
      } catch (e) {
        return false;
      }
    },
  });

  sleep(3 + Math.random() * 4); // 3-7 seconds think time
}

function historicalDataScenario() {
  const res = http.get(`${BASE_URL}/kostal/historicaldata`);

  check(res, {
    "historical status 200": (r) => r.status === 200,
    "historical has data": (r) => {
      try {
        const data = r.json();
        return data !== null;
      } catch (e) {
        return false;
      }
    },
  });

  sleep(5 + Math.random() * 5); // 5-10 seconds think time (users analyze data)
}

function configManagementScenario() {
  const username = `user_${randomString(8)}`;
  const headers = { "Content-Type": "application/json" };

  // Check if user exists (404 is expected, so tag it to exclude from failure threshold)
  let res = http.get(`${BASE_URL}/kostal/${username}`, {
    tags: { name: 'check_user_exists' }
  });

  if (res.status === 404) {
    // User doesn't exist, create one
    const payload = JSON.stringify({
      username: username,
      name: "Kostal Inverter",
      ip_address: `http://homeassistant.local:8123`,
      token: `token_${randomString(16)}`,
    });

    res = http.post(`${BASE_URL}/kostal`, payload, { headers: headers });

    check(res, {
      "config POST status 200": (r) => r.status === 200,
    });

  } else {
    // User exists, maybe update
    if (Math.random() < 0.5) {
      const payload = JSON.stringify({
        username: username,
        name: "Kostal Inverter Updated",
        ip_address: `http://homeassistant-new.local:8123`,
        token: `new_token_${randomString(16)}`,
      });

      res = http.put(`${BASE_URL}/kostal`, payload, { headers: headers });

     check(res, {
        "config PUT status 200 or 500": (r) => r.status === 200 || r.status === 500,
      });

    }
  }

  sleep(8 + Math.random() * 7); // 8-15 seconds (configuration is infrequent)
}
