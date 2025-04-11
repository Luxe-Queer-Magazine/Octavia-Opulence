# n8n Workflow Automation for Luxe Queer Magazine

## Introduction

This document provides comprehensive documentation for implementing workflow automation for Luxe Queer magazine using n8n. By integrating n8n with Ghost CMS and Supabase, we can automate various processes related to content publishing, subscription management, social media distribution, and print production.

## Authentication and Setup

### API Credentials

**n8n API Key:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ZjcyOGQ2YS0wMGUzLTQ4YTgtYTk2NS0zODBjZWIxYWNjYmQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzQzODU1MDc1LCJleHAiOjE3NDY0MTc2MDB9.lhT_Q6hMnFZKEg0twL1WhLU3RF2YmEucyQhMiDkg7qY
```

**Ghost CMS Credentials:**
- URL: `https://rainbow-millipede.pikapod.net`
- Admin API Key: `67ef67107bdbb900014522e2:a83281ff2c5c9eb4ee94242f87cd1e8ace9d4cb9317358acda25f8ec1f266d73`
- Content API Key: `bbc75241a46836b87673d05b12`
- API Version: `v3`

**Supabase Credentials:**
- Configure in n8n with your Supabase project URL and API key

### Initial Setup

1. **Install n8n:**
   ```bash
   npm install n8n -g
   ```

2. **Start n8n:**
   ```bash
   n8n start
   ```

3. **Access the n8n Dashboard:**
   - Open your browser and navigate to `http://localhost:5678`
   - Log in with your credentials

4. **Configure Credentials:**
   - Go to Settings > Credentials
   - Add Ghost API credentials
   - Add Supabase credentials
   - Add other necessary credentials (Stripe, social media platforms, etc.)

## Core Workflows

### 1. AI Content Creation and Publishing Workflow

This workflow automates the process of generating content with AI agents and publishing it to Ghost CMS.

**Workflow Steps:**

1. **Trigger: Schedule**
   - Configure to run on a regular schedule (e.g., weekly for content planning)

2. **HTTP Request: Fetch Content Brief**
   - Fetch content brief from Supabase or external system

3. **AI Agent Orchestration**
   - HTTP Request to each AI agent API with content brief
   - Configure for each AI provider (Cohere, Anthropic, Nvidia, etc.)
   - Example for Anthropic Claude:
     ```json
     {
       "url": "https://api.anthropic.com/v1/messages",
       "method": "POST",
       "headers": {
         "x-api-key": "{{$node['Credentials'].json.anthropicApiKey}}",
         "content-type": "application/json"
       },
       "body": {
         "model": "claude-3-opus-20240229",
         "max_tokens": 4000,
         "messages": [
           {
             "role": "user",
             "content": "Create an article for Luxe Queer magazine on {{$node['Content Brief'].json.topic}}. Focus on {{$node['Content Brief'].json.angle}} with a luxury perspective. Use the Octavia Opulence³ brand voice that balances sophistication with sass and incorporates references to queer culture."
           }
         ]
       }
     }
     ```

4. **Content Aggregation and Editing**
   - Function node to combine AI outputs
   - Apply editorial guidelines and formatting
   - Example function:
     ```javascript
     // Combine content from multiple AI agents
     const combinedContent = {
       title: $input.item(0).json.title,
       introduction: $input.item(1).json.content.substring(0, 500),
       mainContent: $input.item(2).json.content,
       conclusion: $input.item(3).json.content.substring($input.item(3).json.content.length - 500),
       attribution: `This article was created collaboratively by the Luxe Queer AI agent team, featuring contributions from ${$input.item(0).json.agent}, ${$input.item(1).json.agent}, ${$input.item(2).json.agent}, and ${$input.item(3).json.agent}.`
     };
     
     // Format according to Ghost CMS requirements
     const formattedContent = `
     # ${combinedContent.title}
     
     ${combinedContent.introduction}
     
     ${combinedContent.mainContent}
     
     ${combinedContent.conclusion}
     
     ---
     
     ${combinedContent.attribution}
     `;
     
     return {json: {formattedContent}};
     ```

