#!/usr/bin/env python3

import requests
import json
import os
from ghost_api_client import GhostApiClient

def configure_magazine_structure(client):
    """Configure the Ghost CMS instance for Luxe Queer magazine structure"""
    
    # Create main section tags based on our content structure
    sections = [
        {
            "name": "FASHION",
            "slug": "fashion",
            "description": "High-end fashion editorials and analysis with a queer lens"
        },
        {
            "name": "ART",
            "slug": "art",
            "description": "Contemporary art showcases and critical analysis from queer perspectives"
        },
        {
            "name": "CULTURE",
            "slug": "culture",
            "description": "Film, literature, music, and performance through a queer lens"
        },
        {
            "name": "TRAVEL",
            "slug": "travel",
            "description": "Luxury travel guides and experiences with queer-friendly focus"
        },
        {
            "name": "TECHNOLOGY",
            "slug": "technology",
            "description": "Cutting-edge tech with luxury applications and queer innovation"
        },
        {
            "name": "LUXURY",
            "slug": "luxury",
            "description": "Fine timepieces, automobiles, real estate, and premium lifestyle"
        }
    ]
    
    # Create subsection tags for each main section
    subsections = {
        "fashion": [
            {"name": "Runway Report", "slug": "runway-report"},
            {"name": "Style Icons", "slug": "style-icons"},
            {"name": "Luxury Closet", "slug": "luxury-closet"},
            {"name": "Designer Spotlight", "slug": "designer-spotlight"},
            {"name": "Bespoke", "slug": "bespoke"}
        ],
        "art": [
            {"name": "Gallery", "slug": "gallery"},
            {"name": "Collector's Guide", "slug": "collectors-guide"},
            {"name": "Exhibition Reviews", "slug": "exhibition-reviews"},
            {"name": "Art Market", "slug": "art-market"},
            {"name": "Studio Visit", "slug": "studio-visit"}
        ],
        "culture": [
            {"name": "Screen", "slug": "screen"},
            {"name": "Page", "slug": "page"},
            {"name": "Stage", "slug": "stage"},
            {"name": "Sound", "slug": "sound"},
            {"name": "Digital", "slug": "digital-culture"}
        ],
        "travel": [
            {"name": "Destinations", "slug": "destinations"},
            {"name": "Properties", "slug": "properties"},
            {"name": "Experiences", "slug": "experiences"},
            {"name": "City Guide", "slug": "city-guide"},
            {"name": "Escape", "slug": "escape"}
        ],
        "technology": [
            {"name": "Innovation", "slug": "innovation"},
            {"name": "Digital Lifestyle", "slug": "digital-lifestyle"},
            {"name": "Future Forward", "slug": "future-forward"},
            {"name": "Tech Titans", "slug": "tech-titans"},
            {"name": "Design Objects", "slug": "design-objects"}
        ],
        "luxury": [
            {"name": "Timepieces", "slug": "timepieces"},
            {"name": "Automobiles", "slug": "automobiles"},
            {"name": "Real Estate", "slug": "real-estate"},
            {"name": "Spirits & Wine", "slug": "spirits-wine"},
            {"name": "Wellness", "slug": "wellness"}
        ]
    }
    
    # Create special feature tags
    features = [
        {"name": "Cover Story", "slug": "cover-story"},
        {"name": "Portfolio", "slug": "portfolio"},
        {"name": "Long-form", "slug": "long-form"},
        {"name": "Luxury Report", "slug": "luxury-report"},
        {"name": "Philanthropy", "slug": "philanthropy"}
    ]
    
    # Create issue tags for editorial calendar
    issues = [
        {"name": "January/February: Future Issue", "slug": "jan-feb-2025"},
        {"name": "March/April: Style Issue", "slug": "mar-apr-2025"},
        {"name": "May/June: Pride Issue", "slug": "may-jun-2025"},
        {"name": "July/August: Travel Issue", "slug": "jul-aug-2025"},
        {"name": "September/October: Design Issue", "slug": "sep-oct-2025"},
        {"name": "November/December: Luxury Issue", "slug": "nov-dec-2025"}
    ]
    
    # Create internal tags for workflow
    internal_tags = [
        {"name": "#draft", "slug": "hash-draft"},
        {"name": "#review", "slug": "hash-review"},
        {"name": "#ready", "slug": "hash-ready"},
        {"name": "#print", "slug": "hash-print"},
        {"name": "#digital-only", "slug": "hash-digital-only"},
        {"name": "#ai-enhanced", "slug": "hash-ai-enhanced"}
    ]
    
    # Create main section tags
    print("Creating main section tags...")
    for section in sections:
        try:
            result = client.create_tag(
                name=section["name"],
                slug=section["slug"],
                description=section["description"]
            )
            print(f"Created tag: {section['name']}")
        except Exception as e:
            print(f"Error creating tag {section['name']}: {str(e)}")
    
    # Create subsection tags
    print("\nCreating subsection tags...")
    for parent, subs in subsections.items():
        for sub in subs:
            try:
                result = client.create_tag(
                    name=sub["name"],
                    slug=sub["slug"],
                    description=f"Part of the {parent.upper()} section"
                )
                print(f"Created tag: {sub['name']}")
            except Exception as e:
                print(f"Error creating tag {sub['name']}: {str(e)}")
    
    # Create feature tags
    print("\nCreating feature tags...")
    for feature in features:
        try:
            result = client.create_tag(
                name=feature["name"],
                slug=feature["slug"],
                description="Special feature content"
            )
            print(f"Created tag: {feature['name']}")
        except Exception as e:
            print(f"Error creating tag {feature['name']}: {str(e)}")
    
    # Create issue tags
    print("\nCreating issue tags...")
    for issue in issues:
        try:
            result = client.create_tag(
                name=issue["name"],
                slug=issue["slug"],
                description="Bimonthly issue"
            )
            print(f"Created tag: {issue['name']}")
        except Exception as e:
            print(f"Error creating tag {issue['name']}: {str(e)}")
    
    # Create internal tags
    print("\nCreating internal tags...")
    for tag in internal_tags:
        try:
            result = client.create_tag(
                name=tag["name"],
                slug=tag["slug"],
                description="Internal workflow tag"
            )
            print(f"Created tag: {tag['name']}")
        except Exception as e:
            print(f"Error creating tag {tag['name']}: {str(e)}")
    
    # Update site settings
    print("\nUpdating site settings...")
    settings = {
        "settings": {
            "title": "Luxe Queer",
            "description": "Fashion, Art, Culture, Travel, Technology, and Luxury from a Queer Perspective",
            "meta_title": "Luxe Queer | Premium Queer Lifestyle Magazine",
            "meta_description": "The definitive luxury lifestyle magazine for the affluent queer community, covering fashion, art, culture, travel, technology, and luxury.",
            "navigation": [
                {"label": "FASHION", "url": "/tag/fashion/"},
                {"label": "ART", "url": "/tag/art/"},
                {"label": "CULTURE", "url": "/tag/culture/"},
                {"label": "TRAVEL", "url": "/tag/travel/"},
                {"label": "TECHNOLOGY", "url": "/tag/technology/"},
                {"label": "LUXURY", "url": "/tag/luxury/"}
            ],
            "secondary_navigation": [
                {"label": "Subscribe", "url": "#/portal/"},
                {"label": "About", "url": "/about/"}
            ]
        }
    }
    
    try:
        result = client.update_settings(settings)
        print("Site settings updated successfully")
    except Exception as e:
        print(f"Error updating site settings: {str(e)}")
    
    # Create welcome post
    print("\nCreating welcome post...")
    welcome_html = """
    <h2>Welcome to Luxe Queer</h2>
    
    <p>Luxe Queer is a premium lifestyle magazine for the affluent queer community, covering fashion, art, culture, travel, technology, and luxury from a distinctly queer perspective.</p>
    
    <p>Our magazine serves as both a cultural touchstone and a status symbol for our readers, who are discerning, affluent, and seeking content that speaks to their unique perspective.</p>
    
    <h3>Our Content</h3>
    
    <p>Luxe Queer publishes six issues per year, each with a distinct theme:</p>
    
    <ul>
        <li><strong>January/February:</strong> Future Issue (Technology & Innovation Focus)</li>
        <li><strong>March/April:</strong> Style Issue (Fashion Week Coverage)</li>
        <li><strong>May/June:</strong> Pride Issue (Culture & Community)</li>
        <li><strong>July/August:</strong> Travel Issue (Summer Destinations)</li>
        <li><strong>September/October:</strong> Design Issue (Art & Interiors)</li>
        <li><strong>November/December:</strong> Luxury Issue (Holiday & Year in Review)</li>
    </ul>
    
    <p>Each issue features in-depth coverage across our core sections:</p>
    
    <ul>
        <li><strong>FASHION:</strong> High-end fashion editorials and analysis with a queer lens</li>
        <li><strong>ART:</strong> Contemporary art showcases and critical analysis from queer perspectives</li>
        <li><strong>CULTURE:</strong> Film, literature, music, and performance through a queer lens</li>
        <li><strong>TRAVEL:</strong> Luxury travel guides and experiences with queer-friendly focus</li>
        <li><strong>TECHNOLOGY:</strong> Cutting-edge tech with luxury applications and queer innovation</li>
        <li><strong>LUXURY:</strong> Fine timepieces, automobiles, real estate, and premium lifestyle</li>
    </ul>
    
    <p>Subscribe now to receive our inaugural issue and join our community of discerning readers who appreciate the finer things in life through a queer lens.</p>
    """
    
    try:
        result = client.create_post(
            title="Welcome to Luxe Queer Magazine",
            html_content=welcome_html,
            status="published",
            featured=True
        )
        print("Welcome post created successfully")
    except Exception as e:
        print(f"Error creating welcome post: {str(e)}")
    
    # Create about page
    print("\nCreating about page...")
    about_html = """
    <h2>About Luxe Queer</h2>
    
    <p>Luxe Queer is a premium lifestyle magazine for the affluent queer community, published 6 times per year in both print and digital formats.</p>
    
    <h3>Our Mission</h3>
    
    <p>At Luxe Queer, we believe that luxury and queer identity are not mutually exclusive but rather complementary facets of a rich, multidimensional life. Our mission is to celebrate queer excellence, creativity, and influence in premium spaces, providing sophisticated content that resonates with our readers' unique perspectives.</p>
    
    <h3>Our Vision</h3>
    
    <p>We envision a world where queer voices are prominently featured in conversations about luxury, design, and high culture. Luxe Queer aims to be the definitive source for discerning queer individuals seeking content that reflects both their sophisticated tastes and their identities.</p>
    
    <h3>Our Values</h3>
    
    <ul>
        <li><strong>Excellence:</strong> We maintain the highest standards in our content, design, and presentation.</li>
        <li><strong>Authenticity:</strong> We present genuine queer perspectives without compromise.</li>
        <li><strong>Inclusivity:</strong> While focusing on luxury, we recognize and celebrate the diversity within the queer community.</li>
        <li><strong>Innovation:</strong> We embrace new ideas, technologies, and approaches in both our content and our operations.</li>
        <li><strong>Sustainability:</strong> We are committed to responsible luxury that considers environmental and social impact.</li>
    </ul>
    
    <h3>Our Team</h3>
    
    <p>Luxe Queer is created by a diverse team of queer journalists, photographers, designers, and editors, all experts in their respective fields. Our content is further enhanced by our innovative AI agent team, which assists with research and content creation while maintaining human oversight and creative direction.</p>
    
    <h3>Contact Us</h3>
    
    <p>For editorial inquiries, advertising opportunities, or subscription information, please contact us at info@luxequeer.com.</p>
    """
    
    try:
        result = client.create_post(
            title="About Luxe Queer",
            html_content=about_html,
            status="published",
            featured=False
        )
        print("About page created successfully")
    except Exception as e:
        print(f"Error creating about page: {str(e)}")
    
    print("\nGhost CMS configuration for Luxe Queer magazine completed successfully!")

if __name__ == "__main__":
    # Ghost instance URL
    ghost_url = "https://rainbow-millipede.pikapod.net"
    
    # Updated API credentials
    admin_key = "67ef67107bdbb900014522e2:a83281ff2c5c9eb4ee94242f87cd1e8ace9d4cb9317358acda25f8ec1f266d73"
    content_key = "bbc75241a46836b87673d05b12"
    
    # Initialize the client
    client = GhostApiClient(ghost_url, admin_key, content_key)
    
    # Configure the magazine structure
    configure_magazine_structure(client)
