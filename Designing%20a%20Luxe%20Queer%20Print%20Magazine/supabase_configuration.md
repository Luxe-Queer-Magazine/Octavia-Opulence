# Supabase Configuration for Luxe Queer Magazine

## Instance Details

**Supabase URL:** https://ovggshlfwumbtviwvbhi.supabase.co

## Database Schema Implementation

All tables and relationships described in the Supabase integration document should be implemented in this specific Supabase instance. The database schema includes:

- `profiles` - Extended user profile information
- `subscriptions` - Subscription details and status
- `subscription_tiers` - Tier definitions and features
- `transactions` - Payment and subscription change records
- `subscription_banks` - Fluid subscription banking records
- `subscription_pods` - Collective subscription pod configurations
- `pod_members` - Members of subscription pods
- `community_contributions` - Alternative subscription through contributions
- `events` - Exclusive events for higher-tier subscribers
- `nft_memberships` - Token-gated access records

## Authentication Configuration

The authentication system should be configured in this Supabase instance with:

1. Email authentication enabled
2. OAuth providers (Google, Apple, Twitter) for social login
3. Custom claims for subscription tier information
4. Row-level security policies for content access

## API Integration

All API calls from Ghost CMS, n8n, and frontend components should use this specific Supabase URL:

```javascript
// Example Supabase client initialization
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://ovggshlfwumbtviwvbhi.supabase.co'
const supabaseKey = 'your-supabase-key'
const supabase = createClient(supabaseUrl, supabaseKey)
```

## n8n Workflow Integration

Update all n8n workflows to use this Supabase URL in HTTP Request nodes and Supabase nodes:

```json
{
  "parameters": {
    "url": "https://ovggshlfwumbtviwvbhi.supabase.co/rest/v1/subscriptions",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "supabaseApi",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "apikey",
          "value": "={{ $credentials.supabaseApi.apiKey }}"
        },
        {
          "name": "Authorization",
          "value": "Bearer={{ $credentials.supabaseApi.apiKey }}"
        }
      ]
    }
  }
}
```

## Implementation Steps

1. **Create Project:**
   - Confirm the project is already created at https://ovggshlfwumbtviwvbhi.supabase.co
   - If not, create a new project with this URL

2. **Database Setup:**
   - Execute the SQL scripts provided in the Supabase integration document
   - Create all necessary tables, indexes, and relationships
   - Implement row-level security policies

3. **Authentication Configuration:**
   - Configure authentication providers
   - Set up email templates for authentication flows
   - Create custom claims and hooks

4. **API Keys:**
   - Generate and securely store API keys
   - Configure service roles with appropriate permissions
   - Update all integration code with the correct keys

5. **Testing:**
   - Test database operations
   - Verify authentication flows
   - Confirm API access from Ghost CMS and n8n

## Security Considerations

1. **API Key Management:**
   - Store API keys securely
   - Use environment variables for sensitive data
   - Implement proper key rotation procedures

2. **Row-Level Security:**
   - Implement RLS policies for all tables
   - Test security policies thoroughly
   - Ensure proper access control for subscription content

3. **Data Encryption:**
   - Enable column encryption for sensitive data
   - Use secure connections for all API calls
   - Implement proper backup and recovery procedures

## Monitoring and Maintenance

1. **Performance Monitoring:**
   - Set up database performance monitoring
   - Track API usage and response times
   - Implement alerting for potential issues

2. **Backup Strategy:**
   - Configure regular database backups
   - Test restoration procedures
   - Document disaster recovery process

3. **Updates and Maintenance:**
   - Keep Supabase instance updated
   - Monitor for security patches
   - Schedule regular maintenance windows

## Integration Verification

After implementing the Supabase configuration, verify the integration with:

1. **Ghost CMS Integration Test:**
   - Confirm data flow between Ghost and Supabase
   - Test subscription status synchronization
   - Verify content access control

2. **n8n Workflow Test:**
   - Run test workflows for each automation
   - Verify data processing and transformation
   - Confirm proper error handling

3. **Frontend Integration Test:**
   - Test user authentication flows
   - Verify subscription management features
   - Confirm fluid subscription functionality

This configuration ensures that all components of the Luxe Queer magazine system are properly integrated with the specific Supabase instance at https://ovggshlfwumbtviwvbhi.supabase.co.
