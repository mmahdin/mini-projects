import asyncio
from bs4 import BeautifulSoup
from weasyprint import HTML
from playwright.async_api import async_playwright


async def fetch_rendered_section(url: str):
    """Fetch the rendered target section HTML and associated styles from a dynamic page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(3000)

        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        target_div = soup.find(
            'div', {'data-controller': 'mushaf-page tajweed-highlight'})
        if not target_div:
            raise Exception("Target div not found")
        html_content = str(target_div)

        styles = await page.evaluate("""() => {
            let css = '';
            for (const sheet of document.styleSheets) {
                try {
                    for (const rule of sheet.cssRules) {
                        css += rule.cssText + '\\n';
                    }
                } catch (e) {
                    // skip inaccessible rules
                }
            }
            return css;
        }""")

        await browser.close()
        return html_content, styles


def generate_pdf_from_html(html_content: str, styles: str, base_url: str, output_file: str):
    custom_style = """
    .surah-name {
        margin-left: -20px !important;
    }
    .surah-name-v4-icon {
        margin-left: -20px !important;
    }
    """
    full_styles = styles + custom_style
    """Generate a PDF from HTML and CSS."""
    combined_html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <style>{styles}</style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    """
    HTML(string=combined_html, base_url=base_url).write_pdf(output_file)
    print(f"✅ {output_file} created with dynamic content rendered.")


# Main execution
async def main():
    url = 'https://qul.tarteel.ai/resources/musbat-layout/14?page=595'
    html_content, styles = await fetch_rendered_section(url)
    generate_pdf_from_html(html_content, styles, base_url=url,
                           output_file="output_rendered.pdf")


asyncio.run(main())
