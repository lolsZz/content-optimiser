import re  # Add missing import at the top of the file

# Define missing patterns that are referenced later in the file
SCRAPER_WARNING_PATTERN = re.compile(
    r'(?i)(?:This content was automatically scraped|Do not scrape|Web scraping not allowed|Crawling not permitted|Data extraction prohibited)',
    re.IGNORECASE
)

PUBLISHED_TIME_PATTERN = re.compile(
    r'(?i)(?:Published|Posted on|Last updated)(?:\s*(?:at|on))?:?\s*\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)?',
    re.MULTILINE
)

WP_TRACKING_PIXEL_PATTERN = re.compile(
    r'<img[^>]+(?:tracking|pixel|analytics|stats)[^>]*>|<img[^>]+height=["\']?1["\']?[^>]+width=["\']?1["\']?[^>]*>|<img[^>]+width=["\']?1["\']?[^>]+height=["\']?1["\']?[^>]*>',
    re.IGNORECASE
)

META_TITLE_URL_PATTERN = re.compile(
    r'^(?:Title|URL|Source):\s+\S+.*$',
    re.MULTILINE
)

WP_COMMENT_PROMPT_PATTERN = re.compile(
    r'(?:Leave a (?:comment|reply)|Add your comment|Post a comment|Comments below|Share your thoughts).*?(?:below|\.|$)',
    re.IGNORECASE
)

WP_COOKIE_NOTICE_PATTERN = re.compile(
    r'(?:This (?:website|site) uses cookies|We use cookies|Cookie Policy|Accept cookies|We value your privacy).*?(?:experience|setting|privacy|policy|\.|$)',
    re.IGNORECASE
)

GITHUB_LINK_PATTERN = re.compile(
    r'^\s*(?:GitHub|Repository|Source code):\s+https?://(?:www\.)?github\.com/[^/\s]+/[^/\s]+\s*$',
    re.MULTILINE | re.IGNORECASE
)

REDUNDANT_HEADERS_PATTERN = re.compile(
    r'^(?:#+ .+)\n+(?:#+ .+)$',  # Match adjacent headers with no content between them
    re.MULTILINE
)

WEEBLY_HEADER_TABLE_PATTERN = re.compile(
    r'<table[^>]*weebly[^>]*>.*?</table>|<table[^>]*>.*?(?:Logo|Home|About|Contact|Services).*?</table>',
    re.IGNORECASE | re.DOTALL
)

MODAL_DOCS_HEADER_PATTERN = re.compile(
    r'---\s*\ntitle:.*?\n(?:description:.*?\n)?(?:date:.*?\n)?(?:tags:.*?\n)?(?:categories:.*?\n)?(?:slug:.*?\n)?(?:authors:.*?\n)?---\s*\n+',
    re.DOTALL
)

WP_NAV_LIST_PATTERN = re.compile(
    r'<(?:ul|ol)[^>]*(?:menu|navigation)[^>]*>.*?</(?:ul|ol)>',
    re.IGNORECASE | re.DOTALL
)

WP_SIDEBAR_SECTIONS_PATTERN = re.compile(
    r'<(?:div|section|aside)[^>]*(?:sidebar|widget-area)[^>]*>.*?</(?:div|section|aside)>',
    re.IGNORECASE | re.DOTALL
)

WP_SLIDER_NAV_PATTERN = re.compile(
    r'<div[^>]*(?:slider|carousel|gallery)[^>]*>.*?</div>',
    re.IGNORECASE | re.DOTALL
)

CONSECUTIVE_LINK_LIST_PATTERN = re.compile(
    r'(?:^(?:[-*+] )?(?:\[.*?\]\(.*?\)[ \t]*(?:\n|$)){3,})',
    re.MULTILINE
)

LOGO_IMAGE_LINE_PATTERN = re.compile(
    r'<img[^>]*(?:logo|brand|site-icon)[^>]*>',
    re.IGNORECASE
)

MARKDOWN_HORIZONTAL_RULE_PATTERN = re.compile(
    r'^[ \t]*(?:-{3,}|\*{3,}|_{3,})[ \t]*$',
    re.MULTILINE
)

