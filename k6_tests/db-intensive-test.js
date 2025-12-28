import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

// Custom metrics
const dbQueryTime = new Trend("db_query_time");

export const options = {
  stages: [
    { duration: "1m", target: 20 },    // Ramp up to 20 concurrent users
    { duration: "3m", target: 50 },    // Increase to 50 concurrent DB reads
    { duration: "3m", target: 100 },   // Push to 100 concurrent DB reads
    { duration: "2m", target: 50 },    // Step down
    { duration: "1m", target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_failed: ["rate<0.01"],        // Less than 1% failure
    http_req_duration: [
        "p(95)<1500",                       // 95% under 1.5s (DB queries can be slower)
        "p(99)<3000"                        // 99% under 3s
    ],
    db_query_time: ["p(95)<1500"],         // Track DB query performance
  },
};

const BASE_URL = "http://localhost:8082";

export default function () {
  // Focus on historical data endpoint which queries 30 and 365 days
  // This is the most database-intensive operation
  const res = http.get(`${BASE_URL}/kostal/historicaldata`);

  dbQueryTime.add(res.timings.duration);

  check(res, {
    "status 200": (r) => r.status === 200,
    "has historical data": (r) => {
      try {
        const data = r.json();
        return data !== null && data !== undefined;
      } catch (e) {
        return false;
      }
    },
    "query completed in reasonable time": (r) => r.timings.duration < 5000,
    "response has correct structure": (r) => {
      try {
        const data = r.json();
        // Check if response has expected fields (adjust based on your actual response)
        return data.hasOwnProperty("today") ||
               data.hasOwnProperty("last30Days") ||
               data.hasOwnProperty("last365Days");
      } catch (e) {
        return false;
      }
    },
  });

  // Short sleep to maintain high concurrent load on database
  sleep(0.5);
}
