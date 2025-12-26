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
**Purpose**: Track request latency distribution across different endpoints  
**Use**: 
- Identify slow endpoints
- Set SLA targets (e.g., P95 < 500ms)
- Detect performance degradation over time
- Optimize critical user paths

### `http.server.active_requests`
**Type**: Gauge  
**Unit**: count  
**Labels**: `method`, `route`  
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
**Purpose**: Track new user registrations  
**Use**:
- Monitor user growth
- Compare SSO provider popularity
- Track onboarding funnel
- Business analytics

### `session.active.count`
**Type**: Gauge  
**Unit**: count  
**Purpose**: Number of active user sessions  
**Use**:
- Monitor concurrent users
- Capacity planning
- Track user engagement
- Detect unusual session patterns

### `session.created.count`
**Type**: Counter  
**Unit**: count  
**Purpose**: Total sessions created  
**Use**:
- Track session churn
- Monitor login frequency
- Identify session issues

### `session.duration`
**Type**: Histogram  
**Unit**: seconds  
**Purpose**: How long users stay logged in  
**Use**:
- Understand user engagement
- Session timeout optimization
- User behavior analysis

### `session.storage.size`
**Type**: Gauge  
**Unit**: bytes  
**Labels**: `session_type` (authenticated, guest)  
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
**Purpose**: Track business transaction performance  
**Use**:
- Monitor complex operations
- Optimize transaction scope
- Identify lock contention
- Performance benchmarking

### `db.connection.active`
**Type**: Gauge  
**Unit**: count  
**Purpose**: Active database connections  
**Use**:
- Connection pool monitoring
- Detect connection leaks
- Capacity planning
- Connection pool tuning

### `db.connection.wait_time`
**Type**: Histogram  
**Unit**: milliseconds  
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
**Purpose**: Track consent sheet modifications  
**Use**:
- Monitor user activity
- Track feature engagement
- Identify most-edited fields

### `consent.entry.changes`
**Type**: Counter  
**Unit**: count  
**Labels**: `status` (yes, okay, maybe, no, unknown), `template_id`  
**Purpose**: Track consent preference changes  
**Use**:
- Monitor consent patterns
- Identify problematic topics
- Content moderation insights
- User preference analytics

### `group.created`
**Type**: Counter  
**Unit**: count  
**Purpose**: Track RPG group creation  
**Use**:
- Monitor platform adoption
- Track campaign creation
- Business metrics

### `group.members.count`
**Type**: Histogram  
**Unit**: count  
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
**Purpose**: Track group join attempts  
**Use**:
- Monitor invite code effectiveness
- Detect onboarding friction
- Track collaboration features

### `group.leave.count`
**Type**: Counter  
**Unit**: count  
**Purpose**: Track users leaving groups  
**Use**:
- Monitor group churn
- Identify problematic groups
- User retention insights

### `playfun.questionnaire.completed`
**Type**: Counter  
**Unit**: count  
**Purpose**: Track playstyle questionnaire completions  
**Use**:
- Monitor feature adoption
- Onboarding funnel analysis
- Feature engagement

### `playfun.answer.changes`
**Type**: Counter  
**Unit**: count  
**Labels**: `question_id`, `play_style`  
**Purpose**: Track questionnaire answer modifications  
**Use**:
- Identify confusing questions
- Track user engagement
- Question refinement

### `sheet.share.generated`
**Type**: Counter  
**Unit**: count  
**Labels**: `share_type` (qr_code, link)  
**Purpose**: Track public sheet sharing  
**Use**:
- Monitor feature usage
- Track collaboration patterns
- Virality metrics

### `sheet.public.views`
**Type**: Counter  
**Unit**: count  
**Labels**: `has_share_id`  
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
**Purpose**: Application startup time  
**Use**:
- Monitor deployment health
- Optimize startup performance
- Detect initialization issues

### `page.render.duration`
**Type**: Histogram  
**Unit**: milliseconds  
**Labels**: `page` (home, sheet, group_overview, playfun, admin, etc.)  
**Purpose**: Time to render each page  
**Use**:
- Optimize page performance
- Identify rendering bottlenecks
- User experience monitoring

### `component.render.duration`
**Type**: Histogram  
**Unit**: milliseconds  
**Labels**: `component` (ConsentEntryComponent, SheetDisplayComponent, etc.)  
**Purpose**: Component rendering performance  
**Use**:
- Optimize component performance
- Identify heavy components
- UI performance tuning

### `async.task.duration`
**Type**: Histogram  
**Unit**: milliseconds  
**Labels**: `task_type`  
**Purpose**: Async operation performance  
**Use**:
- Monitor background task performance
- Optimize async operations
- Detect async bottlenecks

### `cache.hit_rate`
**Type**: Counter  
**Unit**: count  
**Labels**: `cache_type` (consent_template, localized_text), `result` (hit, miss)  
**Purpose**: Track cache effectiveness  
**Use**:
- Optimize caching strategy
- Monitor cache performance
- Identify caching opportunities

### `memory.usage`
**Type**: Gauge  
**Unit**: bytes  
**Labels**: `type` (rss, vms, shared)  
**Purpose**: Process memory usage  
**Use**:
- Detect memory leaks
- Capacity planning
- Resource optimization

### `cpu.usage`
### `cpu.usage`
**Type**: Gauge  
**Unit**: percent (0-100)  
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
**Purpose**: Track unhandled exceptions  
**Use**:
- Critical error monitoring
- Emergency alerting
- Stability tracking

### `db.error.count`
**Type**: Counter  
**Unit**: count  
**Labels**: `operation`, `error_type` (timeout, connection, constraint, etc.)  
**Purpose**: Database-specific errors  
**Use**:
- Database health monitoring
- Detect data integrity issues
- Connection problem detection

### `auth.error.count`
**Type**: Counter  
**Unit**: count  
**Labels**: `provider`, `error_type`  
**Purpose**: Authentication errors  
**Use**:
- SSO provider reliability
- Security monitoring
- User experience issues

### `sso.callback.duration`
**Type**: Histogram  
**Unit**: milliseconds  
**Labels**: `provider` (google, discord)  
**Purpose**: SSO callback processing time  
**Use**:
- Monitor SSO performance
- Optimize authentication flow
- Detect SSO issues

### `healthcheck.status`
**Type**: Gauge  
**Unit**: 0 (down) or 1 (up)  
**Purpose**: Service health status  
**Use**:
- Service monitoring
- Uptime tracking
- Automated health checks

### `data.validation.errors`
**Type**: Counter  
**Unit**: count  
**Labels**: `field`, `error_type`  
**Purpose**: Track data validation failures  
**Use**:
- Identify problematic inputs
- UX improvement opportunities
- Data quality monitoring

---

## Implementation Priority

### Phase 1 (Critical)
1. `http.server.request.duration`
2. `http.server.request.count`
3. `error.count`
4. `db.query.duration`
5. `auth.login.attempts`

### Phase 2 (Important)
1. `session.active.count`
2. `consent.sheet.created`
3. `group.created`
4. `page.render.duration`
5. `db.connection.active`

### Phase 3 (Enhanced)
1. All business domain metrics
2. Detailed performance metrics
3. Advanced error tracking
4. Resource utilization metrics

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