SUTTON_QUAKER_DOTTED_FOOTER_PATTERN = re.compile(
    r'\.{5,}.*?Sutton Coldfield Quakers.*?$',
    re.MULTILINE | re.IGNORECASE
)

WEEBLY_FOOTER_PATTERN = re.compile(
    r'(?:Powered by|Create your (?:own|free)).*?(?:Weebly|Site Builder|IONOS|Wix|Website Builder|WordPress).*?(?:\.|$)',
    re.IGNORECASE
)

WP_ADDRESS_CONNECT_FOOTER_PATTERN = re.compile(
    r'^(?:Address|Location|Connect With Us|Contact Us|Follow Us)(?::|)\s*\n(?:[^\n]+\n){1,5}(?=\n|$)',
    re.MULTILINE | re.IGNORECASE
)

TRAILING_NAV_LINKS_PATTERN = re.compile(
    r'(?:\[(?:Home|About|Contact|Services|Products)(?:\s+(?:Page|Us|Me))?\]\(.*?\)(?:\s+\|\s+|\s*\n\s*)){2,}(?:\[(?:Home|About|Contact|Services|Products)(?:\s+(?:Page|Us|Me))?\]\(.*?\))',
    re.IGNORECASE
)

WEBSITE_HEADER_PATTERN = re.compile(
    r'^<header.*?>.*?</header>|<div[^>]*(?:site-header|page-header|main-header)[^>]*>.*?</div>',
    re.IGNORECASE | re.DOTALL | re.MULTILINE
)

WEBSITE_FOOTER_PATTERN = re.compile(
    r'<footer.*?>.*?</footer>|<div[^>]*(?:site-footer|page-footer|main-footer)[^>]*>.*?</div>',
    re.IGNORECASE | re.DOTALL
)

ZERO_WIDTH_SPACE_PATTERN = re.compile(
    r'\u200B|\u200C|\u200D|\uFEFF'
)

# optimization_rules.py
# ... (other rules remain the same) ...

# *** REFINED PATTERN ***
# New: Simple Text Navigation Menu Pattern
# Matches 4 or more consecutive lines, each 1-60 chars long, likely starting capitalized, not ending with sentence punctuation.
SIMPLE_TEXT_NAV_MENU_PATTERN = re.compile(
    r"^(?:(?=.{1,60}$)\s*[A-Z][\w &'-]+(?:\s+[A-Z][\w &'-]+){0,4}(?<![.?!])\s*\n){4,}", # Increased lines to 4, added length limit, negative lookbehind for punctuation
    re.MULTILINE
)

# *** REFINED PATTERN ***
# Updated Form Content Pattern - Made underline optional, less greedy field matching
FORM_CONTENT_PATTERN = re.compile(
    r"(?:^|\n{2,})" # Start of block after blank lines
    # Form Header/Title (Keep this part)
    r"((?:Subscribe|Contact|Sign up|Join|Register|Booking|Enquiry|Get in Touch|Send Message|Newsletter|Email Updates)[\s\w]*?)\n"
    r"(?:[-=]{3,}\s*\n+)?" # Optional Underline

    # Form Body - Match typical form elements non-greedily until a likely end-of-form indicator
    r"(?P<form_body>" # Capture form body for potential later inspection if needed
        r"(?:" # Start of elements group
            # Required field indicator (match non-greedily to newline)
            r"(?:\*\s*indicates required[^\n]*\n+)"
            # Common Form Fields (Match label, then non-greedily consume lines until next known field/marker)
            # Using non-greedy .*? but anchored by lookahead for next field or end marker
            r"|(?:(?:First Name|Last Name|Name|Email|Phone|Address|Message|Comments|Company|Organisation|Subject|Enquiry)[\s\w]*(?:\*|)\s*[:\n].*?\n+(?=(?:(?:First Name|Last Name|Name|Email|Phone|Address|Message|Comments|Company|Organisation|Subject|Enquiry)[\s\w]*(?:\*|)\s*[:\n]|Submit|Send|Register|Subscribe|Book Now|POWERED BY|Sutton Coldfield Quakers\.{3,}|\Z)))"
            # Bot-prevention comment
            r"|(?:/\*.*?real people should not fill this in.*?\*/\s*\n*)"
            # GDPR/Privacy message (non-greedy)
            r"|(?:Your (?:data|privacy|information) is important.*?\n+)"
            r"|(?:.*?unsubscribe.*?(?:bottom of|link in).*?(?:message|email).*?\n+)"
            # Buttons / Submit actions (match line non-greedily)
            r"|(?:(?:Submit|Send|Register|Subscribe|Book Now)[^\n]*\n+)"
            # Catch-all for other potential lines within the form (very non-greedy)
            # r"|(?:\s*.*?\n+)" # Use with caution - may match too much if lookahead fails
        r")+" # Match one or more form elements
    r")", # End of form_body capture group
    re.DOTALL | re.MULTILINE | re.IGNORECASE
)

