# K6 Performance Tests - Kostal Microservice

Performance testing suite for the Kostal Inverter Microservice.

## Prerequisites

```bash
# Install k6 (macOS)
brew install k6

# Ensure microservice is running on http://localhost:8082
```

## Available Tests

### 1. `load-test.js` - Baseline Performance
Establishes baseline metrics under normal load.
- 7-minute test: ramp to 20 users, hold 5m, ramp down
- Thresholds: <1% failures, p95 <500ms, p99 <1000ms

```bash
k6 run load-test.js
```

### 2. `stress-test.js` - Breaking Point
Finds service limits by progressively increasing load.
- 15-minute test: 50 → 100 → 200 → 300 → 400 users
- Thresholds: <5% failures, p95 <2000ms

```bash
k6 run stress-test.js
```

### 3. `spike-test.js` - Traffic Bursts
Tests sudden traffic spikes (e.g., mass dashboard refresh).
- ~4.5-minute test: 10 users → spike to 200 → hold 2m → recover
- Thresholds: <10% failures, p90 <3000ms

```bash
k6 run spike-test.js
```

### 4. `soak-test.js` - Long-term Stability
Detects memory leaks and degradation over time.
- 70-minute test: 30 steady users for 1 hour (+ 10m ramp)
- Watch for memory leaks and performance decay

```bash
k6 run soak-test.js
```

### 5. `db-intensive-test.js` - Database Performance
Stress tests SQLite with heavy concurrent reads.
- Up to 100 concurrent users hitting `/kostal/historicaldata`
- 10-minute test: 20 → 50 → 100 → 50 → 0 users (1m/3m/3m/2m/1m)
- Thresholds: <1% failures, p95 <1500ms, p99 <3000ms

```bash
k6 run db-intensive-test.js
```

### 6. `realistic-scenario-test.js` - Production Simulation
**Recommended for validation**. Simulates real user behavior.
- 50% realtime data, 25% lifetime data, 15% historical, 10% config
- Variable think times (2-15s)
- 14-minute test: 30 → 50 → 80 → 50 → 0 users (2m/5m/2m/3m/2m)
- Thresholds: <2% failures, p95 <800ms, p99 <1500ms

```bash
k6 run realistic-scenario-test.js
```

---

## Quick Start

**Run all tests at once:**
```bash
./run-all-tests.sh
```

**Or run individual tests:**
```bash
# 1. Start with realistic scenario (most important)
k6 run realistic-scenario-test.js

# 2. Validate database performance
k6 run db-intensive-test.js

# 3. Establish baseline
k6 run load-test.js

# 4. Optional: Find limits
k6 run stress-test.js
k6 run spike-test.js

# 5. Optional: Long-term stability (70 minutes)
k6 run soak-test.js
```

## Key Metrics to Watch

- **http_req_duration (p95, p99)**: Response time percentiles
- **http_req_failed**: Failure rate
- **http_reqs/s**: Throughput
- Tests **PASS** ✓ when all thresholds are met

## Troubleshooting

**High failure rates?**
- Ensure microservice is running on port 8082

**Slow response times?**
- Database queries may need optimization
- Check for SQLite lock contention
- Monitor CPU/memory usage
