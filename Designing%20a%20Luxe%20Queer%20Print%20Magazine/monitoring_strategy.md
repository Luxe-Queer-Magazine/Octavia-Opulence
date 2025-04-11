# Comprehensive Monitoring Strategy for Luxe Queer Magazine

This document outlines a complete monitoring strategy for all components of the Luxe Queer magazine system, enabling you to track performance, detect issues, and ensure smooth operation across all platforms.

## 1. Ghost CMS Monitoring

### Dashboard Metrics
- **Access Point**: https://rainbow-millipede.pikapod.net/ghost/
- **Key Metrics to Track**:
  - Content views and engagement
  - Member growth and retention
  - Email newsletter performance
  - Staff user activity

### Implementation Steps
1. **Configure Email Notifications**:
   ```
   Settings → Email → Notifications
   ```
   - Enable notifications for new members
   - Enable notifications for new comments
   - Set up notifications for failed email deliveries

2. **Set Up Custom Integrations**:
   ```
   Settings → Integrations
   ```
   - Create a custom integration for API access
   - Set up webhooks for important events:
     - New post published
     - Member signup/cancellation
     - Newsletter sent

3. **Create Admin Dashboard**:
   - Use Ghost Admin API to create a custom dashboard
   - Display key metrics in a single view
   - Set up daily/weekly email reports

## 2. Supabase Monitoring

### Dashboard Access
- **Access Point**: https://app.supabase.io/project/ovggshlfwumbtviwvbhi

### Database Monitoring
1. **Usage Metrics**:
   - Monitor database size and growth
   - Track query performance
   - Set up alerts for slow queries

2. **SQL Monitoring Queries**:
   ```sql
   -- Monitor active subscriptions
   CREATE OR REPLACE FUNCTION monitor_subscriptions()
   RETURNS TRIGGER AS $$
   BEGIN
     -- Log subscription changes
     INSERT INTO subscription_logs (
       user_id, 
       action, 
       tier_before, 
       tier_after, 
       timestamp
     ) VALUES (
       NEW.user_id, 
       TG_OP, 
       OLD.tier_id, 
       NEW.tier_id, 
       NOW()
     );
     
     -- Alert on suspicious activity (e.g., multiple tier changes in short period)
     IF (SELECT COUNT(*) FROM subscription_logs 
         WHERE user_id = NEW.user_id 
         AND timestamp > NOW() - INTERVAL '1 day') > 5 THEN
       
       -- Insert into alerts table
       INSERT INTO system_alerts (
         alert_type, 
         severity, 
         message, 
         related_id, 
         timestamp
       ) VALUES (
         'subscription_suspicious', 
         'warning', 
         'Multiple subscription changes detected', 
         NEW.user_id, 
         NOW()
       );
     END IF;
     
     RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   -- Create trigger
   CREATE TRIGGER monitor_subscription_changes
   AFTER UPDATE ON subscriptions
   FOR EACH ROW
   EXECUTE FUNCTION monitor_subscriptions();
   ```

3. **Create Monitoring Tables**:
   ```sql
   -- System alerts table
   CREATE TABLE system_alerts (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     alert_type TEXT NOT NULL,
     severity TEXT NOT NULL,
     message TEXT NOT NULL,
     related_id UUID,
     timestamp TIMESTAMPTZ NOT NULL,
     acknowledged BOOLEAN DEFAULT FALSE,
     acknowledged_by UUID,
     acknowledged_at TIMESTAMPTZ
   );

   -- System metrics table
   CREATE TABLE system_metrics (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     metric_name TEXT NOT NULL,
     metric_value NUMERIC NOT NULL,
     timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
   );
   ```

### Authentication Monitoring
1. **Track Sign-ups and Logins**:
   - Monitor authentication activity
   - Set up alerts for unusual patterns
   - Track failed login attempts

2. **Implement Auth Hooks**:
   ```js
   // In your Supabase client setup
   supabase.auth.onAuthStateChange((event, session) => {
     // Log auth events to your monitoring system
     logAuthEvent(event, session?.user?.id);
     
     // Check for suspicious activity
     if (event === 'SIGNED_IN') {
       checkForSuspiciousLogin(session?.user?.id);
     }
   });
   ```

