# Business Answers

Candidate name: Sidha
Date: 2026-07-27

---

## Q1. Which region has the worst on-time delivery performance, and what's actually driving it?

**Answer:**

The **Central** region has the worst on-time delivery performance with a **50.3% late rate** (433 out of 861 delivered shipments arrived after the promised date), followed closely by North at 49.2%.

| Region  | Total Delivered | Late | Late % | Avg Delay (days) |
|---------|----------------|------|--------|------------------|
| Central | 861            | 433  | 50.3%  | +0.34            |
| North   | 833            | 410  | 49.2%  | +0.40            |
| East    | 837            | 409  | 48.9%  | +0.27            |
| West    | 870            | 419  | 48.2%  | +0.17            |
| South   | 126            | 60   | 47.6%  | +0.13            |

**What's driving it:**

The primary drivers in Central are specific carriers underperforming in that region:

- **CARR_08 in Central**: 61.1% late rate (33/54 shipments) — the single worst region×carrier combination among high-volume cells
- **CARR_02 in Central**: 58.6% late rate (41/70 shipments)
- **CARR_10 in Central**: 53.7% late rate (29/54 shipments)

Transport mode is **not** a significant driver — FTL (48.8% late), LTL (50.0%), and PTL (47.8%) perform similarly across the board, so the issue is carrier-specific rather than mode-specific.

It's also worth noting that South has only 126 delivered shipments with actual dates (vs 830+ for others), making its numbers less statistically reliable.

**How you checked it (query/method):**

```sql
-- On-time performance by region
SELECT
    region,
    COUNT(shipment_id)                                          AS total,
    SUM(CASE WHEN actual_delivery_date > promised_delivery_date
             THEN 1 ELSE 0 END)                                AS late,
    ROUND(AVG(DATEDIFF(day, promised_delivery_date,
                       actual_delivery_date)), 2)               AS avg_delay_days,
    ROUND(SUM(CASE WHEN actual_delivery_date > promised_delivery_date
                   THEN 1 ELSE 0 END) * 100.0
          / COUNT(shipment_id), 1)                              AS late_pct
FROM   shipments
WHERE  actual_delivery_date IS NOT NULL
GROUP  BY region
ORDER  BY late_pct DESC;

-- Driver analysis: Region × Carrier cross-tab
SELECT
    region,
    carrier_id,
    COUNT(shipment_id)                                          AS total,
    SUM(CASE WHEN actual_delivery_date > promised_delivery_date
             THEN 1 ELSE 0 END)                                AS late,
    ROUND(SUM(CASE WHEN actual_delivery_date > promised_delivery_date
                   THEN 1 ELSE 0 END) * 100.0
          / COUNT(shipment_id), 1)                              AS late_pct
FROM   shipments
WHERE  actual_delivery_date IS NOT NULL
GROUP  BY region, carrier_id
ORDER  BY late_pct DESC;
```

---

## Q2. Is there a relationship between freight cost and distance? Which carrier(s) deviate, and by how much?

**Answer:**

There is a **weak positive relationship** between freight cost and distance — the Pearson correlation is only **r = 0.30** across all carriers. A linear regression yields:

> `freight_cost = 27.20 × distance_km − 1,090`

However, this weak correlation is **almost entirely explained by one carrier**: **CARR_07**.

**CARR_07 is an extreme outlier:**

| Carrier | Avg Cost   | Avg Distance | Avg ₹/km  | Avg Deviation from Regression |
|---------|-----------|-------------|-----------|-------------------------------|
| CARR_07 | ₹206,161  | 1,282 km    | ₹160.8/km | **+548%**                     |
| Others  | ~₹20,500  | ~1,280 km   | ~₹13/km   | −32% to −36%                  |

CARR_07 charges roughly **10× more** than every other carrier for comparable distances. With 342 shipments, this isn't an anomaly — it's a consistently premium-priced carrier (possibly a specialized or express service).

**Excluding CARR_07**, the remaining 14 carriers show a much tighter cost-distance relationship with similar pricing (all averaging ₹12–14/km). No other carrier significantly deviates from the expected cost for its distance.

**How you checked it (query/method):**

