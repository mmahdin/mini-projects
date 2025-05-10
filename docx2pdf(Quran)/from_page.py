import asyncio
from playwright.async_api import async_playwright
from PIL import Image
from fpdf import FPDF


async def main():
    url = 'https://qul.tarteel.ai/resources/musbat-layout/14?page=595'

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(3000)

        # Find the target element
        element = await page.query_selector('div[data-controller="mushaf-page tajweed-highlight"]')
        if not element:
            raise Exception("Target div not found")

        # Take a screenshot of the element
        await element.screenshot(path="section.png")
        print("✅ Screenshot saved as section.png")

        await browser.close()

    # Convert image to PDF
    image = Image.open("section.png")
    pdf = FPDF(unit="pt", format=[image.width, image.height])
    pdf.add_page()
    pdf.image("section.png", 0, 0)
    pdf.output("output_rendered.pdf")
    print("✅ output_rendered.pdf created from screenshot.")

asyncio.run(main())
