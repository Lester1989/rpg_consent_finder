# OpenTelemetry Metrics for RPG Consent Finder

This document outlines the key metrics to collect for monitoring the RPG Consent Finder application using OpenTelemetry.

## Table of Contents
- [HTTP & Request Metrics](#http--request-metrics)
- [Authentication & Session Metrics](#authentication--session-metrics)
- [Database Metrics](#database-metrics)
- [Business Domain Metrics](#business-domain-metrics)
- [Performance & Resource Metrics](#performance--resource-metrics)
- [Error & Reliability Metrics](#error--reliability-metrics)

---

## HTTP & Request Metrics

### `http.server.request.duration`
**Type**: Histogram  
**Unit**: milliseconds  
**Labels**: `method`, `route`, `status_code`  
**Status**: ✅ **Implemented**  
**Query**:
```promql
# P95 latency by route
histogram_quantile(0.95, sum(rate(http_server_request_duration_bucket[5m])) by (le, http_route))

# Average latency by route and method
rate(http_server_request_duration_sum[5m]) / rate(http_server_request_duration_count[5m])
```
**Purpose**: Track request latency distribution across different endpoints  
**Use**: 
- Identify slow endpoints
- Set SLA targets (e.g., P95 < 500ms)
- Detect performance degradation over time
- Optimize critical user paths

### `http.server.active_requests`
**Type**: Gauge (up/down counter)  
**Unit**: count  
**Labels**: `method`, `route`  
**Status**: ✅ **Implemented**  
**Query**:
```promql
# Current active requests by route
http_server_active_requests

# Peak active requests in last 15 minutes
max_over_time(http_server_active_requests[15m])
```
**Purpose**: Track concurrent requests being processed  
**Use**:
- Detect traffic spikes
- Identify bottlenecks
- Capacity planning
- Load balancing decisions

### `http.server.request.count`
**Type**: Counter  
**Unit**: count  
**Labels**: `method`, `route`, `status_code`  
**Status**: ✅ **Implemented**  
**Query**:
```promql
# Request rate by route
rate(http_server_request_count[5m])

# Total requests in last hour
sum(increase(http_server_request_count[1h])) by (http_route)

# Error rate (4xx and 5xx)
sum(rate(http_server_request_count{http_status_code=~"[45].."}[5m])) / sum(rate(http_server_request_count[5m]))
```
**Purpose**: Total count of HTTP requests  
**Use**:
- Track traffic patterns
- Calculate request rates
- Identify most-used features
- Monitor API usage

---

## Authentication & Session Metrics

### `auth.login.attempts`
**Type**: Counter  
**Unit**: count  
**Labels**: `provider` (google, discord, local), `status` (success, failure)  
**Status**: ✅ **Implemented**  
**Query**:
```promql
# Login success rate by provider
sum(rate(auth_login_attempts{status="success"}[5m])) by (provider) / sum(rate(auth_login_attempts[5m])) by (provider)

# Failed login attempts
sum(rate(auth_login_attempts{status="failure"}[5m])) by (provider)

# Total logins in last hour
sum(increase(auth_login_attempts{status="success"}[1h]))
```
**Purpose**: Track authentication attempts and success rates  
**Use**:
- Monitor authentication health
- Detect brute force attacks
- Track SSO provider reliability
- Identify authentication issues early

### `auth.signup.count`
**Type**: Counter  
**Unit**: count  
**Labels**: `provider` (google, discord, local)  
**Status**: 🔄 **Planned** (requires user creation tracking)  
**Purpose**: Track new user registrations  
**Use**:
- Monitor user growth
- Compare SSO provider popularity
- Track onboarding funnel
- Business analytics

### `session.active.count`
**Type**: Gauge (observable)  
**Unit**: count  
**Status**: ✅ **Implemented**  
**Query**:
```promql
# Current active sessions
session_active_count

# Peak sessions today
max_over_time(session_active_count[24h])

# Average sessions over last hour
avg_over_time(session_active_count[1h])
```
**Purpose**: Number of active user sessions  
**Use**:
- Monitor concurrent users
- Capacity planning
- Track user engagement
- Detect unusual session patterns

### `session.created.count`
**Type**: Counter  
**Unit**: count  
**Status**: ✅ **Implemented**  
**Query**:
```promql
# Session creation rate
rate(session_created_count[5m])

# Sessions created in last 24h
increase(session_created_count[24h])
```
**Purpose**: Total sessions created  
**Use**:
- Track session churn
- Monitor login frequency
- Identify session issues

### `session.duration`
**Type**: Histogram  
**Unit**: seconds  
**Status**: 🔄 **Planned** (requires session lifecycle tracking)  
**Purpose**: How long users stay logged in  
**Use**:
- Understand user engagement
- Session timeout optimization
- User behavior analysis

### `session.storage.size`
**Type**: Gauge  
**Unit**: bytes  
**Labels**: `session_type` (authenticated, guest)  
**Status**: 🔄 **Planned** (requires session memory instrumentation)  
**Purpose**: Track session storage size  
**Use**:
- Monitor memory usage
- Detect session bloat
- Optimize session data
---

## Database Metrics

### `db.query.duration`
**Type**: Histogram  
**Unit**: milliseconds  
**Labels**: `operation` (select, insert, update, delete), `table`  
**Status**: 🔄 **Planned** (requires SQLModel/database instrumentation)  
**Purpose**: Track database query performance  
**Use**:
- Identify slow queries
- Optimize database access patterns
- Monitor query performance degradation
- Index optimization decisions

### `db.query.count`
**Type**: Counter  
**Unit**: count  
**Labels**: `operation` (select, insert, update, delete), `table`, `status` (success, error)  
**Status**: 🔄 **Planned** (requires database instrumentation)  
**Purpose**: Count database operations  
**Use**:
- Track database load
- Identify hot tables
- Detect N+1 query problems
- Monitor write vs read ratio

### `db.transaction.duration`
**Type**: Histogram  
**Unit**: milliseconds  
**Labels**: `operation` (create_sheet, create_group, join_group, etc.)  
**Status**: 🔄 **Planned** (requires transaction-level instrumentation)  
**Purpose**: Track business transaction performance  
**Use**:
- Monitor complex operations
- Optimize transaction scope
- Identify lock contention
- Performance benchmarking

### `db.connection.active`
**Type**: Gauge  
**Unit**: count  
**Status**: 🔄 **Planned** (requires connection pool instrumentation)  
**Purpose**: Active database connections  
**Use**:
- Connection pool monitoring
- Detect connection leaks
- Capacity planning
- Connection pool tuning

### `db.connection.wait_time`
**Type**: Histogram  
**Unit**: milliseconds  
**Status**: 🔄 **Planned** (requires connection pool instrumentation)  
**Purpose**: Time waiting for database connection  
**Use**:
- Detect pool exhaustion
- Optimize pool size
- Identify connection bottlenecks

---

## Business Domain Metrics

### `user.active.count`
**Type**: Gauge  
**Unit**: count  
**Labels**: `time_window` (last_hour, last_day, last_week)  
**Status**: 🔄 **Planned** (requires activity tracking)  
**Purpose**: Active users by time window  
**Use**:
- Track daily/weekly/monthly active users
- Business growth metrics
- Engagement tracking
- Feature adoption rates

### `consent.sheet.created`
**Type**: Counter  
**Unit**: count  
**Labels**: `user_type` (new, existing)  
**Status**: 🔄 **Planned** (requires sheet controller instrumentation)  
**Purpose**: Track consent sheet creation  
**Use**:
- Monitor feature usage
- Onboarding completion rates
- User engagement
- Feature popularity

### `consent.sheet.updated`
**Type**: Counter  
**Unit**: count  
**Labels**: `field_type` (entry, custom_entry, metadata)  
**Status**: 🔄 **Planned** (requires sheet controller instrumentation)  
**Purpose**: Track consent sheet modifications  
**Use**:
- Monitor user activity
- Track feature engagement
- Identify most-edited fields

### `consent.entry.changes`
**Type**: Counter  
**Unit**: count  
**Labels**: `status` (yes, okay, maybe, no, unknown), `template_id`  
**Status**: 🔄 **Planned** (requires entry component instrumentation)  
**Purpose**: Track consent preference changes  
**Use**:
- Monitor consent patterns
- Identify problematic topics
- Content moderation insights
- User preference analytics

### `group.created`
**Type**: Counter  
**Unit**: count  
**Status**: 🔄 **Planned** (requires group service instrumentation)  
**Purpose**: Track RPG group creation  
**Use**:
- Monitor platform adoption
- Track campaign creation
- Business metrics

### `group.members.count`
**Type**: Histogram  
**Unit**: count  
**Status**: 🔄 **Planned** (requires group service instrumentation)  
**Purpose**: Distribution of group sizes  
**Use**:
- Understand typical group sizes
- Optimize group features
- Capacity planning
- User behavior insights

### `group.join.count`
**Type**: Counter  
**Unit**: count  
**Labels**: `status` (success, invalid_code, already_member)  
**Status**: 🔄 **Planned** (requires group controller instrumentation)  
**Purpose**: Track group join attempts  
**Use**:
- Monitor invite code effectiveness
- Detect onboarding friction
- Track collaboration features

### `group.leave.count`
**Type**: Counter  
**Unit**: count  
**Status**: 🔄 **Planned** (requires group controller instrumentation)  
**Purpose**: Track users leaving groups  
**Use**:
- Monitor group churn
- Identify problematic groups
- User retention insights

### `playfun.questionnaire.completed`
**Type**: Counter  
**Unit**: count  
**Status**: 🔄 **Planned** (requires playfun controller instrumentation)  
**Purpose**: Track playstyle questionnaire completions  
**Use**:
- Monitor feature adoption
- Onboarding funnel analysis
- Feature engagement

### `playfun.answer.changes`
**Type**: Counter  
**Unit**: count  
**Labels**: `question_id`, `play_style`  
**Status**: 🔄 **Planned** (requires playfun controller instrumentation)  
**Purpose**: Track questionnaire answer modifications  
**Use**:
- Identify confusing questions
- Track user engagement
- Question refinement

### `sheet.share.generated`
**Type**: Counter  
**Unit**: count  
**Labels**: `share_type` (qr_code, link)  
**Status**: 🔄 **Planned** (requires sheet controller instrumentation)  
**Purpose**: Track public sheet sharing  
**Use**:
- Monitor feature usage
- Track collaboration patterns
- Virality metrics

### `sheet.public.views`
**Type**: Counter  
**Unit**: count  
**Labels**: `has_share_id`  
**Status**: 🔄 **Planned** (requires public sheet page instrumentation)  
**Purpose**: Track public sheet views  
**Use**:
- Monitor sharing effectiveness
- Privacy feature usage
- External traffic patterns

---

## Performance & Resource Metrics

### `app.startup.duration`
**Type**: Histogram  
**Unit**: milliseconds  
**Status**: ✅ **Implemented**  
**Query**:
```promql
# Average startup time
rate(app_startup_duration_sum[5m]) / rate(app_startup_duration_count[5m])

# P95 startup time
histogram_quantile(0.95, sum(rate(app_startup_duration_bucket[5m])) by (le))
```
**Purpose**: Application startup time  
**Use**:
- Monitor deployment health
- Optimize startup performance
- Detect initialization issues

### `page.render.duration`
**Type**: Histogram  
**Unit**: milliseconds  
**Labels**: `page` (home, sheet, group_overview, playfun, admin, etc.)  
**Status**: 🔄 **Planned** (requires page-level instrumentation)  
**Purpose**: Time to render each page  
**Use**:
- Optimize page performance
- Identify rendering bottlenecks
- User experience monitoring

### `component.render.duration`
**Type**: Histogram  
**Unit**: milliseconds  
**Labels**: `component` (ConsentEntryComponent, SheetDisplayComponent, etc.)  
**Status**: 🔄 **Planned** (requires component-level instrumentation)  
**Purpose**: Component rendering performance  
**Use**:
- Optimize component performance
- Identify heavy components
- UI performance tuning

### `async.task.duration`
**Type**: Histogram  
**Unit**: milliseconds  
**Labels**: `task_type`  
**Status**: 🔄 **Planned** (requires async task instrumentation)  
**Purpose**: Async operation performance  
**Use**:
- Monitor background task performance
- Optimize async operations
- Detect async bottlenecks

### `cache.hit_rate`
**Type**: Counter  
**Unit**: count  
**Labels**: `cache_type` (consent_template, localized_text), `result` (hit, miss)  
**Status**: 🔄 **Planned** (requires cache layer instrumentation)  
**Purpose**: Track cache effectiveness  
**Use**:
- Optimize caching strategy
- Monitor cache performance
- Identify caching opportunities

### `memory.usage`
**Type**: Gauge  
**Unit**: bytes  
**Labels**: `type` (rss, vms, shared)  
**Status**: 🔄 **Planned** (requires process instrumentation)  
**Purpose**: Process memory usage  
**Use**:
- Detect memory leaks
- Capacity planning
- Resource optimization

### `cpu.usage`
### `cpu.usage`
**Type**: Gauge  
**Unit**: percent (0-100)  
**Status**: 🔄 **Planned** (requires process instrumentation)  
**Purpose**: CPU utilization  
**Use**:
- Performance monitoring
- Capacity planning
- Identify CPU-intensive operations---

## Error & Reliability Metrics

### `error.count`
**Type**: Counter  
**Unit**: count  
**Labels**: `error_type`, `severity`, `page`, `component`  
**Status**: 🔄 **Planned** (requires error handling instrumentation)  
**Purpose**: Track application errors  
**Use**:
- Monitor application health
- Alert on error spikes
- Prioritize bug fixes
- Track error patterns

### `error.unhandled.count`
**Type**: Counter  
**Unit**: count  
**Labels**: `exception_type`, `route`  
**Status**: 🔄 **Planned** (requires exception handler instrumentation)  
**Purpose**: Track unhandled exceptions  
**Use**:
- Critical error monitoring
- Emergency alerting
- Stability tracking

### `db.error.count`
**Type**: Counter  
**Unit**: count  
**Labels**: `operation`, `error_type` (timeout, connection, constraint, etc.)  
**Status**: 🔄 **Planned** (requires database error instrumentation)  
**Purpose**: Database-specific errors  
**Use**:
- Database health monitoring
- Detect data integrity issues
- Connection problem detection

### `auth.error.count`
**Type**: Counter  
**Unit**: count  
**Labels**: `provider`, `error_type`  
**Status**: 🔄 **Planned** (requires auth error instrumentation)  
**Purpose**: Authentication errors  
**Use**:
- SSO provider reliability
- Security monitoring
- User experience issues

### `sso.callback.duration`
**Type**: Histogram  
**Unit**: milliseconds  
**Labels**: `provider` (google, discord)  
**Status**: 🔄 **Planned** (requires SSO callback instrumentation)  
**Purpose**: SSO callback processing time  
**Use**:
- Monitor SSO performance
- Optimize authentication flow
- Detect SSO issues

### `healthcheck.status`
**Type**: Gauge  
**Unit**: 0 (down) or 1 (up)  
**Status**: 🔄 **Planned** (requires healthcheck endpoint instrumentation)  
**Purpose**: Service health status  
**Use**:
- Service monitoring
- Uptime tracking
- Automated health checks

### `data.validation.errors`
**Type**: Counter  
**Unit**: count  
**Labels**: `field`, `error_type`  
**Status**: 🔄 **Planned** (requires form validation instrumentation)  
**Purpose**: Track data validation failures  
**Use**:
- Identify problematic inputs
- UX improvement opportunities
- Data quality monitoring

---

## Implementation Status Summary

### ✅ Implemented (7 metrics)
1. `http.server.request.duration` - Request latency tracking
2. `http.server.request.count` - Request counting with status codes
3. `http.server.active_requests` - Concurrent request tracking
4. `auth.login.attempts` - Authentication attempt tracking (local + SSO)
5. `session.active.count` - Active session gauge
6. `session.created.count` - Session creation counter
7. `app.startup.duration` - Application startup time

### 🔄 Planned - Phase 1 (Critical)
1. `error.count` - Application error tracking
2. `error.unhandled.count` - Unhandled exception tracking
3. `db.query.duration` - Database query performance
4. `db.query.count` - Database operation counting
5. `auth.signup.count` - User registration tracking

### 🔄 Planned - Phase 2 (Important)
1. `consent.sheet.created` - Sheet creation tracking
2. `consent.sheet.updated` - Sheet modification tracking
3. `group.created` - Group creation tracking
4. `page.render.duration` - Page rendering performance
5. `db.connection.active` - Connection pool monitoring

### 🔄 Planned - Phase 3 (Enhanced)
1. All remaining business domain metrics
2. Detailed performance metrics (component, async tasks)
3. Resource utilization metrics (CPU, memory)
4. Advanced error tracking and validation metrics

---

## Dashboarding Recommendations

### User Health Dashboard
- Active users (hourly, daily, weekly)
- Login success rate
- Session duration distribution
- New user signups

### Application Performance Dashboard
- Request latency (P50, P95, P99)
- Error rate
- Page render times
- Database query performance

### Business Metrics Dashboard
- Consent sheets created/updated
- Groups created/joined
- Playfun completions
- Share feature usage

### Infrastructure Dashboard
- CPU/Memory usage
- Database connections
- Cache hit rates
- Error counts by type

---

## Alerting Recommendations

### Critical Alerts
- Error rate > 5% for 5 minutes
- P95 latency > 2s for 5 minutes
- Application error rate > 5% for 5 minutes
  (Calculated as: `error.count` / `http.server.request.count` > 0.05)
  Includes: `error.count` (all types except validation), `error.unhandled.count`
  Excludes: `data.validation.errors`- Unhandled exceptions detected

### Warning Alerts
- Login failure rate > 10%
- Page render time > 1s P95
- Database query time > 500ms P95
- Memory usage > 80%

### Business Alerts
- No new users for 24 hours
- No consent sheets created for 12 hours
- SSO provider errors > 5%