5. **Ghost CMS: Create Draft Post**
   - Use Ghost node to create a draft post
   - Configure with:
     - Title from AI output
     - Content from aggregated AI content
     - Tags based on content category
     - Featured image (placeholder or AI-generated)

6. **Notification: Editorial Review**
   - Send email notification to editorial team
   - Include link to draft post for review

7. **Wait: Editorial Approval**
   - Webhook trigger for editorial approval
   - Continue workflow when approved

8. **Ghost CMS: Update Post Status**
   - Update post status to "published"
   - Schedule publication date if needed

9. **Supabase: Update Content Tracking**
   - Record publication in Supabase database
   - Track AI agent contributions and performance

**Example n8n Workflow JSON:**
```json
{
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "days",
              "minutesInterval": 1,
              "hoursInterval": 1
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
        "url": "https://your-supabase-url.supabase.co/rest/v1/content_briefs?select=*&order=created_at.desc&limit=1",
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
      },
      "name": "Fetch Content Brief",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [
        450,
        300
      ]
    },
    // Additional nodes would follow
  ],
  "connections": {
    "Schedule Trigger": {
      "main": [
        [
          {
            "node": "Fetch Content Brief",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
    // Additional connections would follow
  }
}
```

### 2. Subscription Management Workflow

This workflow automates the synchronization of subscription data between Ghost CMS, Supabase, and payment processors.

**Workflow Steps:**

1. **Trigger: Webhook from Stripe**
   - Configure to receive Stripe webhook events
   - Filter for subscription-related events

2. **Switch: Event Type**
   - Branch based on event type (created, updated, canceled, etc.)

3. **Function: Process Subscription Data**
   - Extract relevant data from webhook payload
   - Format for database storage
   - Example function:
     ```javascript
     // Extract subscription data from Stripe webhook
     const event = $input.item(0).json;
     const subscription = event.data.object;
     
     // Format for database
     const subscriptionData = {
       stripe_subscription_id: subscription.id,
       customer_id: subscription.customer,
       status: subscription.status,
       tier: subscription.metadata.tier_slug,
       current_period_start: new Date(subscription.current_period_start * 1000).toISOString(),
       current_period_end: new Date(subscription.current_period_end * 1000).toISOString(),
       cancel_at_period_end: subscription.cancel_at_period_end,
       amount: subscription.items.data[0].price.unit_amount / 100,
       currency: subscription.currency,
       event_type: event.type
     };
     
     return {json: subscriptionData};
     ```

4. **Supabase: Update Subscription**
   - Update subscription data in Supabase
   - Use upsert operation to handle new and existing subscriptions

5. **Ghost CMS: Update Member**
   - Update member status and labels in Ghost CMS
   - Sync subscription tier information

6. **Conditional: Tier Change**
   - Check if subscription tier has changed
   - If yes, trigger tier change workflow

7. **Supabase: Log Transaction**
   - Record transaction details in Supabase
   - Include payment information and subscription changes

8. **Email: Send Confirmation**
   - Send appropriate email based on event type
   - Include subscription details and next steps

**Example n8n Workflow JSON (Partial):**
```json
{
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "stripe-webhook",
        "options": {}
      },
      "name": "Stripe Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [
        250,
        300
      ]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.type }}",
              "operation": "contains",
              "value2": "customer.subscription"
            }
          ]
        }
      },
      "name": "Is Subscription Event?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [
        450,
        300
      ]
    }
    // Additional nodes would follow
  ],
  "connections": {
    "Stripe Webhook": {
      "main": [
        [
          {
            "node": "Is Subscription Event?",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
    // Additional connections would follow
  }
}
```

### 3. Social Media Distribution Workflow

This workflow automates the distribution of content to various social media platforms when new content is published.

**Workflow Steps:**

1. **Trigger: Ghost CMS Webhook**
   - Configure to trigger when a post is published
   - Filter for published status

2. **Ghost CMS: Get Post Details**
   - Fetch complete post details including content and images
   - Extract metadata and tags

