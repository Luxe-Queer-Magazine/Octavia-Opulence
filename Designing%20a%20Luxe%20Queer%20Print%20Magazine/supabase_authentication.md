# Supabase Authentication Configuration for Luxe Queer Magazine

## Authentication Credentials

**Supabase URL:** https://ovggshlfwumbtviwvbhi.supabase.co

**Supabase Anon Key:** 
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im92Z2dzaGxmd3VtYnR2aXd2YmhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4NTU2MzQsImV4cCI6MjA1OTQzMTYzNH0.cqayJFbYN2jMi7-nz3vLpIa5rL0ftStozdlT_3J7u04
```

## Client-Side Implementation

### Frontend Authentication Setup

Use the following code to initialize the Supabase client in frontend applications:

```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://ovggshlfwumbtviwvbhi.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im92Z2dzaGxmd3VtYnR2aXd2YmhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4NTU2MzQsImV4cCI6MjA1OTQzMTYzNH0.cqayJFbYN2jMi7-nz3vLpIa5rL0ftStozdlT_3J7u04'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### User Authentication Flows

#### Sign Up

```javascript
const signUp = async (email, password) => {
  try {
    const { user, error } = await supabase.auth.signUp({
      email,
      password,
    })
    
    if (error) throw error
    
    // Create initial profile in profiles table
    if (user) {
      const { error: profileError } = await supabase
        .from('profiles')
        .insert([
          { 
            user_id: user.id,
            email: email,
            created_at: new Date(),
          }
        ])
      
      if (profileError) throw profileError
    }
    
    return { user, error: null }
  } catch (error) {
    return { user: null, error }
  }
}
```

#### Sign In

```javascript
const signIn = async (email, password) => {
  try {
    const { user, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    
    if (error) throw error
    return { user, error: null }
  } catch (error) {
    return { user: null, error }
  }
}
```

#### Sign Out

```javascript
const signOut = async () => {
  try {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    return { error: null }
  } catch (error) {
    return { error }
  }
}
```

#### Password Reset

```javascript
const resetPassword = async (email) => {
  try {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: 'https://luxequeer.com/reset-password',
    })
    
    if (error) throw error
    return { error: null }
  } catch (error) {
    return { error }
  }
}
```

### Social Authentication

Configure social authentication with the following providers:

#### Google Authentication

```javascript
const signInWithGoogle = async () => {
  try {
    const { user, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: 'https://luxequeer.com/auth/callback',
      }
    })
    
    if (error) throw error
    return { user, error: null }
  } catch (error) {
    return { user: null, error }
  }
}
```

#### Twitter Authentication

```javascript
const signInWithTwitter = async () => {
  try {
    const { user, error } = await supabase.auth.signInWithOAuth({
      provider: 'twitter',
      options: {
        redirectTo: 'https://luxequeer.com/auth/callback',
      }
    })
    
    if (error) throw error
    return { user, error: null }
  } catch (error) {
    return { user: null, error }
  }
}
```

### User Session Management

#### Get Current User

```javascript
const getCurrentUser = async () => {
  try {
    const { data: { user }, error } = await supabase.auth.getUser()
    
    if (error) throw error
    return { user, error: null }
  } catch (error) {
    return { user: null, error }
  }
}
```

#### Get User Profile

```javascript
const getUserProfile = async (userId) => {
  try {
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('user_id', userId)
      .single()
    
    if (error) throw error
    return { profile: data, error: null }
  } catch (error) {
    return { profile: null, error }
  }
}
```

#### Update User Profile

```javascript
const updateUserProfile = async (userId, updates) => {
  try {
    const { data, error } = await supabase
      .from('profiles')
      .update(updates)
      .eq('user_id', userId)
    
    if (error) throw error
    return { profile: data, error: null }
  } catch (error) {
    return { profile: null, error }
  }
}
```

## Subscription Tier Authentication

### Get User Subscription

```javascript
const getUserSubscription = async (userId) => {
  try {
    const { data, error } = await supabase
      .from('subscriptions')
      .select(`
        *,
        subscription_tiers(*)
      `)
      .eq('user_id', userId)
      .single()
    
    if (error) throw error
    return { subscription: data, error: null }
  } catch (error) {
    return { subscription: null, error }
  }
}
```

### Check Content Access

```javascript
const checkContentAccess = async (userId, contentTier) => {
  try {
    const { data, error } = await supabase
      .rpc('check_content_access', {
        user_id: userId,
        required_tier: contentTier
      })
    
    if (error) throw error
    return { hasAccess: data, error: null }
  } catch (error) {
    return { hasAccess: false, error }
  }
}
```