### Edge Functions Monitoring
1. **Access Logs**:
   - Review invocation history
   - Monitor for errors and exceptions
   - Track performance metrics

2. **Set Up Log Forwarding**:
   - Configure log forwarding to a central logging system
   - Set up alerts for repeated errors
   - Create dashboards for function performance

## 3. n8n Workflow Monitoring

### Dashboard Access
- Access your n8n instance and navigate to the Executions tab

### Workflow Health Checks
1. **Create Monitoring Workflow**:
   - Set up a dedicated workflow that runs every hour
   - Check the status of all critical workflows
   - Send notifications for failed workflows

2. **Example Monitoring Workflow**:
   ```json
   {
     "nodes": [
       {
         "parameters": {
           "rule": {
             "interval": [
               {
                 "field": "hours"
               }
             ]
           }
         },
         "name": "Schedule Trigger",
         "type": "n8n-nodes-base.scheduleTrigger",
         "typeVersion": 1,
         "position": [
           250,
           300
         ]
       },
       {
         "parameters": {
           "functionCode": "// Get list of workflows to check\nconst criticalWorkflows = [\n  \"content-publishing\",\n  \"subscription-management\",\n  \"social-media-distribution\",\n  \"print-preparation\"\n];\n\n// Return workflow IDs to check\nreturn {json: {workflows: criticalWorkflows}};"
         },
         "name": "Prepare Workflow List",
         "type": "n8n-nodes-base.function",
         "typeVersion": 1,
         "position": [
           450,
           300
         ]
       },
       {
         "parameters": {
           "batchSize": 1,
           "options": {}
         },
         "name": "Split Workflows",
         "type": "n8n-nodes-base.splitInBatches",
         "typeVersion": 1,
         "position": [
           650,
           300
         ]
       },
       {
         "parameters": {
           "resource": "workflow",
           "operation": "getAll",
           "filters": {
             "name": "={{ $json.workflow }}"
           }
         },
         "name": "n8n",
         "type": "n8n-nodes-base.n8n",
         "typeVersion": 1,
         "position": [
           850,
           300
         ],
         "credentials": {
           "n8nApi": "n8n-internal-api"
         }
       },
       {
         "parameters": {
           "conditions": {
             "number": [
               {
                 "value1": "={{ $json.length }}",
                 "operation": "equal",
                 "value2": 0
               }
             ]
           }
         },
         "name": "Workflow Exists?",
         "type": "n8n-nodes-base.if",
         "typeVersion": 1,
         "position": [
           1050,
           300
         ]
       },
       {
         "parameters": {
           "resource": "execution",
           "operation": "getAll",
           "filters": {
             "workflowId": "={{ $json[0].id }}",
             "status": "error",
             "limit": 1
           }
         },
         "name": "Check Recent Errors",
         "type": "n8n-nodes-base.n8n",
         "typeVersion": 1,
         "position": [
           1250,
           400
         ],
         "credentials": {
           "n8nApi": "n8n-internal-api"
         }
       },
       {
         "parameters": {
           "conditions": {
             "number": [
               {
                 "value1": "={{ $json.length }}",
                 "operation": "larger",
                 "value2": 0
               }
             ]
           }
         },
         "name": "Has Errors?",
         "type": "n8n-nodes-base.if",
         "typeVersion": 1,
         "position": [
           1450,
           400
         ]
       },
       {
         "parameters": {
           "method": "POST",
           "url": "https://hooks.slack.com/services/YOUR_SLACK_WEBHOOK",
           "sendHeaders": true,
           "headerParameters": {
             "parameters": [
               {
                 "name": "Content-Type",
                 "value": "application/json"
               }
             ]
           },
           "sendBody": true,
           "bodyParameters": {
             "parameters": [
               {
                 "name": "text",
                 "value": "=Workflow Error: {{ $node[\"Split Workflows\"].json.workflow }} has failed executions. Please check n8n dashboard."
               }
             ]
           },
           "options": {}
         },
         "name": "Send Error Alert",
         "type": "n8n-nodes-base.httpRequest",
         "typeVersion": 1,
         "position": [
           1650,
           500
         ]
       },
       {
         "parameters": {
           "method": "POST",
           "url": "https://hooks.slack.com/services/YOUR_SLACK_WEBHOOK",
           "sendHeaders": true,
           "headerParameters": {
             "parameters": [
               {
                 "name": "Content-Type",
                 "value": "application/json"
               }
             ]
           },
           "sendBody": true,
           "bodyParameters": {
             "parameters": [
               {
                 "name": "text",
                 "value": "=Workflow Missing: {{ $node[\"Split Workflows\"].json.workflow }} was not found. Please check n8n dashboard."
               }
             ]
           },
           "options": {}
         },
         "name": "Send Missing Alert",
         "type": "n8n-nodes-base.httpRequest",
         "typeVersion": 1,
         "position": [
           1250,
           200
         ]
       }
     ],
     "connections": {
       "Schedule Trigger": {
         "main": [
           [
             {
               "node": "Prepare Workflow List",
               "type": "main",
               "index": 0
             }
           ]
         ]
       },
       "Prepare Workflow List": {
         "main": [
           [
             {
               "node": "Split Workflows",
               "type": "main",
               "index": 0
             }
           ]
         ]
       },
       "Split Workflows": {
         "main": [
           [
             {
               "node": "n8n",
               "type": "main",
               "index": 0
             }
           ]
         ]
       },
       "n8n": {
         "main": [
           [
             {
               "node": "Workflow Exists?",
               "type": "main",
               "index": 0
             }
           ]
         ]
       },
       "Workflow Exists?": {
         "main": [
           [
             {
               "node": "Send Missing Alert",
               "type": "main",
               "index": 0
             }
           ],
           [
             {
               "node": "Check Recent Errors",
               "type": "main",
               "index": 0
             }
           ]
         ]
       },
       "Check Recent Errors": {
         "main": [
           [
             {
               "node": "Has Errors?",
               "type": "main",
               "index": 0
             }
           ]
         ]
       },
       "Has Errors?": {
         "main": [
           [
             {
               "node": "Send Error Alert",
               "type": "main",
               "index": 0
             }
           ],
           []
         ]
       }
     }
   }
   ```

