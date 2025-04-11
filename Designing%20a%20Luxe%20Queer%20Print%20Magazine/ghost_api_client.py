#!/usr/bin/env python3

import requests
import json
import os
from datetime import datetime

class GhostApiClient:
    def __init__(self, url, admin_key, content_key):
        self.url = url
        self.admin_key = admin_key
        self.content_key = content_key
        self.admin_api_url = f"{url}/ghost/api/admin/v3"
        self.content_api_url = f"{url}/ghost/api/v3/content"
    
    def get_site_info(self):
        """Get basic information about the Ghost site"""
        endpoint = f"{self.content_api_url}/settings"
        headers = {'Content-Type': 'application/json'}
        params = {'key': self.content_key}
        
        response = requests.get(endpoint, headers=headers, params=params)
        return response.json()
    
    def get_posts(self, limit=5):
        """Get posts from the Ghost site"""
        endpoint = f"{self.content_api_url}/posts"
        headers = {'Content-Type': 'application/json'}
        params = {
            'key': self.content_key,
            'limit': limit,
            'include': 'tags,authors'
        }
        
        response = requests.get(endpoint, headers=headers, params=params)
        return response.json()
    
    def get_tags(self):
        """Get all tags from the Ghost site"""
        endpoint = f"{self.content_api_url}/tags"
        headers = {'Content-Type': 'application/json'}
        params = {'key': self.content_key, 'limit': 'all'}
        
        response = requests.get(endpoint, headers=headers, params=params)
        return response.json()
    
    def create_tag(self, name, slug, description=None, feature_image=None):
        """Create a new tag using the Admin API"""
        endpoint = f"{self.admin_api_url}/tags"
        headers = {'Content-Type': 'application/json'}
        
        data = {
            "tags": [
                {
                    "name": name,
                    "slug": slug
                }
            ]
        }
        
        if description:
            data["tags"][0]["description"] = description
        
        if feature_image:
            data["tags"][0]["feature_image"] = feature_image
        
        # Admin API requires authentication with the admin key
        admin_auth = self.admin_key.split(':')
        auth = (admin_auth[0], admin_auth[1])
        
        response = requests.post(endpoint, headers=headers, json=data, auth=auth)
        return response.json()
    
    def create_post(self, title, html_content, status="draft", tags=None, featured=False):
        """Create a new post using the Admin API"""
        endpoint = f"{self.admin_api_url}/posts"
        headers = {'Content-Type': 'application/json'}
        
        data = {
            "posts": [
                {
                    "title": title,
                    "html": html_content,
                    "status": status,
                    "featured": featured
                }
            ]
        }
        
        if tags:
            data["posts"][0]["tags"] = tags
        
        # Admin API requires authentication with the admin key
        admin_auth = self.admin_key.split(':')
        auth = (admin_auth[0], admin_auth[1])
        
        response = requests.post(endpoint, headers=headers, json=data, auth=auth)
        return response.json()
    
    def update_settings(self, settings_data):
        """Update Ghost settings using the Admin API"""
        endpoint = f"{self.admin_api_url}/settings"
        headers = {'Content-Type': 'application/json'}
        
        # Admin API requires authentication with the admin key
        admin_auth = self.admin_key.split(':')
        auth = (admin_auth[0], admin_auth[1])
        
        response = requests.put(endpoint, headers=headers, json=settings_data, auth=auth)
        return response.json()

# Example usage
if __name__ == "__main__":
    # Ghost instance URL
    ghost_url = "https://rainbow-millipede.pikapod.net"
    
    # Updated API credentials
    admin_key = "67ef67107bdbb900014522e2:a83281ff2c5c9eb4ee94242f87cd1e8ace9d4cb9317358acda25f8ec1f266d73"
    content_key = "bbc75241a46836b87673d05b12"
    
    # Initialize the client
    client = GhostApiClient(ghost_url, admin_key, content_key)
    
    # Get site information
    site_info = client.get_site_info()
    print("Site Information:")
    print(json.dumps(site_info, indent=2))
    
    # Get posts
    posts = client.get_posts()
    print("\nPosts:")
    print(json.dumps(posts, indent=2))
