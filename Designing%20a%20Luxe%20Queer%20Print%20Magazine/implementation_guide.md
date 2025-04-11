# Luxe Queer Magazine: Comprehensive Implementation Guide

## Introduction

This comprehensive guide provides detailed instructions for implementing and managing all aspects of Luxe Queer magazine. It consolidates the design, technical setup, content creation, and operational workflows necessary to run a sophisticated luxury queer publication across both digital and print formats.

## Table of Contents

1. [Ghost CMS Setup and Configuration](#1-ghost-cms-setup-and-configuration)
2. [Design Implementation](#2-design-implementation)
3. [Content Management](#3-content-management)
4. [Print Publication Workflow](#4-print-publication-workflow)
5. [AI Agent Integration](#5-ai-agent-integration)
6. [Editorial Calendar and Publication Schedule](#6-editorial-calendar-and-publication-schedule)
7. [Technical Maintenance](#7-technical-maintenance)
8. [Troubleshooting](#8-troubleshooting)

## 1. Ghost CMS Setup and Configuration

### Accessing Your Ghost Instance

Your Ghost CMS instance is hosted at:
- URL: https://rainbow-millipede.pikapod.net
- Admin API Key: 67ef67107bdbb900014522e2:a83281ff2c5c9eb4ee94242f87cd1e8ace9d4cb9317358acda25f8ec1f266d73
- Content API Key: bbc75241a46836b87673d05b12

To access the admin interface:
1. Navigate to https://rainbow-millipede.pikapod.net/ghost/
2. Log in with your administrator credentials

### Tag Structure Implementation

The magazine uses a hierarchical tag structure:

1. **Main Section Tags**:
   - FASHION
   - ART
   - CULTURE
   - TRAVEL
   - TECHNOLOGY
   - LUXURY

2. **Subsection Tags**:
   - Fashion: Runway Report, Designer Profile, Style Guide, Trend Forecast
   - Art: Gallery, Studio Visit, Exhibition Review, Artist Profile
   - Culture: Screen, Stage, Literature, Music
   - Travel: Destination, Hotel Review, Travel Essay, City Guide
   - Technology: Innovation, Digital Life, Product Review, Future Forward
   - Luxury: Objects of Desire, Connoisseurship, Heritage, Craftsmanship

3. **Special Feature Tags**:
   - Cover Story
   - Portfolio
   - Long-form
   - Interview
   - Photo Essay
   - Luxury Report
   - Philanthropy

4. **Issue Tags**:
   - jan-feb-2025
   - mar-apr-2025
   - may-jun-2025
   - jul-aug-2025
   - sep-oct-2025
   - nov-dec-2025

5. **Internal Workflow Tags** (prefixed with #):
   - #draft
   - #review
   - #ready
   - #print
   - #digital-only
   - #ai-enhanced

To implement this tag structure:
1. Go to Ghost Admin > Settings > Tags
2. Click "New tag" to create each tag
3. For main section tags, use all caps (e.g., "FASHION")
4. For internal tags, use the # prefix (e.g., "#draft")
5. Add descriptions to each tag for clarity

### Navigation Setup

To configure the site navigation:
1. Go to Ghost Admin > Settings > Navigation
2. Add the following items to the Primary Navigation:
   - FASHION: https://rainbow-millipede.pikapod.net/tag/fashion/
   - ART: https://rainbow-millipede.pikapod.net/tag/art/
   - CULTURE: https://rainbow-millipede.pikapod.net/tag/culture/
   - TRAVEL: https://rainbow-millipede.pikapod.net/tag/travel/
   - TECHNOLOGY: https://rainbow-millipede.pikapod.net/tag/technology/
   - LUXURY: https://rainbow-millipede.pikapod.net/tag/luxury/
   - ABOUT: https://rainbow-millipede.pikapod.net/about/
   - SUBSCRIBE: https://rainbow-millipede.pikapod.net/#/portal/

3. Add the following items to the Secondary Navigation:
   - Current Issue: https://rainbow-millipede.pikapod.net/tag/jan-feb-2025/
   - Archive: https://rainbow-millipede.pikapod.net/archive/
   - Contact: https://rainbow-millipede.pikapod.net/contact/

### Site Settings Configuration

To configure general site settings:
1. Go to Ghost Admin > Settings > General
2. Set the following:
   - Title: Luxe Queer
   - Description: Fashion, Art, Culture, Travel, Technology, and Luxury from a Queer Perspective
   - Meta title: Luxe Queer | Premium Lifestyle Magazine for the Affluent Queer Community
   - Meta description: Luxe Queer explores fashion, art, culture, travel, technology, and luxury through a sophisticated queer lens, celebrating excellence and innovation.

## 2. Design Implementation

### Uploading Theme Files

To implement the custom theme:
1. Download the theme files from your local directory:
   - `/home/ubuntu/luxe_queer/templates/default.hbs`
   - `/home/ubuntu/luxe_queer/design/luxe_queer_theme.css`

2. Create a ZIP file containing these files with the proper Ghost theme structure:
   ```
   luxe-queer-theme.zip
   ├── assets
   │   └── css
   │       └── luxe_queer_theme.css
   ├── default.hbs
   ├── index.hbs
   ├── post.hbs
   ├── tag.hbs
   └── package.json
   ```

3. Go to Ghost Admin > Settings > Theme
4. Click "Upload a theme" and select your ZIP file
5. After upload, click "Activate"

### Customizing Design Elements

To customize specific design elements:
1. Go to Ghost Admin > Settings > Design
2. Under "Brand", upload:
   - Logo: A high-resolution version of the Luxe Queer logo
   - Icon: A square icon version of the logo
   - Accent color: #7D2027 (deep wine red)

3. Under "Site-wide", configure:
   - Header and footer information
   - Social media accounts
   - Publication cover image

### Creating Page Templates

To create templates for special pages:
1. Go to Ghost Admin > Pages > New page
2. Create the following pages:
   - About: Information about the magazine's mission and team
   - Contact: Contact information and submission guidelines
   - Archive: A catalog of past issues
   - Subscribe: Subscription options and benefits

3. For each page, use the appropriate custom template by selecting it from the settings panel

## 3. Content Management

### Content Creation Workflow

The content creation process follows these steps:
1. **Planning**: Assign articles based on the editorial calendar
2. **Research**: Gather information, conduct interviews, collect visual assets
3. **Drafting**: Create initial content, either by human writers or AI collaboration
4. **Editing**: Review and refine content for quality and alignment with brand voice
5. **Design**: Format content and integrate visual elements
6. **Approval**: Final review by editor-in-chief
7. **Publication**: Schedule for digital release and include in print issue

### Uploading Articles

To upload the sample articles:
1. Go to Ghost Admin > Posts > New post
2. For each article file (e.g., `/home/ubuntu/luxe_queer/content/cover_story.md`):
   - Copy the content
   - Paste into the Ghost editor
   - Add appropriate tags (main section, subsection, issue tag)
   - Add featured image
   - Set publication status (draft, scheduled, or published)

### Managing Images and Media

To upload and manage images:
1. Prepare images in appropriate formats:
   - Feature images: 2000px wide, JPG format
   - In-article images: 1200px wide, JPG format
   - Logos and icons: PNG format with transparency

2. When editing a post, click the "+" button and select "Image"
3. Upload your image or select from the media library
4. Add appropriate alt text and captions

### Content Pillars and Keywords

Based on your provided guidelines, implement these content pillars and keywords:

**Main Content Pillars**:
- Luxury Fashion
- Queer Culture/History
- Contemporary Art
- Tech Innovation
- Artist Profiles
- Designer Spotlights
- Event Coverage
- Critical Commentary

**Keywords**:
- Androgynous fashion
- Digital couture
- Queer resilience
- Intersectionality
- Luxury craftsmanship
- AI art
- Sustainable luxury
- Non-binary beauty
- Archival fashion
- Disruptive tech

When creating content, ensure it aligns with these pillars and incorporates relevant keywords naturally.

### Style and Voice Guide

Implement this style and voice guide for all content:

**Tone**:
- Sophisticated
- Insightful
- Vibrant
- Critical yet celebratory
- Inclusive
- Forward-looking

**Sentence Structure**:
- Mix of short, impactful sentences and longer, analytical ones
- Avoid overly academic language while maintaining intellectual depth
- Maintain a high level of sophistication appropriate for affluent readers

**Terminology**:
- Use inclusive language
- Employ industry-specific terminology accurately
- Balance accessibility with sophistication

### Target Audience Persona

Keep this audience persona in mind when creating content:

"Culturally engaged, aesthetically driven individuals interested in the cutting edge of art, tech, and fashion, with a nuanced understanding of queer issues. Appreciates both luxury heritage and disruptive innovation."

### Trusted Sources and Inspirations

Reference these trusted sources for research and inspiration:
- Business of Fashion
- Artforum
- Vogue
- Frieze
- Wallpaper
- Dezeen
- MIT Technology Review
- Travel + Leisure
- Architectural Digest
- Museum archives (MoMA, Tate, Centre Pompidou)
- Academic journals on queer theory and cultural studies

## 4. Print Publication Workflow

### Setting Up the Print Environment

To set up the print publication environment:
1. Install required dependencies:
   ```bash
   pip install weasyprint requests
   ```

2. Upload the print workflow script:
   - Source: `/home/ubuntu/luxe_queer/api/print_workflow.py`
   - Destination: Your server environment

3. Create output directories:
   ```bash
   mkdir -p /path/to/your/server/luxe_queer/print/pdf
   mkdir -p /path/to/your/server/luxe_queer/print/indesign
   ```

### Generating PDF Issues

To generate a PDF for an issue:
1. Ensure all content for the issue is published in Ghost and tagged with the appropriate issue tag
2. Run the print workflow script:
   ```bash
   python print_workflow.py --issue jan-feb-2025 --title "January/February 2025: Future Issue"
   ```

3. The script will:
   - Fetch all posts with the specified issue tag
   - Generate a formatted PDF with cover, table of contents, and articles
   - Save the PDF to the output directory

### Exporting for InDesign

For more advanced layout in InDesign:
1. Run the export function in the print workflow script:
   ```bash
   python print_workflow.py --issue jan-feb-2025 --export-indesign
   ```

2. The script will:
   - Create a directory for the issue
   - Export each article as HTML and JSON with metadata
   - Generate a manifest file listing all articles

3. Import the exported files into InDesign:
   - Use the HTML files for content
   - Use the JSON files for metadata
   - Follow the manifest for article order

### Print Production Process

The print production process follows these steps:
1. **Content Freeze**: Finalize all content for the issue
2. **PDF Generation**: Create the initial PDF using the workflow script
3. **InDesign Layout**: Import content into InDesign for advanced layout
4. **Design Review**: Review and refine the layout
5. **Proofing**: Generate printer proofs for review
6. **Approval**: Final approval by editor-in-chief
7. **Printing**: Send to printer with appropriate specifications
8. **Distribution**: Ship to subscribers and distribution points

## 5. AI Agent Integration

### Setting Up AI Integration

To set up the AI agent integration:
1. Upload the AI integration script:
   - Source: `/home/ubuntu/luxe_queer/api/ai_integration.py`
   - Destination: Your server environment

2. Create output directory:
   ```bash
   mkdir -p /path/to/your/server/luxe_queer/ai_integration
   ```

3. Install required dependencies:
   ```bash
   pip install requests json
   ```

### AI Agent Team Configuration

Configure the AI agent team according to their specialties:

1. **Cohere Agent**:
   - Specialty: Long-form content generation and semantic search
   - Best for: Research, article drafting, content enhancement
   - API setup: [Cohere API documentation](https://docs.cohere.com/)

2. **Anthropic Claude**:
   - Specialty: Nuanced cultural analysis and ethical considerations
   - Best for: Cultural analysis, trend forecasting, ethical review
   - API setup: [Anthropic API documentation](https://docs.anthropic.com/)

3. **NVIDIA AI**:
   - Specialty: Visual content analysis and generation
   - Best for: Image analysis, visual trend detection, style recommendations
   - API setup: [NVIDIA API documentation](https://developer.nvidia.com/)

4. **Hermes Agent**:
   - Specialty: Multilingual content and international perspectives
   - Best for: Translation, international trends, global market analysis
   - Implementation based on provided guidelines

5. **Hume AI**:
   - Specialty: Emotional intelligence and reader engagement
   - Best for: Sentiment analysis, engagement optimization, audience insights
   - API setup: [Hume AI documentation](https://hume.ai/docs)

6. **Mistral AI**:
   - Specialty: Technical writing and technology trend analysis
   - Best for: Tech reporting, product reviews, technical accuracy
   - API setup: [Mistral AI documentation](https://mistral.ai/)

7. **Gemma Agent**:
   - Specialty: Data analysis and visualization
   - Best for: Data analysis, chart generation, statistical insights
   - API setup: [Gemma documentation](https://ai.google.dev/gemma)

8. **Hugging Face Agent**:
   - Specialty: Content classification and organization
   - Best for: Content tagging, categorization, metadata enhancement
   - API setup: [Hugging Face documentation](https://huggingface.co/docs)

9. **Llama Agent**:
   - Specialty: Creative writing and narrative development
   - Best for: Storytelling, creative features, narrative structure
   - API setup: [Llama documentation](https://llama.meta.com/)

### Prompting Protocols for Hermes

Based on your provided guidelines, use these prompting protocols for Hermes:

**Structure your prompts with**:
- **Role**: "Act as a fashion journalist specializing in..."
- **Task**: "Draft an introduction for an article about..."
- **Context**: "The article focuses on the intersection of queer identity and digital fashion..."
- **Format**: "Provide 5 bullet points." "Write a 300-word summary." "Generate 10 potential headlines."
- **Tone/Style**: Reference the style guide

**Example prompts**:
- "Generate article ideas within our 'Contemporary Art' and 'Queer Culture' pillars."
- "Write in a sophisticated yet vibrant tone, reflecting the style guide provided."
- "Avoid overly academic language but maintain intellectual depth."
- "Generate headlines appealing to an audience interested in both luxury heritage and disruptive tech."
- "Prioritize information from sources like Business of Fashion, Artforum, specific museum archives, reputable tech journals."
- "Analyze the recent collections of [Designer X] based on reviews from [Publication Y and Z]."
- "Using the provided 'Artist Profile Template,' draft sections 1-3 for [Artist Name] focusing on their work's connection to queer themes."

### Content Attribution Guidelines

Follow these guidelines for attributing AI contributions:

1. **Level 1: Tool Assistance**:
   - Definition: AI used for research, editing assistance, or minor enhancements
   - Attribution: No specific attribution required in article
   - Internal Tracking: Tagged as "#ai-assisted" in CMS

2. **Level 2: Collaborative Creation**:
   - Definition: Substantial portions drafted by AI but significantly edited by humans
   - Attribution: "Written by [Human Author] with assistance from [AI System]"
   - Internal Tracking: Tagged as "#ai-collaborative" in CMS

3. **Level 3: AI-Led Creation**:
   - Definition: Primarily AI-generated with human editing and oversight
   - Attribution: "Created by [AI System], edited by [Human Editor]"
   - Internal Tracking: Tagged as "#ai-generated" in CMS

### AI Workflow Integration

Implement this workflow for AI content creation:

1. **Content Planning**:
   - Define article topic, angle, and objectives
   - Select appropriate AI agents based on content type
   - Create detailed brief for AI assistance

2. **Research Phase**:
   - Use Cohere Agent for semantic search across sources
   - Use Hugging Face Agent to organize research findings
   - Use Hermes Agent for international perspectives

3. **Content Creation**:
   - Use selected AI agents to generate initial drafts
   - Human editors review and provide feedback
   - Revise content based on editorial direction

4. **Quality Control**:
   - Human editors review for factual accuracy
   - Check for alignment with brand voice and style
   - Ensure proper attribution of AI contributions

5. **Publication**:
   - Add appropriate AI attribution
   - Tag with relevant AI workflow tags
   - Schedule for publication

## 6. Editorial Calendar and Publication Schedule

### Annual Editorial Calendar

Follow this editorial calendar for the six annual issues:

| Issue | Theme | Publication Date | Content Deadline | Print Deadline |
|-------|-------|-----------------|-----------------|----------------|
| January/February | Future Issue (Technology & Innovation) | January 1 | November 15 | December 1 |
| March/April | Style Issue (Fashion Week Coverage) | March 1 | January 15 | February 1 |
| May/June | Pride Issue (Culture & Community) | May 1 | March 15 | April 1 |
| July/August | Travel Issue (Summer Destinations) | July 1 | May 15 | June 1 |
| September/October | Design Issue (Art & Interiors) | September 1 | July 15 | August 1 |
| November/December | Luxury Issue (Holiday & Year in Review) | November 1 | September 15 | October 1 |

### Production Timeline

For each issue, follow this production timeline:

**Planning Phase (12-14 weeks before publication)**:
- Week 1: Editorial planning meeting
- Week 2: Section editors submit content proposals
- Week 3: AI agent team provides trend analysis
- Week 4: Final content plan approved

**Content Creation Phase (8-12 weeks before publication)**:
- Week 5-6: Research and interviews
- Week 7-8: Initial drafts created
- Week 9: Section editors review drafts
- Week 10: Revisions completed

**Visual and Design Phase (6-8 weeks before publication)**:
- Week 11: Photo shoots and visual asset creation
- Week 12: Initial layout design
- Week 13: Design review and refinement
- Week 14: Final visual assets approved

**Editing and Refinement Phase (4-6 weeks before publication)**:
- Week 15: Copy editing and fact-checking
- Week 16: Final content approval
- Week 17: Proofreading
- Week 18: Final corrections implemented

**Production Phase (2-4 weeks before publication)**:
- Week 19: Digital version finalized in Ghost CMS
- Week 20: Print files prepared
- Week 21: Printer proofs reviewed
- Week 22: Printing and binding

**Distribution Phase (0-2 weeks before publication)**:
- Week 23: Digital version published
- Week 24: Print copies shipped

### Content Planning Templates

Use these templates for content planning:

**Article Brief Template**:
```
Title: [Proposed Title]
Section: [Main Section]
Subsection: [Subsection]
Word Count: [Target Word Count]
Author: [Human Author]
AI Support: [AI Agents to be Used]
Key Angle: [Main Perspective or Hook]
Sources: [Key References and Research Sources]
Visual Elements: [Required Images, Graphics, etc.]
Deadline: [Submission Date]
```

**AI Assignment Template**:
```
Task: [Specific Task for AI]
Content Pillar: [Relevant Content Pillar]
Keywords: [Relevant Keywords]
Tone: [Specific Tone Guidelines]
Format: [Output Format Requirements]
References: [Trusted Sources to Prioritize]
Context: [Background Information]
Deadline: [Completion Date]
```

## 7. Technical Maintenance

### Regular Maintenance Tasks

Perform these maintenance tasks regularly:

**Weekly**:
- Backup Ghost content database
- Check for Ghost CMS updates
- Monitor site performance and loading times
- Review error logs

**Monthly**:
- Apply Ghost updates (if available)
- Test all site functionality
- Verify API integrations are working
- Update SSL certificates if needed

**Quarterly**:
- Comprehensive security audit
- Database optimization
- Content audit and cleanup
- Performance optimization

### Backup Procedures

Implement these backup procedures:

1. **Automated Backups**:
   - Configure daily automated backups of the Ghost database
   - Store backups in multiple locations (local and cloud)
   - Retain at least 30 days of backup history

2. **Manual Backups**:
   - Perform manual backups before major updates
   - Export content using Ghost's export functionality
   - Back up theme files and custom code

3. **Restoration Testing**:
   - Quarterly test of backup restoration process
   - Verify integrity of backed-up data
   - Document restoration procedures

## 8. Troubleshooting

### Common Issues and Solutions

**Ghost CMS Issues**:

1. **Content Not Publishing**:
   - Check scheduled publication date
   - Verify user has publishing permissions
   - Check for validation errors in content

2. **Images Not Displaying**:
   - Verify image was properly uploaded
   - Check image URL for errors
   - Confirm image format is supported

3. **Theme Not Applying**:
   - Clear browser cache
   - Verify theme is activated
   - Check for JavaScript errors

**Print Workflow Issues**:

1. **PDF Generation Fails**:
   - Check for missing dependencies
   - Verify API credentials are correct
   - Check for malformed content

2. **InDesign Export Problems**:
   - Verify content structure is valid
   - Check for special characters causing issues
   - Ensure all images are accessible

**AI Integration Issues**:

1. **API Connection Failures**:
   - Verify API keys are current
   - Check network connectivity
   - Confirm API endpoint URLs are correct

2. **Content Quality Issues**:
   - Refine prompting techniques
   - Adjust AI parameters for better output
   - Increase human editing involvement

### Support Resources

**Technical Support**:
- Ghost CMS Documentation: https://ghost.org/docs/
- Ghost Forum: https://forum.ghost.org/
- WeasyPrint Documentation: https://doc.courtbouillon.org/weasyprint/

**AI Services Support**:
- Cohere Documentation: https://docs.cohere.com/
- Anthropic Documentation: https://docs.anthropic.com/
- NVIDIA Documentation: https://developer.nvidia.com/
- Hume AI Documentation: https://hume.ai/docs
- Mistral Documentation: https://mistral.ai/
- Gemma Documentation: https://ai.google.dev/gemma
- Hugging Face Documentation: https://huggingface.co/docs
- Llama Documentation: https://llama.meta.com/

**Custom Support**:
- Contact your technical administrator for issues with custom code
- Refer to internal documentation for custom workflows

## Conclusion

This comprehensive implementation guide provides all the information needed to set up, manage, and maintain Luxe Queer magazine. By following these instructions, you can ensure a consistent, high-quality publication that effectively delivers sophisticated content to affluent queer readers interested in fashion, art, culture, travel, technology, and luxury.

The integration of Ghost CMS, custom design, print workflow, and AI agent collaboration creates a modern publishing platform capable of producing exceptional content across both digital and print formats, establishing Luxe Queer as a distinctive voice in the luxury publishing landscape.
