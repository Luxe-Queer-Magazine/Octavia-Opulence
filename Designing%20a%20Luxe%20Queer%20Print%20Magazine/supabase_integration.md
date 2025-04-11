# Supabase Integration for Luxe Queer Magazine Subscription Model

## Introduction

This technical implementation plan outlines how to integrate Supabase with Ghost CMS to power the innovative subscription model for Luxe Queer magazine. Supabase will serve as the backend database and authentication system, providing robust user management, real-time capabilities, and secure content access control.

## Architecture Overview

The integration architecture consists of:

1. **Ghost CMS**: Content management and publishing platform
2. **Supabase**: Backend database, authentication, storage, and serverless functions
3. **Integration Layer**: Custom API and webhooks connecting Ghost and Supabase
4. **Frontend Applications**: Web, mobile, and other client interfaces

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Ghost CMS      │◄────┤  Integration    │◄────┤  Supabase       │
│  (Content)      │     │  Layer          │     │  (Users/Data)   │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         ▲                                               ▲
         │                                               │
         │                                               │
         ▼                                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                     Frontend Applications                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Supabase Implementation

### 1. Project Setup

```sql
-- Create a new Supabase project for Luxe Queer
-- Configure project settings:
--   - Region: Select based on primary audience location
--   - Database password: Generate strong password
--   - Pricing plan: Pro (for production) or Free (for development)
```

### 2. Database Schema

```sql
-- Users Table (extends Supabase auth.users)
CREATE TABLE public.profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  first_name TEXT,
  last_name TEXT,
  display_name TEXT,
  avatar_url TEXT,
  subscription_tier TEXT NOT NULL DEFAULT 'none',
  subscription_status TEXT NOT NULL DEFAULT 'inactive',
  subscription_start_date TIMESTAMP WITH TIME ZONE,
  subscription_end_date TIMESTAMP WITH TIME ZONE,
  billing_frequency TEXT,
  billing_amount DECIMAL(10,2),
  currency TEXT DEFAULT 'USD',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Subscription Tiers Table
CREATE TABLE public.subscription_tiers (
  id SERIAL PRIMARY KEY,
  tier_name TEXT UNIQUE NOT NULL,
  tier_slug TEXT UNIQUE NOT NULL,
  monthly_price DECIMAL(10,2) NOT NULL,
  annual_price DECIMAL(10,2) NOT NULL,
  description TEXT NOT NULL,
  features JSONB NOT NULL,
  is_active BOOLEAN DEFAULT true,
  max_members INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Insert initial subscription tiers
INSERT INTO public.subscription_tiers (tier_name, tier_slug, monthly_price, annual_price, description, features)
VALUES 
  ('Digital Devotee', 'digital-devotee', 9.99, 99.00, 'Digital access to all magazine content', '{"digital_access": true, "print_access": false, "events": ["monthly_digital"]}'),
  ('Print Provocateur', 'print-provocateur', 24.99, 249.00, 'Print and digital access with enhanced benefits', '{"digital_access": true, "print_access": true, "events": ["monthly_digital", "quarterly_virtual"]}'),
  ('Opulence Oracle', 'opulence-oracle', 99.99, 999.00, 'Premium access with quarterly luxury gifts', '{"digital_access": true, "print_access": true, "limited_edition": true, "quarterly_gift": true, "events": ["monthly_digital", "quarterly_virtual", "biannual_inperson"]}'),
  ('Category Excellence', 'category-excellence', 0, 4999.00, 'Ultimate luxury membership with exclusive access', '{"digital_access": true, "print_access": true, "limited_edition": true, "quarterly_gift": true, "annual_retreat": true, "concierge": true, "events": ["monthly_digital", "quarterly_virtual", "biannual_inperson", "private_dinners"]}');

-- Subscription Transactions Table
CREATE TABLE public.subscription_transactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  tier_id INTEGER REFERENCES public.subscription_tiers(id) NOT NULL,
  transaction_type TEXT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  currency TEXT DEFAULT 'USD',
  payment_method TEXT,
  payment_id TEXT,
  status TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Subscription Benefits Usage Table
CREATE TABLE public.benefits_usage (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  benefit_type TEXT NOT NULL,
  benefit_details JSONB,
  used_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  expires_at TIMESTAMP WITH TIME ZONE
);

-- Fluid Subscription Bank Table
CREATE TABLE public.subscription_bank (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  banked_days INTEGER NOT NULL,
  reason TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  expires_at TIMESTAMP WITH TIME ZONE
);

-- Subscription Pods Table
CREATE TABLE public.subscription_pods (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pod_name TEXT NOT NULL,
  tier_id INTEGER REFERENCES public.subscription_tiers(id) NOT NULL,
  primary_member_id UUID REFERENCES auth.users(id) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Pod Members Table
CREATE TABLE public.pod_members (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pod_id UUID REFERENCES public.subscription_pods(id) NOT NULL,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  role TEXT NOT NULL DEFAULT 'member',
  joined_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Community Contributions Table
CREATE TABLE public.community_contributions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  contribution_type TEXT NOT NULL,
  description TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  credit_amount INTEGER,
  approved_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Events Table
CREATE TABLE public.events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  event_type TEXT NOT NULL,
  start_time TIMESTAMP WITH TIME ZONE NOT NULL,
  end_time TIMESTAMP WITH TIME ZONE NOT NULL,
  location JSONB,
  max_attendees INTEGER,
  required_tier TEXT,
  is_public BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Event Registrations Table
CREATE TABLE public.event_registrations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_id UUID REFERENCES public.events(id) NOT NULL,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  status TEXT NOT NULL DEFAULT 'registered',
  registration_time TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- NFT Memberships Table (for token-gated access)
CREATE TABLE public.nft_memberships (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  token_id TEXT UNIQUE NOT NULL,
  contract_address TEXT NOT NULL,
  blockchain TEXT NOT NULL DEFAULT 'ethereum',
  tier_id INTEGER REFERENCES public.subscription_tiers(id) NOT NULL,
  current_owner TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Content Access Table (maps Ghost content to subscription tiers)
CREATE TABLE public.content_access (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  ghost_post_id TEXT NOT NULL,
  required_tier TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

### 3. Authentication Setup

```sql
-- Enable email authentication
-- Configure SMTP for transactional emails
-- Set up OAuth providers (Google, Apple, etc.)