```sql
-- Correlation between freight cost and distance
-- Pearson r = 0.2959
SELECT
    (n * sum_xy - sum_x * sum_y)
    / NULLIF(
        SQRT(n * sum_x2 - sum_x * sum_x)
      * SQRT(n * sum_y2 - sum_y * sum_y),
      0
    ) AS pearson_r
FROM (
    SELECT
        CAST(COUNT(*)                        AS FLOAT) AS n,
        CAST(SUM(distance_km)                AS FLOAT) AS sum_x,
        CAST(SUM(freight_cost)               AS FLOAT) AS sum_y,
        CAST(SUM(distance_km * distance_km)  AS FLOAT) AS sum_x2,
        CAST(SUM(freight_cost * freight_cost) AS FLOAT) AS sum_y2,
        CAST(SUM(distance_km * freight_cost) AS FLOAT) AS sum_xy
    FROM shipments
    WHERE distance_km > 0
) t;

-- Residual analysis by carrier
-- Using regression: freight_cost = 27.20 * distance_km - 1090.29
SELECT
    carrier_id,
    COUNT(shipment_id)                                          AS shipments,
    ROUND(AVG(freight_cost), 0)                                 AS avg_cost,
    ROUND(AVG(freight_cost / distance_km), 1)                   AS avg_cost_per_km,
    ROUND(AVG(
        (freight_cost - (27.20 * distance_km - 1090.29))
        / NULLIF(27.20 * distance_km - 1090.29, 0) * 100
    ), 1)                                                       AS avg_deviation_pct
FROM   shipments
WHERE  distance_km > 0
GROUP  BY carrier_id
ORDER  BY avg_deviation_pct DESC;
```

---

## Q3. Which customer(s) are experiencing the most delivery delays? Carrier-driven, region-driven, or something else?

**Answer:**

**Top 5 customers by late delivery rate:**

| Customer | Total Delivered | Late | Late % | Avg Delay (days) |
|----------|----------------|------|--------|------------------|
| CUST_026 | 23             | 17   | 73.9%  | +1.61            |
| CUST_050 | 32             | 22   | 68.8%  | +1.00            |
| CUST_114 | 32             | 22   | 68.8%  | +1.06            |
| CUST_119 | 32             | 22   | 68.8%  | +1.66            |
| CUST_116 | 35             | 24   | 68.6%  | +1.26            |

**Root-cause analysis — it's "something else":**

For all top-5 worst customers, delays are **spread across multiple carriers and multiple regions**. This rules out a single carrier or region as the root cause:

- **CUST_026**: Late shipments came from CARR_01, CARR_02, CARR_04, CARR_07, CARR_09, CARR_10, CARR_11, CARR_12 (8 different carriers). Across North (100% late), East (80%), West (75%), Central (40%).
- **CUST_116**: Late across 11 different carriers and all 5 regions.
- **CUST_050**: Late across 12 different carriers and all 5 regions — but notably **Central region** is 91.7% late for this customer (11/12), suggesting a regional factor for this specific customer.

The pattern is **not carrier-driven** (too many different carriers involved) and **mostly not region-driven** (spread across all regions). Possible explanations:

1. **Customer-specific factors**: Remote or hard-to-reach delivery addresses, strict delivery windows, or complex requirements
2. **Shipment complexity**: These customers may have harder-to-fulfill shipment profiles
3. **Volume effect**: Some of these customers have lower shipment volumes (CUST_026 = 23), so a few late shipments heavily skew the percentage

**How you checked it (query/method):**

```sql
-- Top 5 customers by late delivery rate
SELECT
    customer_id,
    COUNT(shipment_id)                                          AS total,
    SUM(CASE WHEN actual_delivery_date > promised_delivery_date
             THEN 1 ELSE 0 END)                                AS late,
    ROUND(AVG(DATEDIFF(day, promised_delivery_date,
                       actual_delivery_date)), 2)               AS avg_delay_days,
    ROUND(SUM(CASE WHEN actual_delivery_date > promised_delivery_date
                   THEN 1 ELSE 0 END) * 100.0
          / COUNT(shipment_id), 1)                              AS late_pct
FROM   shipments
WHERE  actual_delivery_date IS NOT NULL
GROUP  BY customer_id
ORDER  BY late_pct DESC
LIMIT  5;

-- Root-cause breakdown: carrier & region for a specific customer
SELECT
    customer_id,
    carrier_id,
    COUNT(shipment_id)                                          AS total,
    SUM(CASE WHEN actual_delivery_date > promised_delivery_date
             THEN 1 ELSE 0 END)                                AS late,
    ROUND(SUM(CASE WHEN actual_delivery_date > promised_delivery_date
                   THEN 1 ELSE 0 END) * 100.0
          / COUNT(shipment_id), 1)                              AS late_pct
FROM   shipments
WHERE  actual_delivery_date IS NOT NULL
  AND  customer_id IN ('CUST_026','CUST_050','CUST_114','CUST_119','CUST_116')
GROUP  BY customer_id, carrier_id
ORDER  BY customer_id, late_pct DESC;

SELECT
    customer_id,
    region,
    COUNT(shipment_id)                                          AS total,
    SUM(CASE WHEN actual_delivery_date > promised_delivery_date
             THEN 1 ELSE 0 END)                                AS late,
    ROUND(SUM(CASE WHEN actual_delivery_date > promised_delivery_date
                   THEN 1 ELSE 0 END) * 100.0
          / COUNT(shipment_id), 1)                              AS late_pct
FROM   shipments
WHERE  actual_delivery_date IS NOT NULL
  AND  customer_id IN ('CUST_026','CUST_050','CUST_114','CUST_119','CUST_116')
GROUP  BY customer_id, region
ORDER  BY customer_id, late_pct DESC;
```

