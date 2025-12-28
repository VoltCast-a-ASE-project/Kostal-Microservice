import http from "k6/http";
import { check, sleep } from "k6";
import { Rate } from "k6/metrics";

//  Tests sudden load peaks

export const options = {
  stages: [
    { duration: "1m", target: 10 },    // Normal load
    { duration: "10s", target: 200 },  // Sudden spike to 200 users
    { duration: "2m", target: 200 },   // Hold spike for 2 minutes
    { duration: "10s", target: 10 },   // Drop back to normal
    { duration: "1m", target: 10 },    // Recovery period
    { duration: "10s", target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_failed: ["rate<0.1"],       // Allow up to 10% failure during spike
    http_req_duration: ["p(90)<3000"],   // 90% under 3s during spike
  },
};

const BASE_URL = "http://localhost:8082";

export default function () {
  // Spike test primarily targets realtime data endpoint (most likely to see spikes)
  const res = http.get(`${BASE_URL}/kostal/realtimedata`);

  check(res, {
    "status is 200 or 503": (r) => r.status === 200 || r.status === 503,
    "response received": (r) => r.body.length > 0,
  });

  // Minimal sleep to create more pressure during spike
  sleep(0.3);
}