-- Create custom sign-up trigger to create profile
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, subscription_tier, subscription_status)
  VALUES (new.id, new.email, 'none', 'inactive');
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
```

### 4. Row-Level Security Policies

```sql
-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_tiers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.benefits_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_bank ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_pods ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pod_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.community_contributions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.event_registrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nft_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_access ENABLE ROW LEVEL SECURITY;

-- Create policies for profiles
CREATE POLICY "Users can view their own profile"
  ON public.profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = id);

-- Create policies for subscription tiers (public readable)
CREATE POLICY "Subscription tiers are viewable by everyone"
  ON public.subscription_tiers FOR SELECT
  USING (true);

-- Create policies for transactions
CREATE POLICY "Users can view their own transactions"
  ON public.subscription_transactions FOR SELECT
  USING (auth.uid() = user_id);

-- Create policies for benefits usage
CREATE POLICY "Users can view their own benefits usage"
  ON public.benefits_usage FOR SELECT
  USING (auth.uid() = user_id);

-- Create policies for subscription bank
CREATE POLICY "Users can view their own subscription bank"
  ON public.subscription_bank FOR SELECT
  USING (auth.uid() = user_id);

-- Create policies for pods
CREATE POLICY "Users can view pods they belong to"
  ON public.subscription_pods FOR SELECT
  USING (auth.uid() = primary_member_id OR 
         EXISTS (SELECT 1 FROM public.pod_members WHERE pod_id = id AND user_id = auth.uid()));

-- Create policies for pod members
CREATE POLICY "Users can view members of pods they belong to"
  ON public.pod_members FOR SELECT
  USING (EXISTS (SELECT 1 FROM public.subscription_pods sp 
                 WHERE sp.id = pod_id AND 
                 (sp.primary_member_id = auth.uid() OR 
                  EXISTS (SELECT 1 FROM public.pod_members pm 
                          WHERE pm.pod_id = pod_id AND pm.user_id = auth.uid()))));

-- Create policies for community contributions
CREATE POLICY "Users can view their own contributions"
  ON public.community_contributions FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own contributions"
  ON public.community_contributions FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Create policies for events
CREATE POLICY "Public events are viewable by everyone"
  ON public.events FOR SELECT
  USING (is_public = true);

CREATE POLICY "Tier-restricted events are viewable by eligible subscribers"
  ON public.events FOR SELECT
  USING (is_public = false AND 
         EXISTS (SELECT 1 FROM public.profiles 
                 WHERE id = auth.uid() AND 
                 subscription_tier >= required_tier AND
                 subscription_status = 'active'));

-- Create policies for event registrations
CREATE POLICY "Users can view their own registrations"
  ON public.event_registrations FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can register for events they can view"
  ON public.event_registrations FOR INSERT
  WITH CHECK (auth.uid() = user_id AND
              EXISTS (SELECT 1 FROM public.events 
                      WHERE id = event_id AND 
                      (is_public = true OR
                       EXISTS (SELECT 1 FROM public.profiles 
                               WHERE id = auth.uid() AND 
                               subscription_tier >= required_tier AND
                               subscription_status = 'active'))));

-- Create policies for NFT memberships
CREATE POLICY "NFT memberships are viewable by everyone"
  ON public.nft_memberships FOR SELECT
  USING (true);

-- Create policies for content access
CREATE POLICY "Content access rules are viewable by everyone"
  ON public.content_access FOR SELECT
  USING (true);
```

### 5. Supabase Edge Functions

Create the following serverless functions to handle subscription logic:

```javascript
// subscription-webhook.js - Handle Stripe webhook events
export async function handler(event, context) {
  const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
  const signature = event.headers['stripe-signature'];
  const { data, error } = await supabase.from('profiles').select('*');
  
  try {
    const stripeEvent = stripe.webhooks.constructEvent(
      event.body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET
    );
    
    // Handle different event types
    switch (stripeEvent.type) {
      case 'customer.subscription.created':
      case 'customer.subscription.updated':
        await handleSubscriptionChange(stripeEvent.data.object);
        break;
      case 'customer.subscription.deleted':
        await handleSubscriptionCancellation(stripeEvent.data.object);
        break;
      case 'invoice.payment_succeeded':
        await handleSuccessfulPayment(stripeEvent.data.object);
        break;
      case 'invoice.payment_failed':
        await handleFailedPayment(stripeEvent.data.object);
        break;
    }
    
    return { statusCode: 200, body: JSON.stringify({ received: true }) };
  } catch (err) {
    return { 
      statusCode: 400, 
      body: JSON.stringify({ error: `Webhook Error: ${err.message}` }) 
    };
  }
}

// tier-access.js - Check if user has access to content
export async function handler(event, context) {
  const { user_id, ghost_post_id } = JSON.parse(event.body);
  
  // Get user's subscription tier
  const { data: profile, error: profileError } = await supabase
    .from('profiles')
    .select('subscription_tier, subscription_status')
    .eq('id', user_id)
    .single();
    
  if (profileError || !profile) {
    return { statusCode: 404, body: JSON.stringify({ error: 'User not found' }) };
  }
  
  if (profile.subscription_status !== 'active') {
    return { statusCode: 403, body: JSON.stringify({ error: 'Subscription not active' }) };
  }
  
  // Get content access requirements
  const { data: contentAccess, error: contentError } = await supabase
    .from('content_access')
    .select('required_tier')
    .eq('ghost_post_id', ghost_post_id)
    .single();
    
  if (contentError) {
    // If no specific rule, assume public content
    return { statusCode: 200, body: JSON.stringify({ has_access: true }) };
  }
  
  // Check tier access (using tier hierarchy)
  const tiers = ['none', 'digital-devotee', 'print-provocateur', 'opulence-oracle', 'category-excellence'];
  const userTierIndex = tiers.indexOf(profile.subscription_tier);
  const requiredTierIndex = tiers.indexOf(contentAccess.required_tier);
  
  const hasAccess = userTierIndex >= requiredTierIndex;
  
  return { 
    statusCode: 200, 
    body: JSON.stringify({ 
      has_access: hasAccess,
      user_tier: profile.subscription_tier,
      required_tier: contentAccess.required_tier
    }) 
  };
}