3. **Execution History Monitoring**:
   - Regularly review execution history
   - Look for patterns in failures
   - Monitor execution times for performance issues

## 4. Website and Frontend Monitoring

### Analytics Implementation
1. **Set Up Google Analytics or Plausible**:
   - Add tracking code to your website
   - Configure custom events for:
     - Subscription actions
     - Content engagement
     - User journeys

2. **Custom Event Tracking**:
   ```javascript
   // Example Google Analytics 4 event tracking
   function trackSubscriptionEvent(action, tier, value) {
     gtag('event', 'subscription_action', {
       'action': action,
       'tier': tier,
       'value': value
     });
   }

   // Track subscription signup
   trackSubscriptionEvent('signup', 'digital-devotee', 99);

   // Track subscription upgrade
   trackSubscriptionEvent('upgrade', 'opulence-oracle', 999);
   ```

3. **User Journey Tracking**:
   - Set up funnel visualization
   - Track conversion paths
   - Identify drop-off points

### Performance Monitoring
1. **Implement Web Vitals Tracking**:
   ```javascript
   // Web Vitals tracking
   import {getLCP, getFID, getCLS} from 'web-vitals';

   function sendToAnalytics({name, delta, id}) {
     // Send metrics to your analytics
     console.log({name, delta, id});
   }

   getCLS(sendToAnalytics);
   getFID(sendToAnalytics);
   getLCP(sendToAnalytics);
   ```

2. **Set Up Uptime Monitoring**:
   - Use a service like UptimeRobot or Pingdom
   - Configure alerts for downtime
   - Monitor response times

## 5. Subscription System Monitoring