3. **Function: Generate Platform-Specific Content**
   - Create tailored content for each social platform
   - Apply character limits and formatting
   - Example function:
     ```javascript
     // Get post data
     const post = $input.item(0).json;
     
     // Generate platform-specific content
     const platformContent = {
       twitter: {
         text: `${post.title} | The category is: EXCELLENCE. Read more on Luxe Queer Magazine. #LuxeQueer #${post.primary_tag.slug.replace(/-/g, '')}`,
         url: post.url,
         image: post.feature_image
       },
       instagram: {
         caption: `${post.title}\n\n${post.excerpt.substring(0, 200)}...\n\nThe category is: EXCELLENCE. 💜\n\nRead the full article on Luxe Queer Magazine (link in bio).\n\n#LuxeQueer #${post.primary_tag.slug.replace(/-/g, '')} #LuxuryLifestyle #QueerExcellence`,
         image: post.feature_image
       },
       linkedin: {
         title: post.title,
         text: `${post.excerpt}\n\nRead the full article on Luxe Queer Magazine.`,
         url: post.url,
         image: post.feature_image
       }
       // Add other platforms as needed
     };
     
     return {json: platformContent};
     ```

4. **Switch: Platform Distribution**
   - Branch for each social media platform

5. **HTTP Request: Twitter/X Post**
   - Post to Twitter/X API
   - Include image if available

6. **HTTP Request: Instagram Post**
   - Post to Instagram API
   - Format as carousel if multiple images

7. **HTTP Request: LinkedIn Post**
   - Post to LinkedIn API
   - Include professional context

8. **HTTP Request: Other Platforms**
   - Additional branches for other platforms
   - Customize content for each

9. **Supabase: Log Distribution**
   - Record distribution details in Supabase
   - Track engagement metrics if available

10. **Notification: Distribution Report**
    - Send summary of distribution to team
    - Include links to posts

### 4. Print Issue Preparation Workflow

This workflow automates the preparation of content for print issues of the magazine.

**Workflow Steps:**

1. **Trigger: Manual or Scheduled**
   - Configure to run on issue preparation schedule
   - Allow manual triggering for special issues

2. **Ghost CMS: Get Issue Content**
   - Fetch all posts with specific issue tag
   - Sort by section and priority

3. **Function: Organize Content Structure**
   - Arrange content according to magazine structure
   - Generate table of contents
   - Example function:
     ```javascript
     // Get all posts for the issue
     const posts = $input.item(0).json;
     
     // Organize by section
     const sections = {
       fashion: posts.filter(post => post.tags.some(tag => tag.slug === 'fashion')),
       art: posts.filter(post => post.tags.some(tag => tag.slug === 'art')),
       culture: posts.filter(post => post.tags.some(tag => tag.slug === 'culture')),
       travel: posts.filter(post => post.tags.some(tag => tag.slug === 'travel')),
       technology: posts.filter(post => post.tags.some(tag => tag.slug === 'technology')),
       luxury: posts.filter(post => post.tags.some(tag => tag.slug === 'luxury'))
     };
     
     // Generate table of contents
     const toc = Object.entries(sections).map(([section, posts]) => {
       return {
         section: section.toUpperCase(),
         articles: posts.map(post => ({
           title: post.title,
           author: post.primary_author.name,
           page: 0 // To be filled later
         }))
       };
     });
     
     return {json: {sections, toc}};
     ```

4. **HTTP Request: Generate PDFs**
   - Call PDF generation service for each article
   - Apply print templates and styling

5. **Function: Combine PDFs**
   - Merge individual PDFs into complete issue
   - Add pagination and references

6. **HTTP Request: Send to InDesign**
   - Prepare package for InDesign
   - Include assets and layout information

7. **Supabase: Update Issue Status**
   - Record issue preparation status
   - Track included content and metadata

8. **Notification: Print Ready**
   - Notify production team of print-ready issue
   - Include links to final files

### 5. Email Marketing Automation Workflow

This workflow automates email communications with subscribers based on their tier and engagement.

**Workflow Steps:**

1. **Trigger: Schedule or Event**
   - Configure to run on schedule for newsletters
   - Trigger on specific events (new issue, subscription change)

2. **Supabase: Get Subscriber Segments**
   - Fetch subscriber lists by tier and preferences
   - Filter for active subscriptions

3. **Ghost CMS: Get Content**
   - Fetch relevant content for email
   - Filter based on subscriber tier

4. **Function: Personalize Content**
   - Customize content for each subscriber segment
   - Apply tier-specific offerings
   - Example function:
     ```javascript
     // Get subscriber segment and content
     const segment = $input.item(0).json;
     const content = $input.item(1).json;
     
     // Personalize based on tier
     const tierContent = {
       'digital-devotee': {
         heading: 'Digital Exclusives for You',
         features: content.filter(item => item.tier <= 1).slice(0, 3),
         cta: 'Read More Online'
       },
       'print-provocateur': {
         heading: 'Your Print Edition is On the Way',
         features: content.filter(item => item.tier <= 2).slice(0, 5),
         cta: 'Preview Online Now'
       },
       'opulence-oracle': {
         heading: 'Exclusive Oracle Insights',
         features: content.filter(item => item.tier <= 3),
         cta: 'Access Your Premium Content',
         special: 'Your quarterly gift selection is now available'
       },
       'category-excellence': {
         heading: 'Excellence Awaits',
         features: content,
         cta: 'Access Your Exclusive Content',
         special: 'Your invitation to our next retreat is enclosed'
       }
     };
     
     const emailContent = tierContent[segment.tier] || tierContent['digital-devotee'];
     
     return {json: {segment, emailContent}};
     ```

5. **HTTP Request: Email Service**
   - Send emails via email service API
   - Include personalized content and links

6. **Supabase: Log Email Activity**
   - Record email sends in Supabase
   - Track open and click rates when available

7. **Wait: Engagement Window**
   - Pause workflow for engagement window
   - Continue for follow-up actions

8. **Conditional: Engagement Check**
   - Check if subscriber engaged with email
   - Branch based on engagement status

9. **HTTP Request: Follow-up Email**
   - Send follow-up to non-engaged subscribers
   - Include alternative content or offers

## Advanced Workflows

### 1. AI Agent Team Coordination Workflow

This workflow manages the coordination between different AI agents for content creation.

**Workflow Steps:**

1. **Trigger: Content Request**
   - Receive content request with specifications
   - Parse requirements and content type

2. **Function: Agent Assignment**
   - Determine optimal AI agents for the content
   - Assign specific sections to each agent
   - Example function:
     ```javascript
     // Content request details
     const request = $input.item(0).json;
     
     // Agent specialties
     const agents = {
       cohere: ['cultural analysis', 'trend forecasting'],
       anthropic: ['long-form narrative', 'ethical perspectives'],
       nvidia: ['visual descriptions', 'technical content'],
       hermes: ['luxury expertise', 'fashion commentary'],
       hume: ['emotional resonance', 'personal narratives'],
       mistral: ['data analysis', 'research synthesis'],
       gemma: ['concise summaries', 'practical advice'],
       huggingface: ['multilingual content', 'diverse perspectives'],
       llama: ['creative concepts', 'innovative angles']
     };
     
     // Match content needs with agent specialties
     const contentNeeds = request.content_type.split(',').map(item => item.trim().toLowerCase());
     
     const assignments = {};
     contentNeeds.forEach(need => {
       const matchingAgents = Object.entries(agents).filter(([agent, specialties]) => 
         specialties.some(specialty => need.includes(specialty))
       ).map(([agent]) => agent);
       
       if (matchingAgents.length > 0) {
         assignments[need] = matchingAgents[0]; // Assign to first matching agent
       } else {
         assignments[need] = 'anthropic'; // Default to Anthropic for unmatched needs
       }
     });
     
     return {json: {assignments, request}};
     ```

3. **HTTP Request: Agent APIs**
   - Parallel requests to each assigned AI agent
   - Include specific instructions for each

4. **Wait: Agent Responses**
   - Collect responses from all agents
   - Handle timeouts and retries

5. **Function: Content Integration**
   - Combine outputs from different agents
   - Ensure consistent voice and flow

6. **HTTP Request: Editorial Review**
   - Send to human editor for review
   - Include agent attribution and notes

7. **Conditional: Revision Needed**
   - Check if revisions are requested
   - Branch based on revision status

8. **HTTP Request: Agent Revisions**
   - Send revision requests to specific agents
   - Include editor feedback and guidelines

9. **Function: Finalize Content**
   - Incorporate revisions and finalize
   - Format for publication platform

### 2. Fluid Subscription Management Workflow

This workflow manages the innovative fluid subscription features, including banking days and subscription pods.

**Workflow Steps:**

1. **Trigger: Subscription Action**
   - Receive action request (bank, gift, pod)
   - Validate user and action type

2. **Switch: Action Type**
   - Branch based on action type
   - Handle each action with specific logic

3. **Function: Process Banking Request**
   - Calculate days to bank
   - Update subscription status
   - Example function:
     ```javascript
     // Banking request details
     const request = $input.item(0).json;
     
     // Calculate days to bank
     const startDate = new Date();
     const endDate = new Date(request.end_date);
     const daysDifference = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
     
     // Validate request
     if (daysDifference <= 0) {
       return {json: {success: false, error: 'Invalid date range'}};
     }
     
     // Prepare banking data
     const bankingData = {
       user_id: request.user_id,
       banked_days: daysDifference,
       reason: request.reason || 'User requested',
       start_date: startDate.toISOString(),
       end_date: endDate.toISOString(),
       expires_at: new Date(startDate.getTime() + 365 * 24 * 60 * 60 * 1000).toISOString() // 1 year expiry
     };
     
     return {json: {success: true, bankingData}};
     ```

4. **Supabase: Update Subscription Bank**
   - Record banked days in Supabase
   - Update subscription status

5. **Function: Process Gift Request**
   - Validate gift recipient
   - Calculate gift duration

6. **Supabase: Update Gift Recipient**
   - Add subscription time to recipient
   - Record gift transaction

7. **Function: Process Pod Request**
   - Manage pod creation or updates
   - Validate pod membership

8. **Supabase: Update Pod Configuration**
   - Update pod details in Supabase
   - Manage pod member access

9. **Notification: Action Confirmation**
   - Send confirmation to user
   - Include action details and next steps

### 3. Content Analytics and Optimization Workflow

This workflow collects and analyzes content performance data to optimize future content.

**Workflow Steps:**

1. **Trigger: Schedule**
   - Run weekly for regular analysis
   - Additional runs after issue publication

2. **Ghost CMS: Get Content Performance**
   - Fetch view and engagement metrics
   - Filter by date range and content type

3. **Supabase: Get Subscription Data**
   - Fetch subscription conversions
   - Link to content engagement

4. **HTTP Request: Social Media Analytics**
   - Collect performance data from social platforms
   - Aggregate engagement metrics

5. **Function: Performance Analysis**
   - Calculate key performance indicators
   - Identify trends and patterns
   - Example function:
     ```javascript
     // Collect data from various sources
     const ghostData = $input.item(0).json;
     const subscriptionData = $input.item(1).json;
     const socialData = $input.item(2).json;
     
     // Calculate content performance metrics
     const contentPerformance = ghostData.map(post => {
       // Find related subscription conversions
       const relatedConversions = subscriptionData.filter(sub => 
         sub.referrer_url.includes(post.slug)
       );
       
       // Find social engagement
       const socialEngagement = socialData.filter(item => 
         item.url.includes(post.slug)
       );
       
       // Calculate metrics
       const conversionRate = post.views > 0 ? (relatedConversions.length / post.views) * 100 : 0;
       const socialEngagementRate = socialEngagement.reduce((sum, item) => sum + item.engagement, 0) / post.views;
       
       return {
         title: post.title,
         slug: post.slug,
         views: post.views,
         reading_time: post.reading_time,
         conversions: relatedConversions.length,
         conversion_rate: conversionRate,
         social_shares: socialEngagement.length,
         social_engagement: socialEngagement.reduce((sum, item) => sum + item.engagement, 0),
         social_engagement_rate: socialEngagementRate,
         tags: post.tags.map(tag => tag.name),
         published_at: post.published_at
       };
     });
     
     // Identify top performing content
     const topContent = [...contentPerformance].sort((a, b) => b.conversion_rate - a.conversion_rate).slice(0, 5);
     
     // Identify content patterns
     const tagPerformance = {};
     contentPerformance.forEach(post => {
       post.tags.forEach(tag => {
         if (!tagPerformance[tag]) {
           tagPerformance[tag] = {
             views: 0,
             conversions: 0,
             posts: 0
           };
         }
         tagPerformance[tag].views += post.views;
         tagPerformance[tag].conversions += post.conversions;
         tagPerformance[tag].posts += 1;
       });
     });
     
     Object.keys(tagPerformance).forEach(tag => {
       tagPerformance[tag].conversion_rate = tagPerformance[tag].views > 0 ? 
         (tagPerformance[tag].conversions / tagPerformance[tag].views) * 100 : 0;
       tagPerformance[tag].average_views = tagPerformance[tag].views / tagPerformance[tag].posts;
     });
     
     return {json: {contentPerformance, topContent, tagPerformance}};
     ```

6. **Function: Generate Recommendations**
   - Create content recommendations
   - Suggest optimization strategies

7. **Supabase: Store Analysis Results**
   - Save analysis data for historical tracking
   - Update content performance metrics

8. **HTTP Request: Create Report**
   - Generate PDF or dashboard report
   - Format for editorial team review

9. **Email: Send Analysis Report**
   - Send report to editorial team
   - Include key insights and recommendations

## Integration with External Systems

### 1. Stripe Integration

Configure n8n to work with Stripe for subscription payments:

```javascript
// Example Stripe webhook handling in n8n
function processStripeWebhook(webhook) {
  const event = webhook.body;
  
  switch (event.type) {
    case 'customer.subscription.created':
    case 'customer.subscription.updated':
      return {
        operation: 'upsert',
        table: 'subscriptions',
        data: {
          stripe_id: event.data.object.id,
          customer_id: event.data.object.customer,
          status: event.data.object.status,
          current_period_end: new Date(event.data.object.current_period_end * 1000).toISOString(),
          tier: event.data.object.metadata.tier_slug || 'digital-devotee'
        },
        key: 'stripe_id'
      };
      
    case 'customer.subscription.deleted':
      return {
        operation: 'update',
        table: 'subscriptions',
        data: {
          stripe_id: event.data.object.id,
          status: 'canceled',
          canceled_at: new Date().toISOString()
        },
        key: 'stripe_id'
      };
      
    case 'invoice.payment_succeeded':
      return {
        operation: 'insert',
        table: 'transactions',
        data: {
          stripe_invoice_id: event.data.object.id,
          customer_id: event.data.object.customer,
          amount: event.data.object.amount_paid / 100,
          currency: event.data.object.currency,
          status: 'succeeded',
          date: new Date(event.data.object.created * 1000).toISOString()
        }
      };
      
    case 'invoice.payment_failed':
      return {
        operation: 'insert',
        table: 'transactions',
        data: {
          stripe_invoice_id: event.data.object.id,
          customer_id: event.data.object.customer,
          amount: event.data.object.amount_due / 100,
          currency: event.data.object.currency,
          status: 'failed',
          date: new Date(event.data.object.created * 1000).toISOString()
        }
      };
      
    default:
      return null;
  }
}
```

### 2. Social Media API Integration

Configure n8n to work with various social media APIs:

```javascript
// Example Twitter/X API integration
const twitterPost = {
  url: 'https://api.twitter.com/2/tweets',
  method: 'POST',
  authentication: 'oauth2',
  headers: {
    'Content-Type': 'application/json'
  },
  body: {
    text: `${post.title} | The category is: EXCELLENCE. Read more on Luxe Queer Magazine. #LuxeQueer #${post.primary_tag.slug.replace(/-/g, '')}`,
    media: {
      media_ids: ['{{ $node["Upload Media"].json.media_id }}']
    }
  }
};

