import os
from playwright.async_api import async_playwright
import jinja2

# Get template directory
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# Create default template if it doesn't exist
TEMPLATE_CONTENT = """<!DOCTYPE html>
<html data-theme="{{ theme }}">
<head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/css/bootstrap.min.css" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.3.0/github-markdown.min.css" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" crossorigin="anonymous">
    <style>
        {{ custom_styles }}
    </style>

    <style>
        /* PDF specific overrides */
        body {
            background-color: {{ bg_color }};
            color: {{ text_color }};
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        .markdown-body {
            padding: 20mm;
            background-color: transparent !important;
            box-sizing: border-box;
            min-height: 100vh;
            font-size: 13px !important;
        }
        /* Page break configurations */
        h1, h2, h3, h4, h5, h6 {
            page-break-after: avoid;
            break-after: avoid;
        }
        pre, blockquote, table, img, svg {
            page-break-inside: avoid;
            break-inside: avoid;
        }
        @media print {
            body {
                background-color: {{ bg_color }} !important;
                color: {{ text_color }} !important;
            }
            .markdown-body {
                padding: 0;
            }
        }
    </style>
</head>
<body>
    <div class="markdown-body">
        {{ html_content }}
    </div>
</body>
</html>
"""

template_path = os.path.join(TEMPLATE_DIR, "pdf_template.html")
with open(template_path, "w", encoding="utf-8") as f:
    f.write(TEMPLATE_CONTENT)


async def generate_pdf_with_progress(html_content: str, theme: str, pdf_path: str, custom_styles: str = "", title: str = "Markdown Export"):
    """
    Generate PDF from HTML content using Playwright Chromium.
    Yields progress dicts during the process.
    """
    # Map theme colors for body background/text
    bg_color = "#0d1117" if theme == "dark" else "#ffffff"
    text_color = "#c9d1d9" if theme == "dark" else "#24292e"

    yield {"progress": 15, "stage": "Preparing template", "detail": "Compiling HTML with styles..."}

    # Render template using Jinja2
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("pdf_template.html")
    
    rendered_html = template.render(
        html_content=html_content,
        theme=theme,
        bg_color=bg_color,
        text_color=text_color,
        custom_styles=custom_styles,
        title=title
    )

    yield {"progress": 30, "stage": "Launching browser", "detail": "Starting headless Chromium instance..."}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            yield {"progress": 45, "stage": "Creating page", "detail": "Creating browser context..."}
            
            context = await browser.new_context(
                viewport={"width": 1000, "height": 800},
                device_scale_factor=2
            )
            page = await context.new_page()

            yield {"progress": 60, "stage": "Loading content", "detail": "Setting page content..."}
            
            # Set content and wait for it to be loaded
            await page.set_content(rendered_html, wait_until="load")
            
            yield {"progress": 75, "stage": "Rendering assets", "detail": "Waiting for fonts and images..."}
            
            # Wait for network idle to ensure any external assets (like images) are fully loaded
            try:
                await page.wait_for_load_state("networkidle", timeout=3000)
            except Exception:
                # Proceed even if networkidle times out
                pass

            # Give a small buffer for layout stabilization
            await page.evaluate("() => new Promise(resolve => setTimeout(resolve, 500))")

            yield {"progress": 85, "stage": "Generating PDF", "detail": "Printing page to PDF file..."}

            # Generate PDF with A4 margins and proper layout
            await page.pdf(
                path=pdf_path,
                format="A4",
                print_background=True,
                margin={
                    "top": "20mm",
                    "bottom": "20mm",
                    "left": "15mm",
                    "right": "15mm"
                },
                display_header_footer=True,
                header_template='<div style="font-size: 8px; color: transparent; margin: 0; padding: 0;"></div>',
                footer_template='<div style="font-size: 10px; color: #888; width: 100%; text-align: center; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif; margin-bottom: 5mm;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
                prefer_css_page_size=False
            )

            yield {"progress": 95, "stage": "Finalizing", "detail": "Closing browser and saving..."}

        finally:
            await browser.close()