### Key Metrics Dashboard
1. **Create Subscription Dashboard**:
   ```sql
   -- Create view for subscription metrics
   CREATE OR REPLACE VIEW subscription_metrics AS
   SELECT
     date_trunc('day', created_at) AS day,
     tier_id,
     COUNT(*) AS new_subscriptions,
     SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_subscriptions,
     SUM(CASE WHEN status = 'canceled' THEN 1 ELSE 0 END) AS canceled_subscriptions
   FROM subscriptions
   GROUP BY 1, 2
   ORDER BY 1 DESC, 2;
   ```

2. **Track Fluid Subscription Usage**:
   ```sql
   -- Create view for fluid subscription metrics
   CREATE OR REPLACE VIEW fluid_subscription_metrics AS
   SELECT
     date_trunc('day', created_at) AS day,
     SUM(banked_days) AS total_banked_days,
     COUNT(*) AS banking_transactions,
     AVG(banked_days) AS avg_banked_days
   FROM subscription_bank
   GROUP BY 1
   ORDER BY 1 DESC;
   ```

3. **Monitor Pod Usage**:
   ```sql
   -- Create view for pod metrics
   CREATE OR REPLACE VIEW pod_metrics AS
   SELECT
     p.tier_id,
     COUNT(DISTINCT p.id) AS total_pods,
     AVG((SELECT COUNT(*) FROM pod_members pm WHERE pm.pod_id = p.id)) AS avg_members_per_pod,
     COUNT(DISTINCT pm.user_id) AS total_pod_members
   FROM subscription_pods p
   LEFT JOIN pod_members pm ON p.id = pm.pod_id
   GROUP BY 1;
   ```

### Alerting System
1. **Set Up Subscription Alerts**:
   ```sql
   -- Create function to monitor subscription churn
   CREATE OR REPLACE FUNCTION alert_high_churn()
   RETURNS TRIGGER AS $$
   DECLARE
     recent_cancellations INTEGER;
     total_active INTEGER;
     churn_rate NUMERIC;
   BEGIN
     -- Count recent cancellations
     SELECT COUNT(*) INTO recent_cancellations
     FROM subscriptions
     WHERE status = 'canceled'
     AND updated_at > NOW() - INTERVAL '1 day';
     
     -- Count total active
     SELECT COUNT(*) INTO total_active
     FROM subscriptions
     WHERE status = 'active';
     
     -- Calculate churn rate
     IF total_active > 0 THEN
       churn_rate := recent_cancellations::NUMERIC / total_active::NUMERIC;
     ELSE
       churn_rate := 0;
     END IF;
     
     -- Alert if churn rate is high
     IF churn_rate > 0.05 THEN -- 5% daily churn threshold
       INSERT INTO system_alerts (
         alert_type,
         severity,
         message,
         timestamp
       ) VALUES (
         'high_churn',
         'critical',
         'High subscription churn rate detected: ' || (churn_rate * 100) || '%',
         NOW()
       );
     END IF;
     
     RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   -- Create trigger
   CREATE TRIGGER monitor_subscription_churn
   AFTER UPDATE ON subscriptions
   FOR EACH ROW
   WHEN (OLD.status = 'active' AND NEW.status = 'canceled')
   EXECUTE FUNCTION alert_high_churn();
   ```

## 6. Centralized Monitoring Dashboard

### Grafana Setup
1. **Install Grafana**:
   ```bash
   # Docker installation
   docker run -d -p 3000:3000 --name=grafana grafana/grafana-oss
   ```

2. **Configure Data Sources**:
   - Add Supabase PostgreSQL as a data source
   - Configure API data sources for Ghost and n8n
   - Set up Google Analytics data source

3. **Create Dashboards**:
   - System health dashboard
   - Content performance dashboard
   - Subscription metrics dashboard
   - User engagement dashboard

