import http from "k6/http";
import { check, sleep } from "k6";
import { Rate } from "k6/metrics";

// Establishes baseline performance

export const options = {
  stages: [
    { duration: "1m", target: 20 },   // Ramp up to 20 users over 1 minute
    { duration: "5m", target: 20 },   // Stay at 20 users for 5 minutes
    { duration: "1m", target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
      http_req_failed: ["rate<0.01"],      // Less than 1% of requests should fail
      http_req_duration: [
          "p(95)<500",                      // 95% of requests should be below 500ms
          "p(99)<1000",                     // 99% of requests should be below 1s
    ],
  },
};

const BASE_URL = "http://localhost:8082";

export default function () {
  // Test realtime data endpoint
  let res = http.get(`${BASE_URL}/kostal/realtimedata`);
  check(res, {
    "realtime status 200": (r) => r.status === 200,
    "realtime has data": (r) => r.json() !== null,
  });
  sleep(1);

  // Test lifetime data endpoint
  res = http.get(`${BASE_URL}/kostal/lfdata`);
  check(res, {
    "lfdata status 200": (r) => r.status === 200,
    "lfdata has data": (r) => r.json() !== null,
  });
  sleep(1);

  // Test historical data endpoint
  res = http.get(`${BASE_URL}/kostal/historicaldata`);
  check(res, {
    "historical status 200": (r) => r.status === 200,
    "historical has data": (r) => r.json() !== null,
  });
  sleep(2);
}