// fluid-subscription.js - Handle fluid subscription changes
export async function handler(event, context) {
  const { user_id, action, days, target_user_id, reason } = JSON.parse(event.body);
  
  switch (action) {
    case 'bank':
      // Bank subscription days
      const { data, error } = await supabase
        .from('subscription_bank')
        .insert({
          user_id,
          banked_days: days,
          reason,
          expires_at: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000) // 1 year expiry
        });
      
      if (error) {
        return { statusCode: 400, body: JSON.stringify({ error: error.message }) };
      }
      
      return { statusCode: 200, body: JSON.stringify({ success: true, data }) };
      
    case 'gift':
      // Gift subscription days to another user
      // First check if user has enough banked days
      const { data: bankData, error: bankError } = await supabase
        .from('subscription_bank')
        .select('id, banked_days')
        .eq('user_id', user_id)
        .order('created_at', { ascending: true });
        
      if (bankError) {
        return { statusCode: 400, body: JSON.stringify({ error: bankError.message }) };
      }
      
      let remainingDays = days;
      let usedBankEntries = [];
      
      for (const entry of bankData) {
        if (remainingDays <= 0) break;
        
        if (entry.banked_days <= remainingDays) {
          // Use entire entry
          usedBankEntries.push({
            id: entry.id,
            used: entry.banked_days
          });
          remainingDays -= entry.banked_days;
        } else {
          // Use partial entry
          usedBankEntries.push({
            id: entry.id,
            used: remainingDays
          });
          remainingDays = 0;
        }
      }
      
      if (remainingDays > 0) {
        return { 
          statusCode: 400, 
          body: JSON.stringify({ 
            error: `Not enough banked days. Requested: ${days}, Available: ${days - remainingDays}` 
          }) 
        };
      }
      
      // Process the gift
      // 1. Deduct from bank
      for (const entry of usedBankEntries) {
        if (entry.used === bankData.find(b => b.id === entry.id).banked_days) {
          // Delete entire entry
          await supabase
            .from('subscription_bank')
            .delete()
            .eq('id', entry.id);
        } else {
          // Update entry
          await supabase
            .from('subscription_bank')
            .update({ banked_days: bankData.find(b => b.id === entry.id).banked_days - entry.used })
            .eq('id', entry.id);
        }
      }
      
      // 2. Add to target user's subscription
      const { data: targetProfile, error: targetError } = await supabase
        .from('profiles')
        .select('subscription_end_date')
        .eq('id', target_user_id)
        .single();
        
      if (targetError) {
        return { statusCode: 404, body: JSON.stringify({ error: 'Target user not found' }) };
      }
      
      let newEndDate;
      if (targetProfile.subscription_end_date) {
        newEndDate = new Date(targetProfile.subscription_end_date);
        newEndDate.setDate(newEndDate.getDate() + days);
      } else {
        newEndDate = new Date();
        newEndDate.setDate(newEndDate.getDate() + days);
      }
      
      await supabase
        .from('profiles')
        .update({ 
          subscription_end_date: newEndDate,
          subscription_status: 'active'
        })
        .eq('id', target_user_id);
      
      return { statusCode: 200, body: JSON.stringify({ success: true }) };
      
    default:
      return { 
        statusCode: 400, 
        body: JSON.stringify({ error: 'Invalid action' }) 
      };
  }
}

// pod-management.js - Handle subscription pod operations
export async function handler(event, context) {
  const { action, pod_id, user_id, pod_name, tier_id } = JSON.parse(event.body);
  
  switch (action) {
    case 'create':
      // Create new pod
      const { data: podData, error: podError } = await supabase
        .from('subscription_pods')
        .insert({
          pod_name,
          tier_id,
          primary_member_id: user_id
        })
        .select();
        
      if (podError) {
        return { statusCode: 400, body: JSON.stringify({ error: podError.message }) };
      }
      
      // Add creator as first member
      const { error: memberError } = await supabase
        .from('pod_members')
        .insert({
          pod_id: podData[0].id,
          user_id,
          role: 'admin'
        });
        
      if (memberError) {
        return { statusCode: 400, body: JSON.stringify({ error: memberError.message }) };
      }
      
      return { statusCode: 200, body: JSON.stringify({ success: true, pod: podData[0] }) };
      
    case 'invite':
      // Check if pod exists and user is admin
      const { data: pod, error: podCheckError } = await supabase
        .from('subscription_pods')
        .select('*')
        .eq('id', pod_id)
        .single();
        
      if (podCheckError) {
        return { statusCode: 404, body: JSON.stringify({ error: 'Pod not found' }) };
      }
      
      const { data: adminCheck, error: adminCheckError } = await supabase
        .from('pod_members')
        .select('role')
        .eq('pod_id', pod_id)
        .eq('user_id', user_id)
        .single();
        
      if (adminCheckError || adminCheck.role !== 'admin') {
        return { statusCode: 403, body: JSON.stringify({ error: 'Not authorized to invite members' }) };
      }
      
      // Count existing members
      const { data: memberCount, error: countError } = await supabase
        .from('pod_members')
        .select('id', { count: 'exact' })
        .eq('pod_id', pod_id);
        
      if (countError) {
        return { statusCode: 400, body: JSON.stringify({ error: countError.message }) };
      }
      
      // Check if pod is full (max 5 members)
      if (memberCount.length >= 5) {
        return { statusCode: 400, body: JSON.stringify({ error: 'Pod is full (max 5 members)' }) };
      }
      
      // TODO: Send invitation email to new member
      
      return { statusCode: 200, body: JSON.stringify({ success: true }) };
      
    default:
      return { 
        statusCode: 400, 
        body: JSON.stringify({ error: 'Invalid action' }) 
      };
  }
}
```

### 6. Storage Buckets

```sql
-- Create storage buckets for magazine assets
-- magazine_issues: For storing PDF issues
-- member_uploads: For community contributions
-- event_assets: For event materials and recordings

-- Set up bucket policies
-- Public read access for magazine previews
-- Authenticated read access for full issues based on subscription tier
```

## Ghost CMS Integration

### 1. Custom Integration API

Create a Node.js application to serve as the integration layer between Ghost and Supabase:

```javascript
// app.js
const express = require('express');
const { createClient } = require('@supabase/supabase-js');
const GhostAdminAPI = require('@tryghost/admin-api');
const GhostContentAPI = require('@tryghost/content-api');

