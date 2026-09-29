# Scoring Formula Documentation

## Overview
The scoring system has been enhanced to provide accurate relevance scores with special handling for top 5 results and proper seniority level matching.

## Base Scoring Formula

### Components (Weighted)
1. **Industry Alignment** (35% weight)
   - Matches person's industry with query terms
   - Checks company industry alignment if provided
   - Score: 0-100

2. **Role Relevance** (30% weight)
   - Job title matching with query terms
   - Headline matching
   - **Seniority Level Matching** (Enhanced)
     - Uses `seniority_levels` from parsed query
     - Checks person's seniority field
     - Matches against job_title and headline
     - Score boost: +40 for exact match, +30 for keyword match

3. **Location Proximity** (15% weight)
   - Exact location match: 100
   - City match: 90
   - Partial match: 70
   - Country match: 50
   - No match: 0

4. **Profile Completeness** (10% weight)
   - Uses `profile_completeness` field
   - Score: 0-100

5. **Recency/Freshness** (5% weight)
   - Based on `importDate`
   - <30 days: 100
   - <90 days: 75
   - <180 days: 50
   - <365 days: 25
   - >365 days: 10

6. **Special Flags** (5% weight)
   - Premium member: +30
   - Job seeker: +20
   - Base: 50

### Base Score Calculation
```
base_score = (
    industry_score × 0.35 +
    role_score × 0.30 +
    location_score × 0.15 +
    completeness_score × 0.10 +
    recency_score × 0.05 +
    flags_score × 0.05
)
```

## Top 5 Scoring Formula

For the first 5 results, an enhanced scoring formula is applied:

### Rank-Based Boosts
- **Rank 1**: +15%
- **Rank 2**: +10%
- **Rank 3**: +5%
- **Rank 4-5**: +2%

### Additional Boosts
- **Seniority Match**: +10% (if seniority_levels match person's seniority)
- **High Completeness**: +5% (if profile_completeness > 80%)
- **Premium Member**: +3% (if premium = true/yes)

### Exact Match Boosts (Applied to all results)
- **Job Title Match**: +3%
- **Company Match**: +3%
- **Location Match**: +2%
- **Industry/Technology Match**: +2%

### Top 5 Final Score
```
final_score = base_score + rank_boost + seniority_boost + 
              completeness_boost + premium_boost + exact_match_boosts
```

**Capped at 100%**

## Seniority Level Matching

### Extracted Seniority Levels
The LLM parser extracts seniority levels from queries:
- `executive` - CEO, CTO, CIO, VP, Vice President
- `director` - Director, Head of, Head
- `manager` - Manager, Managing
- `leader` - Lead, Leader, Leading
- `founder` - Founder, Co-founder

### Matching Logic
1. Checks `person.seniority` field
2. Checks `person.job_title` for seniority keywords
3. Checks `person.headline` for seniority keywords
4. Exact match: +40 points
5. Keyword match: +30 points

## Score Display (Frontend)

### Score Ranges
- **80-100%**: "Excellent Match" (Green/Purple)
- **60-79%**: "Good Match" (Cyan)
- **40-59%**: "Fair Match" (Light Cyan)
- **0-39%**: "Low Match" (Red)

### Display Format
- Score badge with percentage
- Match quality label
- Color-coded based on score range

## Example Calculation

### Query: "Find CEO in Riyadh working in AI"

**Person Profile:**
- Job Title: "CEO"
- Industry: "Artificial Intelligence"
- Location: "Riyadh, Saudi Arabia"
- Seniority: "Executive"
- Profile Completeness: 85%
- Premium: Yes

**Base Score:**
- Industry Alignment: 100 × 0.35 = 35
- Role Relevance: 100 × 0.30 = 30 (CEO match + seniority match)
- Location Proximity: 100 × 0.15 = 15
- Profile Completeness: 85 × 0.10 = 8.5
- Recency: 75 × 0.05 = 3.75
- Special Flags: 80 × 0.05 = 4
- **Base Total: 96.25**

**Top 5 Boost (Rank 1):**
- Rank Boost: +15
- Seniority Boost: +10
- Completeness Boost: +5
- Premium Boost: +3
- Job Title Match: +3
- Location Match: +2
- **Total Boost: +38**

**Final Score: min(100, 96.25 + 38) = 100%**

## Implementation Notes

1. **Seniority Levels**: Extracted from query and passed to scoring engine
2. **Top 5 Formula**: Only applied to first 5 results
3. **Score Capping**: All scores capped at 100%
4. **Explanation**: Includes seniority match info when applicable
5. **Statistics**: Query results tracked for optimization

## API Endpoints

- `/api/search/llm` - Main search with enhanced scoring
- `/api/query/stats` - Query statistics
- `/api/query/popular` - Popular queries
- `/api/query/recent` - Recent queries


