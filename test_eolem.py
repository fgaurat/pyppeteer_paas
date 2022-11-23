#!/usr/bin/env python
from pprint import pprint
import sys
import os
import asyncio
import time
from pyppeteer import launch
import uuid
import urllib

async def main():
    url = "https://eolem.com"
    
    try:
        # browser = await launch()
        browser = await launch({"ignoreHTTPSErrors": True})
        page = await browser.newPage()

        await page.setViewport(viewport={"width": 1920, "height": 1080})
        await page.goto(url)
        await page.screenshot({'path': f'start.png'})



        dimensions = await page.evaluate('''() => {
            for (let i = 0; i < 5; i++) {
                setTimeout(function() {
                    document.querySelectorAll('div[data-q]').forEach((e)=>{
                        e.querySelectorAll('div[data-ved]').forEach((eved)=>{
                            eved.click()
                        });
                    });

                },4000)
            }

        }''')


    finally:
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())