## Row-Level Security Policies

Implement the following RLS policies in your Supabase instance:

### Profiles Table

```sql
-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Allow users to read their own profile
CREATE POLICY "Users can view their own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = user_id);

-- Allow users to update their own profile
CREATE POLICY "Users can update their own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = user_id);

-- Allow service role to manage all profiles
CREATE POLICY "Service role can do anything with profiles"
  ON profiles
  USING (auth.role() = 'service_role');
```

### Subscriptions Table

```sql
-- Enable RLS
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Allow users to read their own subscription
CREATE POLICY "Users can view their own subscription"
  ON subscriptions FOR SELECT
  USING (auth.uid() = user_id);

-- Allow service role to manage all subscriptions
CREATE POLICY "Service role can do anything with subscriptions"
  ON subscriptions
  USING (auth.role() = 'service_role');
```

### Content Access Table

```sql
-- Enable RLS
ALTER TABLE content_access ENABLE ROW LEVEL SECURITY;

-- Allow users to read content they have access to
CREATE POLICY "Users can view content they have access to"
  ON content_access FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM subscriptions s
      JOIN subscription_tiers st ON s.tier_id = st.id
      WHERE s.user_id = auth.uid()
      AND st.tier_level >= content_access.required_tier_level
    )
  );

-- Allow service role to manage all content access
CREATE POLICY "Service role can do anything with content access"
  ON content_access
  USING (auth.role() = 'service_role');
```

## Stored Procedures

Create the following stored procedures to handle subscription-related authentication:

### Check Content Access

```sql
CREATE OR REPLACE FUNCTION check_content_access(user_id UUID, required_tier INT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM subscriptions s
    JOIN subscription_tiers st ON s.tier_id = st.id
    WHERE s.user_id = check_content_access.user_id
    AND st.tier_level >= check_content_access.required_tier
    AND s.status = 'active'
  );
END;
$$;
```

### Get User Tier Level

```sql
CREATE OR REPLACE FUNCTION get_user_tier_level(user_id UUID)
RETURNS INT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  tier_level INT;
BEGIN
  SELECT st.tier_level INTO tier_level
  FROM subscriptions s
  JOIN subscription_tiers st ON s.tier_id = st.id
  WHERE s.user_id = get_user_tier_level.user_id
  AND s.status = 'active';
  
  RETURN COALESCE(tier_level, 0);
END;
$$;
```

## JWT Configuration

Configure JWT handling for subscription tier information:

```javascript
// Example of extracting subscription tier from JWT
const getUserTierFromJWT = () => {
  const { data: { session } } = supabase.auth.getSession()
  
  if (!session) return null
  
  // Extract custom claims from JWT
  const jwt = session.access_token
  const payload = JSON.parse(atob(jwt.split('.')[1]))
  
  return payload.app_metadata?.tier || 'digital-devotee'
}
```

## Security Considerations

1. **Store the anon key securely:**
   - For web applications, include it in environment variables
   - For mobile apps, use secure storage mechanisms
   - Never expose the key in client-side source code repositories

2. **Implement proper CORS settings:**
   - Configure allowed origins in Supabase dashboard
   - Restrict to your production domains

3. **Set up proper email templates:**
   - Customize authentication emails
   - Ensure brand consistency
   - Include clear instructions for users

4. **Monitor authentication activity:**
   - Set up logging for authentication events
   - Create alerts for suspicious activities
   - Regularly review authentication logs

5. **Implement rate limiting:**
   - Protect against brute force attacks
   - Limit authentication attempts
   - Use Supabase's built-in rate limiting features

## Implementation Checklist

- [ ] Initialize Supabase client with URL and anon key
- [ ] Implement user authentication flows (signup, signin, signout)
- [ ] Configure social authentication providers
- [ ] Set up password reset functionality
- [ ] Create user profile management
- [ ] Implement subscription tier authentication
- [ ] Configure row-level security policies
- [ ] Create stored procedures for access control
- [ ] Set up JWT handling for subscription information
- [ ] Test all authentication flows
- [ ] Implement security monitoring

This authentication configuration ensures that all components of the Luxe Queer magazine system properly authenticate users and control access to content based on subscription tiers, using the specific Supabase instance at https://ovggshlfwumbtviwvbhi.supabase.co with the provided anon key.