---

## Q4. What data quality issues did you find, and how did you handle them?

**Answer:**

I found **8 data quality issues**, ranked by severity:

### Critical Issues

1. **15 Duplicate Shipment IDs**: 15 rows share a `shipment_id` with another row.
   - *Handling*: Dropped duplicates, kept first occurrence. Impact: minimal (0.3% of data).

2. **1,488 Missing `actual_delivery_date` (29.7%)**: Nearly a third of rows lack this field. Breakdown: 502 In-Transit, 302 Cancelled, 588 Delivered (should have a date), 86 Delayed.
   - *Handling*: Only used rows with `actual_delivery_date` present for on-time analysis. This leaves 3,527 usable rows — still statistically robust for all segments except South region.

3. **588 "Delivered" with No Actual Date**: These shipments are marked Delivered but have no `actual_delivery_date`, creating a blind spot.
   - *Handling*: Excluded from on-time calculations. Flagged as a data collection gap that should be fixed at source.

### Medium Issues

4. **499 Rows with Actual Date but Status ≠ Delivered**: Rows marked as Delayed/In-Transit/Cancelled have `actual_delivery_date` filled in. The status field contradicts the date field.
   - *Handling*: Included these in on-time analysis (the date is usable even if the status label is wrong). The `status` field appears to be unreliably maintained.

5. **71 Missing Booking Dates, 88 Missing Pickup Dates**: Gaps in operational date tracking.
   - *Handling*: Excluded from time-trend charts; other analyses unaffected.

### Low-Impact Issues

6. **244 Same Origin & Destination City**: These show non-zero distances (up to 2,499 km), suggesting `distance_km` may be route distance rather than city-to-city.
   - *Handling*: Retained. The distance field appears to represent actual route km.

7. **231 Freight Cost Outliers (>3×IQR)**: Almost all belong to CARR_07 (avg ₹206K vs ₹20K for others).
   - *Handling*: Not removed — CARR_07 is consistently premium-priced, not erroneous. Analyzed separately in cost analysis.

8. **South Region Under-represented**: Only 126 delivered-with-actual-date records vs 830+ for other regions.
   - *Handling*: Noted as a caveat; South's performance stats should be interpreted with caution.

---

## Q5. If you could track exactly one metric weekly to catch delivery problems early, what would it be and why?

**Answer:**

**The metric: Weekly "Promise Breach Rate" — the percentage of shipments delivered after their promised delivery date, segmented by region and carrier.**

Specifically:

> **Promise Breach Rate** = (Shipments where `actual_delivery_date > promised_delivery_date`) / (All shipments delivered that week) × 100

**Why this single metric:**

1. **It's the customer-facing metric that matters most.** Customers don't care about internal transit times — they care about whether the shipment arrived by the date they were promised. A rising breach rate directly translates to customer dissatisfaction and churn risk.

2. **It's a leading indicator.** If this metric ticks up from 48% to 55% in a single week, you know something has changed — a carrier is struggling, a route is congested, or a region is having operational issues. You can investigate *before* customer complaints pile up.

3. **It naturally rolls up the right dimensions.** By segmenting it weekly by region and carrier, you can immediately pinpoint *where* the problem is emerging. The heatmap in Tab 2 of the dashboard shows exactly this kind of drill-down.

4. **It's simple to compute and explain.** Ops teams need a metric they can act on without needing a data science degree. "52% of shipments this week missed their promise" is immediately actionable.

**What I'd pair it with (if I got a second metric):** Average delay magnitude (in days) for breached shipments — because a 1-day miss is very different from a 7-day miss, and the breach rate alone doesn't capture severity.

---

## Anything else you'd flag if this were a real dataset at FreightFox?

1. **CARR_07 pricing needs investigation.** This carrier charges 10× more than all others. If it's a premium/express service, the data should include a `service_level` column to distinguish it. If it's a pricing error, it's costing the company significantly.

2. **The `status` field is unreliable.** 499 non-Delivered shipments have actual delivery dates, and 588 Delivered shipments don't. This field should either be auto-derived from dates or have stricter validation at data entry.

3. **South region data gap.** South has far fewer usable records for on-time analysis (126 vs 830+). Either fewer shipments go to/from South, or there's a systematic data collection issue in that region that should be investigated.

4. **Missing `actual_delivery_date` for Delivered shipments is a systemic problem.** 588 shipments (16% of Delivered) lack this critical field. This likely means delivery confirmation isn't being captured consistently — possibly a driver app or scanning process issue.

5. **Consider adding fields**: shipment weight/volume, service level (express/standard), customer location type (metro/rural), and reason codes for delays would make root-cause analysis much richer.