### Example Dashboard Configuration
```json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": 1,
  "links": [],
  "panels": [
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "PostgreSQL",
      "fieldConfig": {
        "defaults": {},
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "hiddenSeries": false,
      "id": 2,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "alertThreshold": true
      },
      "percentage": false,
      "pluginVersion": "7.5.5",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "format": "time_series",
          "group": [],
          "metricColumn": "none",
          "rawQuery": true,
          "rawSql": "SELECT\n  day as time,\n  new_subscriptions as value,\n  'New Subscriptions' as metric\nFROM subscription_metrics\nWHERE $__timeFilter(day)\nORDER BY 1",
          "refId": "A",
          "select": [
            [
              {
                "params": [
                  "value"
                ],
                "type": "column"
              }
            ]
          ],
          "timeColumn": "time",
          "where": [
            {
              "name": "$__timeFilter",
              "params": [],
              "type": "macro"
            }
          ]
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "New Subscriptions",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    }
  ],
  "refresh": "5m",
  "schemaVersion": 27,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-7d",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "Luxe Queer Subscription Dashboard",
  "uid": "luxequeer-subscriptions",
  "version": 1
}
```

## 7. Automated Health Checks

### Comprehensive Health Check Workflow
1. **Create n8n Workflow**:
   - Set up a workflow that runs every hour
   - Check all system components
   - Send notifications for any issues

2. **Components to Check**:
   - Ghost CMS API accessibility
   - Supabase database connectivity
   - Edge Function responsiveness
   - Website availability
   - n8n workflow status

3. **Example Health Check Code**:
   ```javascript
   // Health check function
   async function performHealthChecks() {
     const results = {
       ghost: await checkGhostCMS(),
       supabase: await checkSupabase(),
       edgeFunctions: await checkEdgeFunctions(),
       website: await checkWebsite(),
       n8n: await checkN8nWorkflows()
     };
     
     // Check for failures
     const failures = Object.entries(results)
       .filter(([_, status]) => status !== 'healthy')
       .map(([system, status]) => `${system}: ${status}`);
     
     if (failures.length > 0) {
       sendAlertNotification(failures);
     }
     
     // Log results
     logHealthCheckResults(results);
     
     return results;
   }
   
   // Check Ghost CMS
   async function checkGhostCMS() {
     try {
       const response = await fetch('https://rainbow-millipede.pikapod.net/ghost/api/v3/content/settings/', {
         headers: {
           'Content-Type': 'application/json'
         }
       });
       
       if (response.ok) {
         return 'healthy';
       } else {
         return `error: ${response.status}`;
       }
     } catch (error) {
       return `error: ${error.message}`;
     }
   }
   
   // Similar functions for other components...
   ```

## 8. Content Performance Monitoring

### Ghost Content Analytics
1. **Track Post Performance**:
   - Monitor views, reading time, and engagement
   - Compare performance across content categories
   - Identify top-performing content

2. **Email Newsletter Analytics**:
   - Track open rates and click-through rates
   - Monitor subscriber growth and engagement
   - Analyze content preferences

### Social Media Analytics
1. **Platform-Specific Metrics**:
   - Track engagement across all platforms
   - Monitor follower growth
   - Analyze content performance by platform

2. **Consolidated Social Dashboard**:
   - Aggregate metrics from all platforms
   - Compare performance across channels
   - Identify optimal posting strategies

## 9. Implementation Checklist

- [ ] Set up Ghost CMS email notifications
- [ ] Create Supabase monitoring tables and triggers
- [ ] Implement n8n monitoring workflow
- [ ] Set up analytics tracking on website
- [ ] Create subscription monitoring views
- [ ] Install and configure Grafana
- [ ] Implement automated health checks
- [ ] Set up content performance tracking
- [ ] Configure alerting systems
- [ ] Create documentation for monitoring procedures

## 10. Maintenance and Review

### Regular Maintenance
1. **Weekly Review**:
   - Check all monitoring dashboards
   - Review alerts and incidents
   - Update monitoring thresholds as needed

2. **Monthly Audit**:
   - Comprehensive system review
   - Performance optimization
   - Monitoring system updates

### Documentation
1. **Incident Response Plan**:
   - Document procedures for common issues
   - Define escalation paths
   - Create troubleshooting guides

2. **Monitoring System Documentation**:
   - Document all monitoring components
   - Create user guides for team members
   - Maintain configuration documentation

This comprehensive monitoring strategy ensures you'll have complete visibility into all aspects of your Luxe Queer magazine system, allowing you to proactively address issues, optimize performance, and track the success of your publication.
