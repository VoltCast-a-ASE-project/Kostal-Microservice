import http from "k6/http";
import { check, sleep } from "k6";
import { Rate } from "k6/metrics";

// Tests load across the border


export const options = {
  stages: [
    { duration: "2m", target: 50 },    // Ramp up to 50 users
    { duration: "3m", target: 100 },   // Ramp up to 100 users
    { duration: "3m", target: 200 },   // Ramp up to 200 users
    { duration: "3m", target: 300 },   // Ramp up to 300 users
    { duration: "2m", target: 400 },   // Push to 400 users
    { duration: "2m", target: 0 },     // Ramp down to 0
  ],
  thresholds: {
    http_req_failed: ["rate<0.05"],      // Allow up to 5% failure during stress
    http_req_duration: ["p(95)<2000"],   // 95% under 2s during stress
  },
};

const BASE_URL = "http://localhost:8082";

export default function () {
  const endpoints = [
    `${BASE_URL}/kostal/realtimedata`,
    `${BASE_URL}/kostal/lfdata`,
    `${BASE_URL}/kostal/historicaldata`,
  ];

  // Randomly hit different endpoints to stress the system
  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];

  const res = http.get(endpoint);
  check(res, {
    "status is 200 or 503": (r) => r.status === 200 || r.status === 503,
    "response time OK": (r) => r.timings.duration < 3000,
  });

  sleep(0.5); // Shorter sleep for more aggressive stress
}