# Duplicate heading pattern - matches identical consecutive markdown headings
DUPLICATE_HEADING_PATTERN = re.compile(
    r'^(#+\s+.+?)\n+\1(?:\n+\1)*',  # Matches identical headings (including whitespace and #s) repeated consecutively
    re.MULTILINE
)

# Enhanced Form Content Pattern - More comprehensive pattern to match form elements
ENHANCED_FORM_CONTENT_PATTERN = re.compile(
    r"(?:^|\n{2,})" # Start of block after blank lines
    # Form Header/Title (Keep this part)
    r"((?:Subscribe|Contact|Sign up|Join|Register|Booking|Enquiry|Get in Touch|Send Message|Newsletter|Email Updates|Updates on)[\s\w]*?)\n"
    r"(?:[-=]{3,}\s*\n+)?" # Optional Underline

    # Form Body - More comprehensive pattern to match form elements
    r"(?P<form_body>" # Capture form body
        r"(?:" # Start of elements group
            # Required field indicator
            r"(?:\*\s*indicates required[^\n]*\n+)"
            # Form fields with labels (First Name, Last Name, Email, etc.)
            r"|(?:\s*(?:First|Last)?\s*Name\s*(?:\*|\(required\))?\s*\n+)"
            r"|(?:\s*Email\s*(?:Address)?\s*(?:\*|\(required\))?\s*\n+)"
            r"|(?:\s*Phone\s*(?:Number)?\s*(?:\*|\(required\))?\s*\n+)"
            r"|(?:\s*Message\s*(?:\*|\(required\))?\s*\n+)"
            r"|(?:\s*Comments?\s*(?:\*|\(required\))?\s*\n+)"
            # Bot prevention comment
            r"|(?:/\*.*?real people should not fill this in.*?\*/\s*\n*)"
            # GDPR messages and privacy notices
            r"|(?:\s*Your\s+(?:data|privacy|information).*?important.*?\n+)"
            r"|(?:\s*We\s+(?:do\s+not\s+share|use|collect).*?information.*?\n+)"
            r"|(?:\s*You\s+can\s+unsubscribe.*?(?:anytime|at\s+any\s+time).*?\n+)"
            # Submit buttons and form endings
            r"|(?:\s*(?:Submit|Send|Register|Subscribe|Sign\s+Up).*?\n+)"
        r")+" # Match one or more form elements
    r")" # End of form body capture group
    r"(?:\s*Archives)?", # Optional "Archives" text often found after forms
    re.DOTALL | re.MULTILINE | re.IGNORECASE
)

# --- Notion Export Specific Patterns ---

# Notion ID pattern (32 hex characters, typically preceded by space or underscore)
NOTION_ID_PATTERN = re.compile(r'([^/\\]+?)[ _]([a-f0-9]{32})(?:\.[^/\\]*)?$')

# Notion export dividers (3+ dashes with optional spaces)
NOTION_DIVIDERS_PATTERN = re.compile(r'^---+\s*$', re.MULTILINE)

# Notion export properties block
NOTION_PROPERTIES_PATTERN = re.compile(r'^(?:Property|Properties):\s*\n(?:(?:[^\n]+: [^\n]+\n)+)', re.MULTILINE)

# Notion created/edited timestamps
NOTION_TIMESTAMPS_PATTERN = re.compile(r'^(?:Created|Last Edited)(?:[ :]+).*?\d{4}\s*$', re.MULTILINE)