// Example Instagram API integration
const instagramPost = {
  url: 'https://graph.facebook.com/v16.0/{{ $credentials.instagramBusinessAccount }}/media',
  method: 'POST',
  authentication: 'oauth2',
  headers: {
    'Content-Type': 'application/json'
  },
  body: {
    image_url: post.feature_image,
    caption: `${post.title}\n\n${post.excerpt.substring(0, 200)}...\n\nThe category is: EXCELLENCE. 💜\n\nRead the full article on Luxe Queer Magazine (link in bio).\n\n#LuxeQueer #${post.primary_tag.slug.replace(/-/g, '')} #LuxuryLifestyle #QueerExcellence`
  }
};
```

### 3. Email Service Integration

Configure n8n to work with email service providers:

```javascript
// Example email service integration
const emailConfig = {
  url: 'https://api.sendgrid.com/v3/mail/send',
  method: 'POST',
  authentication: 'headerAuth',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {{ $credentials.sendgridApi.apiKey }}'
  },
  body: {
    personalizations: [
      {
        to: [
          {
            email: '{{ $json.email }}'
          }
        ],
        dynamic_template_data: {
          first_name: '{{ $json.first_name }}',
          tier: '{{ $json.tier }}',
          content_items: '{{ $json.content_items }}',
          special_offer: '{{ $json.special_offer }}'
        }
      }
    ],
    from: {
      email: 'editor@luxequeer.com',
      name: 'Luxe Queer Magazine'
    },
    template_id: '{{ $json.template_id }}'
  }
};
```

## Deployment and Maintenance

### Hosting Options

1. **Self-hosted n8n:**
   - Deploy on your own server
   - Configure with PM2 for process management
   - Set up SSL for secure connections

2. **n8n Cloud:**
   - Use n8n's managed cloud service
   - Simplifies maintenance and updates
   - Provides built-in monitoring

3. **Docker Deployment:**
   - Use Docker for containerized deployment
   - Example docker-compose.yml:
     ```yaml
     version: '3'
     
     services:
       n8n:
         image: n8nio/n8n
         restart: always
         ports:
           - "5678:5678"
         environment:
           - N8N_BASIC_AUTH_ACTIVE=true
           - N8N_BASIC_AUTH_USER=admin
           - N8N_BASIC_AUTH_PASSWORD=securepassword
           - N8N_HOST=n8n.yourdomain.com
           - N8N_PORT=5678
           - N8N_PROTOCOL=https
           - N8N_ENCRYPTION_KEY=your-secret-encryption-key
           - NODE_ENV=production
         volumes:
           - n8n_data:/home/node/.n8n
     
     volumes:
       n8n_data:
     ```

### Security Considerations

1. **API Key Management:**
   - Store API keys securely in n8n credentials
   - Rotate keys regularly
   - Use environment variables for sensitive data

2. **Access Control:**
   - Implement proper authentication for n8n
   - Restrict access to authorized users only
   - Use HTTPS for all connections

3. **Webhook Security:**
   - Validate webhook signatures
   - Implement rate limiting
   - Filter requests by IP when possible

### Monitoring and Maintenance

1. **Workflow Monitoring:**
   - Set up execution monitoring
   - Configure error notifications
   - Track execution times and performance

2. **Regular Backups:**
   - Back up workflow configurations
   - Export workflows regularly
   - Store backups securely

3. **Version Control:**
   - Export workflows to JSON
   - Store in version control system
   - Document changes and updates

## Conclusion

This n8n workflow automation documentation provides a comprehensive framework for implementing automated processes for Luxe Queer magazine. By integrating Ghost CMS, Supabase, and various external services, these workflows streamline content creation, subscription management, social media distribution, print production, and analytics.

The modular approach allows for easy maintenance and extension as the magazine's needs evolve. Each workflow can be implemented independently and integrated with others as needed, providing flexibility and scalability.

By implementing these workflows, Luxe Queer magazine will benefit from:

1. **Increased Efficiency:** Automating repetitive tasks and streamlining processes
2. **Improved Consistency:** Ensuring consistent handling of subscriptions and content
3. **Enhanced Analytics:** Gathering and analyzing performance data automatically
4. **Seamless Integration:** Connecting various systems and services into a cohesive ecosystem
5. **Scalable Operations:** Supporting growth with automated workflows that scale

The n8n platform provides the flexibility and power needed to implement these sophisticated workflows while maintaining ease of use and adaptability for future requirements.
