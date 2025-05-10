import asyncio
from bs4 import BeautifulSoup
from weasyprint import HTML, CSS
from pathlib import Path
from playwright.async_api import async_playwright


async def main():
    url = 'https://qul.tarteel.ai/resources/musbat-layout/14?page=595'

    # Step 1: Launch browser and go to page
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        # Wait for JS to load content (increase if needed)
        await page.wait_for_timeout(3000)

        # Step 2: Extract the fully rendered HTML
        html = await page.content()

        # Step 3: Extract the specific div
        soup = BeautifulSoup(html, 'html.parser')
        target_div = soup.find(
            'div', {'data-controller': 'mushaf-page tajweed-highlight'})
        if not target_div:
            raise Exception("Target div not found")
        html_content = str(target_div)

        # Step 4: Collect all computed styles
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

    # Step 5: Save PDF with styles
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

    HTML(string=combined_html, base_url=url).write_pdf("output_rendered.pdf")
    print("✅ output_rendered.pdf created with dynamic content rendered.")

asyncio.run(main())