# Notion URL references
NOTION_URL_PATTERN = re.compile(r'https://www\.notion\.so/[a-f0-9]{32}')

# Notion inline comments (double square brackets with text)
NOTION_COMMENTS_PATTERN = re.compile(r'\[\[([^\]]+)\]\]')

# Notion export citation markers
NOTION_CITATIONS_PATTERN = re.compile(r'\[(\d+)\]\(#cite-[a-f0-9-]+\)')

# ... (rest of the file including OPTIMIZATION_RULES_ORDERED remains the same) ...

# Make sure the refined patterns are used in OPTIMIZATION_RULES_ORDERED
OPTIMIZATION_RULES_ORDERED = [
    # 1. Highly Specific Metadata / Tracking / Prompts / Artifacts (Usually safe)
    ("Scraper Warning", SCRAPER_WARNING_PATTERN),
    ("Published Time", PUBLISHED_TIME_PATTERN),
    ("WP Tracking Pixel", WP_TRACKING_PIXEL_PATTERN),
    ("Meta Title/URL", META_TITLE_URL_PATTERN),
    ("WP Comment Prompt", WP_COMMENT_PROMPT_PATTERN),
    ("WP Cookie Notice", WP_COOKIE_NOTICE_PATTERN),
    ("Form Content", FORM_CONTENT_PATTERN),               # *** Using REFINED pattern ***
    ("GitHub Link", GITHUB_LINK_PATTERN),
    ("Redundant Headers", REDUNDANT_HEADERS_PATTERN),

    # 2. Specific Structural Elements / Platform Boilerplate (Known sources/formats)
    ("Weebly Header Table", WEEBLY_HEADER_TABLE_PATTERN),
    ("Modal Docs Header", MODAL_DOCS_HEADER_PATTERN),
    ("WP Nav List", WP_NAV_LIST_PATTERN),
    ("WP Sidebar Sections", WP_SIDEBAR_SECTIONS_PATTERN),
    ("WP Slider Nav", WP_SLIDER_NAV_PATTERN),
    ("Consecutive Markdown Link List", CONSECUTIVE_LINK_LIST_PATTERN),

    # 3. Common Assets / Less Specific Structural (Logos, Separators, Footers)
    ("Logo Image Line", LOGO_IMAGE_LINE_PATTERN),
    ("Markdown Horizontal Rule", MARKDOWN_HORIZONTAL_RULE_PATTERN),
    ("Sutton Quaker Dotted Footer", SUTTON_QUAKER_DOTTED_FOOTER_PATTERN),
    ("Weebly Footer", WEEBLY_FOOTER_PATTERN),
    ("WP Address/Connect Footer", WP_ADDRESS_CONNECT_FOOTER_PATTERN),

    # 4. General Website Chrome / Navigation (Broader patterns, apply later)
    ("Trailing Nav Links", TRAILING_NAV_LINKS_PATTERN),
    ("Simple Text Nav Menu", SIMPLE_TEXT_NAV_MENU_PATTERN), # *** Using REFINED pattern ***
    ("General Website Header", WEBSITE_HEADER_PATTERN),
    ("General Website Footer", WEBSITE_FOOTER_PATTERN),

    # 5. Final Formatting Cleanup (Applied last in this list or separately)
    ("Zero Width Space", ZERO_WIDTH_SPACE_PATTERN),

    # 6. New Patterns
    ("Duplicate Headings", DUPLICATE_HEADING_PATTERN),
    ("Enhanced Form Content", ENHANCED_FORM_CONTENT_PATTERN),
]

# Add the Notion rules to the ordered list, but only apply when in notion mode
NOTION_SPECIFIC_RULES = [
    ("Notion Dividers", NOTION_DIVIDERS_PATTERN),
    ("Notion Properties", NOTION_PROPERTIES_PATTERN),
    ("Notion Timestamps", NOTION_TIMESTAMPS_PATTERN),
    ("Notion URLs", NOTION_URL_PATTERN),
    ("Notion Comments", NOTION_COMMENTS_PATTERN),
    ("Notion Citations", NOTION_CITATIONS_PATTERN),
]