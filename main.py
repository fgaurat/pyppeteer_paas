#!/usr/bin/env python
from pprint import pprint
import random
import sys
import os
import asyncio
import time
from pyppeteer import launch
import uuid
import urllib
import utils
import argparse

async def main(kw):
    random.shuffle(utils.proxy_url)
    random.shuffle(utils.fetch_url)

    kw  = urllib.parse.quote_plus(kw)
    num=10 # pour récupérer des paas => 10 résultats
    hl='fr'
    gl='fr'
    pws = '0'
    iqu='1'
    ip='0.0.0.0'
    safe='images'
    gwsRd='ssl'
    source='hp'

    # url = f'https://www.google.com/search?q={kw}&oq={kw}&num=100'
    url = f'https://www.google.fr/search?q={kw}&oq={kw}&num={num}&hl={hl}&gl={gl}&pws={pws}&iqu={iqu}&ip={ip}&safe={safe}&gws_rd={gwsRd}&source={source}'
    
    try:
        browser = await launch()
        # browser = await launch({'args': ['--proxy-server=196.242.10.181:7777:seoser:aun!btn.gvh7DBG7pur'], 'headless': False })
        # browser = await launch({"headless": False, "args": ["--start-maximized"]})
        # browser = await launch({"headless": False})
        # context = await browser.createIncognitoBrowserContext()


        page = await browser.newPage()
        await page.setViewport(viewport={"width": 1920, "height": 1080})
        await page.goto(url)
        await page.screenshot({'path': f'start.png'})

        await page.waitForXPath("//button/div[contains(., 'Tout accepter')]")
        elements = await page.xpath("//button/div[contains(., 'Tout accepter')]")
        await page.screenshot({'path': f'{kw}1.png', 'fullPage': True})




        # Accepter les cookies
        for element in elements:
            await element.click()


        associated_search = await page.evaluate('''

            () => {
                const associated_search = []
                
                document.querySelectorAll('#bres a').forEach((e)=>{
                    associated_search.push(e.textContent)
                })

                return {
                    associated_search
                }
            }        
        ''')

        pprint(associated_search)


        await page.waitForXPath("//div[@data-it='rq']/div")
        await page.screenshot({'path': f'{kw}2.png', 'fullPage': True})

        await page.evaluate('''() => {
                    document.querySelectorAll('div[data-q]').forEach((e)=>{
                        e.querySelectorAll('div[data-ved]').forEach((eved)=>{
                            eved.click()
                        });
                    });

        }''')
        await asyncio.sleep(4)

        await page.evaluate('''() => {
                    document.querySelectorAll('div[data-q]').forEach((e)=>{
                        e.querySelectorAll('div[data-ved]').forEach((eved)=>{
                            eved.click()
                        });
                    });

        }''')
        await asyncio.sleep(4)

        await page.evaluate('''() => {
                    document.querySelectorAll('div[data-q]').forEach((e)=>{
                        e.querySelectorAll('div[data-ved]').forEach((eved)=>{
                            eved.click()
                        });
                    });

        }''')
        await asyncio.sleep(4)
        await page.screenshot({'path': f'{kw}3.png', 'fullPage': True})
        info = await page.evaluate('''

            () => {
                const paas = []
                const titles = []
                const descriptions = []
                const associated_search = []
                
                document.querySelectorAll('div[data-q]').forEach((e)=>{
                    paas.push(e.dataset.q)
                })
                
                document.querySelectorAll('div.g h3').forEach((e)=>{
                    titles.push(e.textContent)
                })
                document.querySelectorAll('div#rso div.g span').forEach((e)=>{
                    descriptions.push(e.textContent)
                })
                document.querySelectorAll('#bres a').forEach((e)=>{
                    associated_search.push(e.textContent)
                })

                return {
                    paas,
                    titles,
                    descriptions,
                    associated_search
                }
            }        
        ''')

        pprint(info['associated_search'])

        # elements = await page.xpath("//div[@data-it='rq']/div")


        # for element in elements:
        #     if await element.boundingBox(): # si visible
        #         questions = await element.querySelectorAll("div")
        #         for question in questions:
        #             print(await question.jsonValue())
        #             # await question.click()
        #             # time.sleep(1)
        #     await element.screenshot({'path': f'q.png'})
                    
                
            
        
        await page.screenshot({'path': f'{kw}4.png', 'fullPage': True})

    finally:
        await browser.close()

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('kw', help='keyword', default=None)
    args = args.parse_args()
    asyncio.run(main(args.kw))