const app = express();
app.use(express.json());

// Initialize Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

// Initialize Ghost Admin API client
const ghostAdmin = new GhostAdminAPI({
  url: process.env.GHOST_URL,
  key: process.env.GHOST_ADMIN_API_KEY,
  version: 'v3'
});

// Initialize Ghost Content API client
const ghostContent = new GhostContentAPI({
  url: process.env.GHOST_URL,
  key: process.env.GHOST_CONTENT_API_KEY,
  version: 'v3'
});

// Sync Ghost members with Supabase users
app.post('/api/sync-members', async (req, res) => {
  try {
    // Get all Ghost members
    const members = await ghostAdmin.members.browse({
      limit: 'all'
    });
    
    // For each member, ensure they exist in Supabase
    for (const member of members) {
      // Check if user exists in Supabase
      const { data: user, error } = await supabase
        .from('profiles')
        .select('id, email')
        .eq('email', member.email)
        .single();
        
      if (error) {
        // User doesn't exist, create them
        // First create auth user
        const { data: authUser, error: authError } = await supabase.auth.admin.createUser({
          email: member.email,
          email_confirm: true,
          user_metadata: {
            name: member.name
          }
        });
        
        if (authError) {
          console.error(`Error creating user for ${member.email}:`, authError);
          continue;
        }
        
        // Profile will be created by trigger
      }
    }
    
    res.json({ success: true, count: members.length });
  } catch (error) {
    console.error('Error syncing members:', error);
    res.status(500).json({ error: error.message });
  }
});

// Map Ghost content to subscription tiers
app.post('/api/map-content', async (req, res) => {
  try {
    const { post_id, required_tier } = req.body;
    
    if (!post_id || !required_tier) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    // Check if mapping already exists
    const { data: existing, error: checkError } = await supabase
      .from('content_access')
      .select('id')
      .eq('ghost_post_id', post_id)
      .single();
      
    if (existing) {
      // Update existing mapping
      const { error: updateError } = await supabase
        .from('content_access')
        .update({ required_tier })
        .eq('ghost_post_id', post_id);
        
      if (updateError) {
        return res.status(400).json({ error: updateError.message });
      }
    } else {
      // Create new mapping
      const { error: insertError } = await supabase
        .from('content_access')
        .insert({ ghost_post_id: post_id, required_tier });
        
      if (insertError) {
        return res.status(400).json({ error: insertError.message });
      }
    }
    
    res.json({ success: true });
  } catch (error) {
    console.error('Error mapping content:', error);
    res.status(500).json({ error: error.message });
  }
});

// Check content access for a user
app.get('/api/check-access', async (req, res) => {
  try {
    const { user_id, post_id } = req.query;
    
    if (!user_id || !post_id) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    // Call the tier-access function
    const response = await fetch(`${process.env.SUPABASE_URL}/functions/v1/tier-access`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.SUPABASE_ANON_KEY}`
      },
      body: JSON.stringify({
        user_id,
        ghost_post_id: post_id
      })
    });
    
    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Error checking access:', error);
    res.status(500).json({ error: error.message });
  }
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Integration API running on port ${PORT}`);
});
```

### 2. Ghost Webhooks

Configure Ghost webhooks to notify the integration API of relevant events:

1. **Post Published/Updated**: Trigger content mapping
2. **Member Added/Updated**: Sync with Supabase users

### 3. Custom Ghost Theme Modifications

Modify the Ghost theme to integrate with Supabase for subscription features:

```handlebars
{{!-- In default.hbs --}}
<script>
  // Initialize Supabase client
  const supabaseUrl = '{{@custom.supabase_url}}';
  const supabaseAnonKey = '{{@custom.supabase_anon_key}}';
  const supabase = supabase.createClient(supabaseUrl, supabaseAnonKey);
  
  // Check if user is logged in
  async function checkAuth() {
    const { data: { session } } = await supabase.auth.getSession();
    if (session) {
      // User is logged in
      document.body.classList.add('logged-in');
      
      // Get user profile
      const { data: profile } = await supabase
        .from('profiles')
        .select('subscription_tier, subscription_status')
        .eq('id', session.user.id)
        .single();
        
      if (profile) {
        // Add tier-specific classes
        document.body.classList.add(`tier-${profile.subscription_tier}`);
        document.body.classList.add(`subscription-${profile.subscription_status}`);
      }
    } else {
      document.body.classList.add('logged-out');
    }
  }
  
  // Check content access
  async function checkContentAccess(postId) {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) return false;
    
    const response = await fetch(`/api/check-access?user_id=${session.user.id}&post_id=${postId}`);
    const data = await response.json();
    
    return data.has_access;
  }
  
  // Initialize
  document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    
    // Check content access if on a post page
    const postId = document.querySelector('article')?.dataset.postId;
    if (postId) {
      checkContentAccess(postId).then(hasAccess => {
        if (!hasAccess) {
          // Show subscription prompt
          document.querySelector('.content').classList.add('content-restricted');
          document.querySelector('.subscription-prompt').classList.remove('hidden');
        }
      });
    }
  });
</script>

{{!-- Add subscription prompt template --}}
<div class="subscription-prompt hidden">
  <div class="subscription-prompt-inner">
    <h2>This content is exclusive to our subscribers</h2>
    <p>Join Luxe Queer magazine to access this and other premium content.</p>
    <div class="subscription-options">
      {{!-- Dynamically populated with subscription tiers --}}
    </div>
    <button class="login-button">Already a subscriber? Log in</button>
  </div>
</div>
```

## Frontend Implementation

### 1. Subscription Portal

Create a custom subscription portal using React:

```jsx
// SubscriptionPortal.jsx
import React, { useState, useEffect } from 'react';
import { supabase } from './supabaseClient';
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe('pk_test_...');

