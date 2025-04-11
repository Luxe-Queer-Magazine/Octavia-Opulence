#!/usr/bin/env python3

import os
import json
import requests
from ghost_api_client import GhostApiClient
from weasyprint import HTML, CSS
from datetime import datetime

class PrintPublicationWorkflow:
    def __init__(self, client, output_dir):
        """Initialize the print publication workflow with a Ghost API client and output directory"""
        self.client = client
        self.output_dir = output_dir
        self.css_path = os.path.join(output_dir, 'print_styles.css')
        self.create_print_css()
        
        # Ensure output directories exist
        os.makedirs(os.path.join(output_dir, 'pdf'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'indesign'), exist_ok=True)
    
    def create_print_css(self):
        """Create CSS for print styling"""
        css_content = """
        @page {
            margin: 1cm;
            size: 9in 12in;
            @bottom-center {
                content: "Luxe Queer Magazine";
            }
            @bottom-right {
                content: counter(page);
            }
        }
        
        body {
            font-family: 'Garamond', serif;
            font-size: 12pt;
            line-height: 1.5;
            color: #000000;
        }
        
        h1 {
            font-family: 'Didot', serif;
            font-size: 24pt;
            margin-top: 1cm;
            margin-bottom: 0.5cm;
            page-break-after: avoid;
        }
        
        h2 {
            font-family: 'Didot', serif;
            font-size: 18pt;
            margin-top: 0.8cm;
            margin-bottom: 0.4cm;
            page-break-after: avoid;
        }
        
        h3 {
            font-family: 'Didot', serif;
            font-size: 14pt;
            margin-top: 0.6cm;
            margin-bottom: 0.3cm;
            page-break-after: avoid;
        }
        
        p {
            margin-bottom: 0.4cm;
            text-align: justify;
            hyphens: auto;
        }
        
        img {
            max-width: 100%;
            height: auto;
            margin: 0.5cm 0;
        }
        
        blockquote {
            font-family: 'Futura', sans-serif;
            font-size: 14pt;
            border-left: 3px solid #7D2027;
            padding-left: 0.5cm;
            margin: 0.5cm 0;
            color: #7D2027;
        }
        
        .article-meta {
            font-size: 10pt;
            color: #666666;
            margin-bottom: 0.5cm;
        }
        
        .article-tag {
            font-family: 'Futura', sans-serif;
            font-size: 9pt;
            text-transform: uppercase;
            color: #7D2027;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        .two-column {
            column-count: 2;
            column-gap: 0.5cm;
        }
        
        .caption {
            font-size: 9pt;
            font-style: italic;
            text-align: center;
            margin-top: 0.2cm;
        }
        
        .toc-entry {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.2cm;
        }
        
        .toc-page {
            font-weight: bold;
        }
        
        .cover-page {
            text-align: center;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        
        .cover-title {
            font-family: 'Didot', serif;
            font-size: 36pt;
            margin-bottom: 0.5cm;
        }
        
        .cover-subtitle {
            font-family: 'Garamond', serif;
            font-size: 18pt;
            font-style: italic;
            margin-bottom: 1cm;
        }
        
        .cover-issue {
            font-family: 'Futura', sans-serif;
            font-size: 14pt;
            text-transform: uppercase;
            letter-spacing: 0.1cm;
        }
        """
        
        with open(self.css_path, 'w') as f:
            f.write(css_content)
    
    def generate_issue_pdf(self, issue_tag, title=None):
        """Generate a PDF for a specific issue based on its tag"""
        # Get posts for this issue
        posts = self.client.get_posts(limit=100, filter=f"tag:{issue_tag}")
        
        if 'posts' not in posts or not posts['posts']:
            print(f"No posts found for issue tag: {issue_tag}")
            return None
        
        # Determine issue title if not provided
        if not title:
            # Try to find the issue tag object to get its name
            tags = self.client.get_tags()
            issue_tag_obj = next((tag for tag in tags.get('tags', []) if tag['slug'] == issue_tag), None)
            title = issue_tag_obj['name'] if issue_tag_obj else f"Luxe Queer - {issue_tag}"
        
        # Create HTML for the issue
        html_content = self.create_issue_html(posts['posts'], title)
        
        # Generate PDF filename
        current_date = datetime.now().strftime("%Y%m%d")
        pdf_filename = f"luxe_queer_{issue_tag}_{current_date}.pdf"
        pdf_path = os.path.join(self.output_dir, 'pdf', pdf_filename)
        
        # Generate PDF
        html = HTML(string=html_content)
        css = CSS(filename=self.css_path)
        html.write_pdf(pdf_path, stylesheets=[css])
        
        print(f"PDF generated: {pdf_path}")
        return pdf_path
    
    def create_issue_html(self, posts, title):
        """Create HTML content for the issue"""
        # Sort posts by section and importance
        # For a real implementation, we would have a more sophisticated sorting mechanism
        posts.sort(key=lambda x: x.get('featured', False), reverse=True)
        
        # Create cover page
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
        </head>
        <body>
            <div class="cover-page">
                <div class="cover-issue">Luxe Queer Magazine</div>
                <h1 class="cover-title">{title}</h1>
                <div class="cover-subtitle">Fashion, Art, Culture, Travel, Technology, and Luxury from a Queer Perspective</div>
                <div class="cover-issue">{datetime.now().strftime("%B %Y")}</div>
            </div>
            
            <div class="page-break"></div>
            
            <h1>Table of Contents</h1>
        """
        
        # Add table of contents
        page_counter = 3  # Start after cover and TOC
        toc_entries = []
        
        for i, post in enumerate(posts):
            # Estimate page count (very rough approximation)
            content_length = len(post.get('html', ''))
            estimated_pages = max(1, content_length // 3000)
            
            toc_entries.append({
                'title': post.get('title', 'Untitled'),
                'page': page_counter
            })
            
            page_counter += estimated_pages
        
        # Add TOC entries to HTML
        for entry in toc_entries:
            html += f"""
            <div class="toc-entry">
                <span class="toc-title">{entry['title']}</span>
                <span class="toc-page">{entry['page']}</span>
            </div>
            """
        
        # Add articles
        for i, post in enumerate(posts):
            html += f"""
            <div class="page-break"></div>
            
            <article>
                <div class="article-tag">{post.get('primary_tag', {}).get('name', '')}</div>
                <h1>{post.get('title', 'Untitled')}</h1>
                
                <div class="article-meta">
                    By {post.get('primary_author', {}).get('name', 'Anonymous')} | 
                    {post.get('published_at', '').split('T')[0]}
                </div>
                
                <div class="two-column">
                    {post.get('html', '')}
                </div>
            </article>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def export_for_indesign(self, issue_tag):
        """Export content in a format suitable for InDesign import"""
        # Get posts for this issue
        posts = self.client.get_posts(limit=100, filter=f"tag:{issue_tag}")
        
        if 'posts' not in posts or not posts['posts']:
            print(f"No posts found for issue tag: {issue_tag}")
            return None
        
        # Create a directory for this issue
        current_date = datetime.now().strftime("%Y%m%d")
        issue_dir = os.path.join(self.output_dir, 'indesign', f"{issue_tag}_{current_date}")
        os.makedirs(issue_dir, exist_ok=True)
        
        # Export each article as individual HTML and JSON
        for post in posts['posts']:
            post_slug = post.get('slug', 'article')
            
            # Export HTML
            html_path = os.path.join(issue_dir, f"{post_slug}.html")
            with open(html_path, 'w') as f:
                f.write(post.get('html', ''))
            
            # Export metadata as JSON
            meta = {
                'title': post.get('title', 'Untitled'),
                'author': post.get('primary_author', {}).get('name', 'Anonymous'),
                'date': post.get('published_at', '').split('T')[0],
                'tags': [tag.get('name', '') for tag in post.get('tags', [])],
                'excerpt': post.get('excerpt', ''),
                'feature_image': post.get('feature_image', '')
            }
            
            json_path = os.path.join(issue_dir, f"{post_slug}.json")
            with open(json_path, 'w') as f:
                json.dump(meta, f, indent=2)
        
        # Create a manifest file
        manifest = {
            'issue': issue_tag,
            'date': current_date,
            'articles': [post.get('slug', 'article') for post in posts['posts']]
        }
        
        manifest_path = os.path.join(issue_dir, 'manifest.json')
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"InDesign export completed: {issue_dir}")
        return issue_dir

# Example usage
if __name__ == "__main__":
    # Ghost instance URL
    ghost_url = "https://rainbow-millipede.pikapod.net"
    
    # Updated API credentials
    admin_key = "67ef67107bdbb900014522e2:a83281ff2c5c9eb4ee94242f87cd1e8ace9d4cb9317358acda25f8ec1f266d73"
    content_key = "bbc75241a46836b87673d05b12"
    
    # Initialize the client
    client = GhostApiClient(ghost_url, admin_key, content_key)
    
    # Initialize the print workflow
    output_dir = "/home/ubuntu/luxe_queer/print"
    workflow = PrintPublicationWorkflow(client, output_dir)
    
    # Generate PDF for the first issue (using the tag slug)
    pdf_path = workflow.generate_issue_pdf("jan-feb-2025", "January/February 2025: Future Issue")
    
    # Export for InDesign
    indesign_dir = workflow.export_for_indesign("jan-feb-2025")
