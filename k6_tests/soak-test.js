import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

// Tests stability with constant load over extended periods

const responseTime = new Trend("response_time");

export const options = {
  stages: [
    { duration: "5m", target: 30 },    // Ramp up to 30 users
    { duration: "60m", target: 30 },   // Hold 30 users for 1 hour (soak period)
    { duration: "5m", target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_failed: ["rate<0.01"],        // Less than 1% failure
    http_req_duration:[
        "p(95)<600",                        // 95% under 600ms
        "p(99)<1200"                        // 99% under 1.2s
    ],
    response_time: ["p(95)<600"],          // Monitor degradation over time
  },
};

const BASE_URL = "http://localhost:8082";

export default function () {
  // Rotate through all endpoints to simulate real usage over extended period
  const endpoints = [
    { url: `${BASE_URL}/kostal/realtimedata`, name: "realtime" },
    { url: `${BASE_URL}/kostal/lfdata`, name: "lfdata" },
    { url: `${BASE_URL}/kostal/historicaldata`, name: "historical" },
  ];

  endpoints.forEach((endpoint) => {
    const res = http.get(endpoint.url);

    responseTime.add(res.timings.duration);

    check(res, {
      [`${endpoint.name} status 200`]: (r) => r.status === 200,
      [`${endpoint.name} response time OK`]: (r) => r.timings.duration < 2000,
      [`${endpoint.name} has body`]: (r) => r.body.length > 0,
    });


    sleep(2); // Realistic user think time
  });

  sleep(3); // Additional pause between cycles
}