export default function SubscriptionPortal() {
  const [session, setSession] = useState(null);
  const [profile, setProfile] = useState(null);
  const [tiers, setTiers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Get session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session) {
        fetchProfile(session.user.id);
      }
    });
    
    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session);
        if (session) {
          fetchProfile(session.user.id);
        } else {
          setProfile(null);
        }
      }
    );
    
    // Fetch subscription tiers
    fetchTiers();
    
    return () => subscription.unsubscribe();
  }, []);
  
  async function fetchProfile(userId) {
    setLoading(true);
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .single();
      
    if (error) {
      console.error('Error fetching profile:', error);
    } else {
      setProfile(data);
    }
    setLoading(false);
  }
  
  async function fetchTiers() {
    const { data, error } = await supabase
      .from('subscription_tiers')
      .select('*')
      .eq('is_active', true)
      .order('monthly_price', { ascending: true });
      
    if (error) {
      console.error('Error fetching tiers:', error);
    } else {
      setTiers(data);
    }
  }
  
  async function handleSubscribe(tierId) {
    if (!session) {
      // Redirect to login
      return;
    }
    
    try {
      // Create Stripe checkout session
      const response = await fetch('/api/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tier_id: tierId,
          user_id: session.user.id,
          email: session.user.email
        }),
      });
      
      const { sessionId } = await response.json();
      
      // Redirect to Stripe checkout
      const stripe = await stripePromise;
      const { error } = await stripe.redirectToCheckout({ sessionId });
      
      if (error) {
        console.error('Error redirecting to checkout:', error);
      }
    } catch (error) {
      console.error('Error creating checkout session:', error);
    }
  }
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <div className="subscription-portal">
      <h1>Luxe Queer Membership</h1>
      
      {profile ? (
        <div className="current-subscription">
          <h2>Your Membership</h2>
          <p>Current tier: {profile.subscription_tier}</p>
          <p>Status: {profile.subscription_status}</p>
          {profile.subscription_end_date && (
            <p>Renews on: {new Date(profile.subscription_end_date).toLocaleDateString()}</p>
          )}
        </div>
      ) : (
        <div className="login-prompt">
          <p>Please log in to manage your subscription</p>
          <button onClick={() => supabase.auth.signIn({ provider: 'google' })}>
            Log in with Google
          </button>
        </div>
      )}
      
      <div className="subscription-tiers">
        <h2>Membership Options</h2>
        <div className="tier-cards">
          {tiers.map(tier => (
            <div key={tier.id} className="tier-card">
              <h3>{tier.tier_name}</h3>
              <p>{tier.description}</p>
              <div className="pricing">
                <div className="monthly">
                  <span className="price">${tier.monthly_price}</span>
                  <span className="period">per month</span>
                </div>
                <div className="annual">
                  <span className="price">${tier.annual_price}</span>
                  <span className="period">per year</span>
                  <span className="savings">
                    Save ${(tier.monthly_price * 12 - tier.annual_price).toFixed(2)}
                  </span>
                </div>
              </div>
              <ul className="features">
                {Object.entries(tier.features).map(([key, value]) => (
                  <li key={key} className={value ? 'included' : 'excluded'}>
                    {formatFeatureName(key)}
                  </li>
                ))}
              </ul>
              <div className="actions">
                <button 
                  onClick={() => handleSubscribe(tier.id)}
                  disabled={profile?.subscription_tier === tier.tier_slug}
                >
                  {profile?.subscription_tier === tier.tier_slug 
                    ? 'Current Tier' 
                    : 'Subscribe'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {profile && (
        <div className="subscription-management">
          <h2>Manage Your Membership</h2>
          <div className="management-options">
            <div className="option">
              <h3>Fluid Subscription</h3>
              <p>Bank days when you're away or gift to friends</p>
              <button onClick={() => navigate('/fluid-subscription')}>
                Manage Fluid Options
              </button>
            </div>
            <div className="option">
              <h3>Subscription Pods</h3>
              <p>Share a higher tier with friends at a reduced cost</p>
              <button onClick={() => navigate('/subscription-pods')}>
                Manage Pods
              </button>
            </div>
            <div className="option">
              <h3>Community Contributions</h3>
              <p>Earn subscription credits through contributions</p>
              <button onClick={() => navigate('/community-contributions')}>
                View Opportunities
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function formatFeatureName(key) {
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
```

### 2. Fluid Subscription Management

Create a component for managing fluid subscription options:

```jsx
// FluidSubscription.jsx
import React, { useState, useEffect } from 'react';
import { supabase } from './supabaseClient';

export default function FluidSubscription() {
  const [session, setSession] = useState(null);
  const [bankedDays, setBankedDays] = useState(0);
  const [bankHistory, setBankHistory] = useState([]);
  const [daysToBank, setDaysToBank] = useState(0);
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Get session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session) {
        fetchBankData(session.user.id);
      }
    });
    
    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session);
        if (session) {
          fetchBankData(session.user.id);
        }
      }
    );
    
    return () => subscription.unsubscribe();
  }, []);
  
  async function fetchBankData(userId) {
    setLoading(true);
    
    // Get total banked days
    const { data: bankData, error: bankError } = await supabase
      .from('subscription_bank')
      .select('banked_days')
      .eq('user_id', userId);
      
    if (bankError) {
      console.error('Error fetching bank data:', bankError);
    } else {
      const total = bankData.reduce((sum, item) => sum + item.banked_days, 0);
      setBankedDays(total);
    }
    
    // Get bank history
    const { data: historyData, error: historyError } = await supabase
      .from('subscription_bank')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });
      
    if (historyError) {
      console.error('Error fetching bank history:', historyError);
    } else {
      setBankHistory(historyData);
    }
    
    setLoading(false);
  }
  
  async function handleBankDays() {
    if (!session || daysToBank <= 0) return;
    
    try {
      const response = await fetch('/functions/v1/fluid-subscription', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          user_id: session.user.id,
          action: 'bank',
          days: daysToBank,
          reason
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Refresh bank data
        fetchBankData(session.user.id);
        // Reset form
        setDaysToBank(0);
        setReason('');
      } else {
        console.error('Error banking days:', data.error);
      }
    } catch (error) {
      console.error('Error banking days:', error);
    }
  }
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!session) {
    return <div>Please log in to manage your subscription</div>;
  }
  
  return (
    <div className="fluid-subscription">
      <h1>Fluid Subscription Management</h1>
      
      <div className="bank-summary">
        <h2>Your Subscription Bank</h2>
        <p className="bank-total">Total banked days: {bankedDays}</p>
      </div>
      
      <div className="bank-days-form">
        <h2>Bank Subscription Days</h2>
        <p>Pause your subscription and bank days for later use</p>
        
        <div className="form-group">
          <label htmlFor="daysToBank">Days to bank:</label>
          <input
            type="number"
            id="daysToBank"
            value={daysToBank}
            onChange={e => setDaysToBank(parseInt(e.target.value))}
            min="1"
            max="365"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="reason">Reason (optional):</label>
          <select
            id="reason"
            value={reason}
            onChange={e => setReason(e.target.value)}
          >
            <option value="">Select a reason</option>
            <option value="travel">Traveling</option>
            <option value="busy">Too busy to read</option>
            <option value="saving">Saving for later</option>
            <option value="other">Other</option>
          </select>
        </div>
        
        <button 
          onClick={handleBankDays}
          disabled={daysToBank <= 0}
        >
          Bank Days
        </button>
      </div>
      
      <div className="gift-days">
        <h2>Gift Subscription Days</h2>
        <p>Share your banked days with friends</p>
        {/* Gift form implementation */}
      </div>
      
      <div className="bank-history">
        <h2>Bank History</h2>
        {bankHistory.length === 0 ? (
          <p>No bank history yet</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Days</th>
                <th>Reason</th>
                <th>Expires</th>
              </tr>
            </thead>
            <tbody>
              {bankHistory.map(item => (
                <tr key={item.id}>
                  <td>{new Date(item.created_at).toLocaleDateString()}</td>
                  <td>{item.banked_days}</td>
                  <td>{item.reason || 'Not specified'}</td>
                  <td>{new Date(item.expires_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
```

### 3. Subscription Pods Management

Create a component for managing subscription pods:

```jsx
// SubscriptionPods.jsx
import React, { useState, useEffect } from 'react';
import { supabase } from './supabaseClient';

export default function SubscriptionPods() {
  const [session, setSession] = useState(null);
  const [pods, setPods] = useState([]);
  const [tiers, setTiers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newPodName, setNewPodName] = useState('');
  const [selectedTier, setSelectedTier] = useState('');
  
  useEffect(() => {
    // Get session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session) {
        fetchPods(session.user.id);
        fetchTiers();
      }
    });
    
    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session);
        if (session) {
          fetchPods(session.user.id);
          fetchTiers();
        }
      }
    );
    
    return () => subscription.unsubscribe();
  }, []);
  
  async function fetchPods(userId) {
    setLoading(true);
    
    // Get pods where user is a member
    const { data, error } = await supabase
      .from('subscription_pods')
      .select(`
        *,
        pod_members!inner(user_id)
      `)
      .eq('pod_members.user_id', userId);
      
    if (error) {
      console.error('Error fetching pods:', error);
    } else {
      // For each pod, get all members
      const podsWithMembers = await Promise.all(data.map(async pod => {
        const { data: members, error: membersError } = await supabase
          .from('pod_members')
          .select(`
            *,
            profiles:user_id(email, first_name, last_name, display_name)
          `)
          .eq('pod_id', pod.id);
          
        if (membersError) {
          console.error('Error fetching pod members:', membersError);
          return { ...pod, members: [] };
        }
        
        return { ...pod, members };
      }));
      
      setPods(podsWithMembers);
    }
    
    setLoading(false);
  }
  
  async function fetchTiers() {
    const { data, error } = await supabase
      .from('subscription_tiers')
      .select('*')
      .eq('is_active', true)
      .order('monthly_price', { ascending: true });
      
    if (error) {
      console.error('Error fetching tiers:', error);
    } else {
      setTiers(data);
    }
  }
  
  async function handleCreatePod() {
    if (!session || !newPodName || !selectedTier) return;
    
    try {
      const response = await fetch('/functions/v1/pod-management', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          action: 'create',
          user_id: session.user.id,
          pod_name: newPodName,
          tier_id: selectedTier
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Refresh pods
        fetchPods(session.user.id);
        // Reset form
        setNewPodName('');
        setSelectedTier('');
        setShowCreateForm(false);
      } else {
        console.error('Error creating pod:', data.error);
      }
    } catch (error) {
      console.error('Error creating pod:', error);
    }
  }
  
  async function handleInviteMember(podId) {
    // Implementation for inviting members
  }
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!session) {
    return <div>Please log in to manage subscription pods</div>;
  }
  
  return (
    <div className="subscription-pods">
      <h1>Subscription Pods</h1>
      <p>Share higher-tier subscriptions with friends at a reduced cost</p>
      
      {pods.length === 0 ? (
        <div className="no-pods">
          <p>You are not a member of any subscription pods yet.</p>
        </div>
      ) : (
        <div className="pods-list">
          {pods.map(pod => (
            <div key={pod.id} className="pod-card">
              <h2>{pod.pod_name}</h2>
              <p>Tier: {tiers.find(t => t.id === pod.tier_id)?.tier_name || 'Unknown'}</p>
              
              <h3>Members ({pod.members.length}/5)</h3>
              <ul className="members-list">
                {pod.members.map(member => (
                  <li key={member.id} className={member.role === 'admin' ? 'admin' : ''}>
                    {member.profiles.display_name || member.profiles.email}
                    {member.role === 'admin' && ' (Admin)'}
                  </li>
                ))}
              </ul>
              
              {pod.members.find(m => m.user_id === session.user.id)?.role === 'admin' && (
                <div className="admin-actions">
                  <button onClick={() => handleInviteMember(pod.id)}>
                    Invite Member
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
      
      <div className="create-pod">
        {showCreateForm ? (
          <div className="create-pod-form">
            <h2>Create New Pod</h2>
            
            <div className="form-group">
              <label htmlFor="podName">Pod Name:</label>
              <input
                type="text"
                id="podName"
                value={newPodName}
                onChange={e => setNewPodName(e.target.value)}
                placeholder="e.g., Fashion Friends"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="tierSelect">Subscription Tier:</label>
              <select
                id="tierSelect"
                value={selectedTier}
                onChange={e => setSelectedTier(e.target.value)}
              >
                <option value="">Select a tier</option>
                {tiers.map(tier => (
                  <option key={tier.id} value={tier.id}>
                    {tier.tier_name} (${tier.monthly_price}/month)
                  </option>
                ))}
              </select>
            </div>
            
            <div className="form-actions">
              <button 
                onClick={handleCreatePod}
                disabled={!newPodName || !selectedTier}
              >
                Create Pod
              </button>
              <button 
                className="cancel"
                onClick={() => setShowCreateForm(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <button 
            className="create-pod-button"
            onClick={() => setShowCreateForm(true)}
          >
            Create New Pod
          </button>
        )}
      </div>
    </div>
  );
}
```

## Payment Integration

### 1. Stripe Integration

Set up Stripe for subscription payments:

```javascript
// stripe-integration.js
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const express = require('express');
const router = express.Router();
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

// Create checkout session
router.post('/create-checkout-session', async (req, res) => {
  try {
    const { tier_id, user_id, email } = req.body;
    
    // Get tier details
    const { data: tier, error: tierError } = await supabase
      .from('subscription_tiers')
      .select('*')
      .eq('id', tier_id)
      .single();
      
    if (tierError) {
      return res.status(400).json({ error: 'Invalid tier' });
    }
    
    // Create or get Stripe customer
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('stripe_customer_id')
      .eq('id', user_id)
      .single();
      
    let customerId;
    
    if (profileError || !profile.stripe_customer_id) {
      // Create new customer
      const customer = await stripe.customers.create({
        email,
        metadata: {
          supabase_id: user_id
        }
      });
      
      customerId = customer.id;
      
      // Update profile with customer ID
      await supabase
        .from('profiles')
        .update({ stripe_customer_id: customerId })
        .eq('id', user_id);
    } else {
      customerId = profile.stripe_customer_id;
    }
    
    // Create price if needed (or use existing price IDs)
    // In production, you would have predefined price IDs
    
    // Create checkout session
    const session = await stripe.checkout.sessions.create({
      customer: customerId,
      payment_method_types: ['card'],
      line_items: [
        {
          price_data: {
            currency: 'usd',
            product_data: {
              name: tier.tier_name,
              description: tier.description
            },
            unit_amount: Math.round(tier.monthly_price * 100),
            recurring: {
              interval: 'month'
            }
          },
          quantity: 1
        }
      ],
      mode: 'subscription',
      success_url: `${process.env.FRONTEND_URL}/subscription/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.FRONTEND_URL}/subscription/cancel`,
      metadata: {
        user_id,
        tier_id,
        tier_slug: tier.tier_slug
      }
    });
    
    res.json({ sessionId: session.id });
  } catch (error) {
    console.error('Error creating checkout session:', error);
    res.status(500).json({ error: error.message });
  }
});

// Handle webhook events
router.post('/webhook', async (req, res) => {
  const signature = req.headers['stripe-signature'];
  
  try {
    const event = stripe.webhooks.constructEvent(
      req.rawBody,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET
    );
    
    // Handle the event
    switch (event.type) {
      case 'checkout.session.completed':
        await handleCheckoutCompleted(event.data.object);
        break;
      case 'customer.subscription.created':
      case 'customer.subscription.updated':
        await handleSubscriptionUpdated(event.data.object);
        break;
      case 'customer.subscription.deleted':
        await handleSubscriptionDeleted(event.data.object);
        break;
      default:
        console.log(`Unhandled event type ${event.type}`);
    }
    
    res.json({ received: true });
  } catch (error) {
    console.error('Error handling webhook:', error);
    res.status(400).send(`Webhook Error: ${error.message}`);
  }
});

async function handleCheckoutCompleted(session) {
  // Record the transaction
  await supabase
    .from('subscription_transactions')
    .insert({
      user_id: session.metadata.user_id,
      tier_id: session.metadata.tier_id,
      transaction_type: 'subscription_start',
      amount: session.amount_total / 100,
      currency: session.currency,
      payment_method: 'card',
      payment_id: session.payment_intent,
      status: 'completed'
    });
}

async function handleSubscriptionUpdated(subscription) {
  // Get customer
  const customer = await stripe.customers.retrieve(subscription.customer);
  const userId = customer.metadata.supabase_id;
  
  if (!userId) {
    console.error('No user ID found in customer metadata');
    return;
  }
  
  // Get subscription item
  const subscriptionItem = subscription.items.data[0];
  const priceId = subscriptionItem.price.id;
  
  // Get tier from price ID
  // In production, you would have a mapping of price IDs to tiers
  // For this example, we'll use the metadata from the subscription
  const tierSlug = subscription.metadata.tier_slug;
  
  // Update user profile
  await supabase
    .from('profiles')
    .update({
      subscription_tier: tierSlug,
      subscription_status: subscription.status,
      subscription_start_date: new Date(subscription.current_period_start * 1000).toISOString(),
      subscription_end_date: new Date(subscription.current_period_end * 1000).toISOString(),
      billing_frequency: subscriptionItem.price.recurring.interval,
      billing_amount: subscriptionItem.price.unit_amount / 100,
      currency: subscriptionItem.price.currency
    })
    .eq('id', userId);
}

async function handleSubscriptionDeleted(subscription) {
  // Get customer
  const customer = await stripe.customers.retrieve(subscription.customer);
  const userId = customer.metadata.supabase_id;
  
  if (!userId) {
    console.error('No user ID found in customer metadata');
    return;
  }
  
  // Update user profile
  await supabase
    .from('profiles')
    .update({
      subscription_status: 'canceled',
      subscription_end_date: new Date(subscription.current_period_end * 1000).toISOString()
    })
    .eq('id', userId);
}

module.exports = router;
```

### 2. NFT Membership Integration

Set up token-gated access for NFT memberships:

```javascript
// nft-integration.js
const express = require('express');
const router = express.Router();
const { createClient } = require('@supabase/supabase-js');
const { ethers } = require('ethers');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

// ABI for ERC721 interface (simplified)
const ERC721_ABI = [
  'function balanceOf(address owner) view returns (uint256)',
  'function ownerOf(uint256 tokenId) view returns (address)',
  'function tokenURI(uint256 tokenId) view returns (string)'
];

// Verify NFT ownership
router.post('/verify-nft', async (req, res) => {
  try {
    const { wallet_address, token_id, contract_address } = req.body;
    
    // Check if NFT exists in our database
    const { data: nft, error: nftError } = await supabase
      .from('nft_memberships')
      .select('*')
      .eq('token_id', token_id)
      .eq('contract_address', contract_address)
      .single();
      
    if (nftError) {
      return res.status(404).json({ error: 'NFT not found in our records' });
    }
    
    if (!nft.is_active) {
      return res.status(403).json({ error: 'NFT membership is not active' });
    }
    
    // Connect to Ethereum provider
    const provider = new ethers.providers.JsonRpcProvider(process.env.ETHEREUM_RPC_URL);
    
    // Create contract instance
    const contract = new ethers.Contract(contract_address, ERC721_ABI, provider);
    
    try {
      // Check ownership
      const owner = await contract.ownerOf(token_id);
      
      if (owner.toLowerCase() !== wallet_address.toLowerCase()) {
        return res.status(403).json({ error: 'Wallet does not own this NFT' });
      }
      
      // Update NFT ownership in database
      await supabase
        .from('nft_memberships')
        .update({ current_owner: wallet_address })
        .eq('token_id', token_id)
        .eq('contract_address', contract_address);
      
      // Get tier details
      const { data: tier, error: tierError } = await supabase
        .from('subscription_tiers')
        .select('*')
        .eq('id', nft.tier_id)
        .single();
        
      if (tierError) {
        return res.status(500).json({ error: 'Error fetching tier details' });
      }
      
      res.json({
        verified: true,
        tier: tier.tier_slug,
        tier_name: tier.tier_name
      });
    } catch (error) {
      console.error('Error verifying NFT ownership:', error);
      res.status(403).json({ error: 'Error verifying NFT ownership' });
    }
  } catch (error) {
    console.error('Error in NFT verification:', error);
    res.status(500).json({ error: error.message });
  }
});

// Link NFT to user account
router.post('/link-nft', async (req, res) => {
  try {
    const { user_id, wallet_address, token_id, contract_address } = req.body;
    
    // Verify NFT ownership first
    const verifyResponse = await fetch(`${req.protocol}://${req.get('host')}/api/verify-nft`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        wallet_address,
        token_id,
        contract_address
      })
    });
    
    const verifyData = await verifyResponse.json();
    
    if (!verifyResponse.ok || !verifyData.verified) {
      return res.status(403).json({ error: verifyData.error || 'NFT verification failed' });
    }
    
    // Get user profile
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user_id)
      .single();
      
    if (profileError) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    // Update user profile with NFT membership
    await supabase
      .from('profiles')
      .update({
        subscription_tier: verifyData.tier,
        subscription_status: 'active',
        wallet_address
      })
      .eq('id', user_id);
    
    res.json({
      success: true,
      tier: verifyData.tier,
      tier_name: verifyData.tier_name
    });
  } catch (error) {
    console.error('Error linking NFT:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
```

## Deployment and Integration

### 1. Deployment Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Ghost CMS      │◄────┤  Integration    │◄────┤  Supabase       │
│  (Content)      │     │  API            │     │  (Users/Data)   │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         ▲                      ▲                       ▲
         │                      │                       │
         │                      │                       │
         ▼                      ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Frontend       │◄────┤  Stripe         │◄────┤  Blockchain     │
│  Applications   │     │  Payments       │     │  (NFTs)         │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 2. Integration Steps

1. **Create Supabase Project**:
   - Set up a new Supabase project
   - Execute the database schema SQL
   - Configure authentication providers
   - Set up storage buckets

2. **Deploy Integration API**:
   - Deploy the Node.js integration API to a hosting service
   - Configure environment variables for API keys and endpoints
   - Set up webhooks between Ghost and the integration API

3. **Configure Ghost CMS**:
   - Update Ghost theme with Supabase integration code
   - Configure custom routes for subscription management
   - Set up content access rules

4. **Deploy Frontend Applications**:
   - Build and deploy the React components for subscription management
   - Configure environment variables for API endpoints
   - Set up routing and authentication flow

5. **Set Up Payment Processing**:
   - Configure Stripe account and API keys
   - Set up webhook endpoints
   - Create subscription products and prices

6. **Configure NFT Integration** (if using token-gated access):
   - Deploy smart contracts for NFT memberships
   - Set up blockchain provider connections
   - Configure verification endpoints

### 3. Testing Plan

1. **User Registration and Authentication**:
   - Test user registration flow
   - Verify email confirmation
   - Test social login providers
   - Ensure profile creation on registration

2. **Subscription Purchase**:
   - Test checkout flow for each tier
   - Verify Stripe webhook processing
   - Confirm profile updates with subscription details
   - Test renewal process

3. **Content Access Control**:
   - Test access to content based on subscription tier
   - Verify paywall functionality
   - Test upgrade/downgrade scenarios

4. **Fluid Subscription Features**:
   - Test banking subscription days
   - Verify gifting functionality
   - Test subscription pod creation and management
   - Verify community contribution system

5. **NFT Membership** (if implemented):
   - Test NFT minting process
   - Verify ownership verification
   - Test linking NFT to user account
   - Confirm access based on NFT ownership

## Conclusion

This technical implementation plan provides a comprehensive framework for integrating Supabase with Ghost CMS to power the innovative subscription model for Luxe Queer magazine. The integration leverages Supabase's robust authentication, real-time database, and serverless functions to create a sophisticated subscription system that supports all the innovative features outlined in the subscription model framework.

The implementation includes:

1. **Complete Database Schema** with tables for profiles, subscription tiers, transactions, benefits usage, subscription banking, pods, community contributions, events, and NFT memberships

2. **Authentication System** with secure user management and profile creation

3. **Row-Level Security Policies** to ensure data privacy and access control

4. **Serverless Functions** for handling subscription logic, fluid subscription management, and pod operations

5. **Frontend Components** for subscription management, fluid subscription features, and pod management

6. **Payment Integration** with Stripe for recurring subscriptions

7. **NFT Membership Support** for token-gated access (optional)

8. **Deployment Architecture** showing how all components interact

By implementing this plan, Luxe Queer magazine will have a state-of-the-art subscription system that supports traditional subscriptions while enabling innovative features like fluid subscriptions, collective pods, community contributions, and token-gated access. This technical foundation will provide the flexibility and scalability needed to grow the magazine's subscriber base while offering a unique and valuable experience to members.
