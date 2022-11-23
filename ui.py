#!/usr/bin/env python
import sys
import os
import urllib
import streamlit as st
from pyppeteer import launch
import asyncio
from pprint import pprint
import itertools
import httpx
import random

async def query_google_suggest(query):
    url = f'https://www.google.com/complete/search?client=firefox&q={query}'
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        await asyncio.sleep(random.randint(1, 2))
        return r.json()

async def load_paas(kw,my_bar):

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
        # browser = await launch()
        browser = await launch(
            handleSIGINT=False,
            handleSIGTERM=False,
            handleSIGHUP=False
        )        
        my_bar.progress(10)
        # browser = await launch({'args': ['--proxy-server=196.242.10.181:7777:seoser:aun!btn.gvh7DBG7pur'], 'headless': False })
        # browser = await launch({"headless": False, "args": ["--start-maximized"]})
        # browser = await launch({"headless": False})
        # context = await browser.createIncognitoBrowserContext()


        page = await browser.newPage()
        my_bar.progress(20)
        await page.setViewport(viewport={"width": 1920, "height": 1080})
        await page.goto(url)
        my_bar.progress(40)

        await page.waitForXPath("//button/div[contains(., 'Tout accepter')]")
        elements = await page.xpath("//button/div[contains(., 'Tout accepter')]")


        # Accepter les cookies
        for element in elements:
            await element.click()
        my_bar.progress(50)

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
        my_bar.progress(60)
        await page.waitForXPath("//div[@data-it='rq']/div")

        await page.evaluate('''() => {
                    document.querySelectorAll('div[data-q]').forEach((e)=>{
                        e.querySelectorAll('div[data-ved]').forEach((eved)=>{
                            eved.click()
                        });
                    });

        }''')
        await asyncio.sleep(4)
        my_bar.progress(70)
        await page.evaluate('''() => {
                    document.querySelectorAll('div[data-q]').forEach((e)=>{
                        e.querySelectorAll('div[data-ved]').forEach((eved)=>{
                            eved.click()
                        });
                    });

        }''')
        await asyncio.sleep(4)
        my_bar.progress(80)
        await page.evaluate('''() => {
                    document.querySelectorAll('div[data-q]').forEach((e)=>{
                        e.querySelectorAll('div[data-ved]').forEach((eved)=>{
                            eved.click()
                        });
                    });

        }''')
        await asyncio.sleep(4)
        my_bar.progress(90)
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

            
        

    finally:
        await browser.close()
        my_bar.progress(100)
    
    return info

async def google_scrap():
    st.header("Get Google people also ask")
    # input query
    query = st.text_input("Enter your query")
    if query:
        # load data state 
        my_bar = st.progress(0)

        info = await load_paas(query,my_bar)
        paas = info['paas']
        titles = info['titles']
        associated_search = info['associated_search']
        col1, col2, col3 = st.columns(3)

        with col1:
            st.header("Titles")
            st.table(titles)

        with col2:
            st.header("People also ask")
            st.table(paas)

        with col3:
            st.header("Associated search")
            st.table(associated_search)

async def google_suggest():
    st.header("Get Google suggest")
    
    # input query
    query = st.text_input("Enter your query",key="suggest")
    alphabet="abcdefghijklmnopqrstuvwxyz"
    questions = [
        "Comment _ ",
        "Comment puis-je _ ",
        "Pourquoi _ ",
        "Ou _ ",
        "Quel _ ",
        "Quelle _ ",
        "Qui _ ",
        "Par quel moyen _ ",
        "A quel endroit _ ",
        "Est il possible de _ ",
        ]
    queries = []
    queries.append({"query":f"{query}","question":""})
    queries.append({"query":f"{query} _","question":""})
    for letter in alphabet:
        queries.append({"query":f"{query} {letter}_","question":""})
    for i,question in enumerate(questions):
        if len(queries) > i:
            queries[i]["question"] = f"{question} {query}"

    if query:
        my_bar = st.progress(0)
        txt_status = st.text("Loading...")

        col1, col2 = st.columns(2)

        with col1:
            st.header("Google suggest")
            tbl_suggest = st.table([])
      
        

        with col2:
            st.header("Google Questions")
            tbl_questions = st.table([])
           

        for i,query in enumerate(queries):
            p = ((100//len(queries))+1)*i+1
            if p>100:
                p=100
            my_bar.progress(p)
            if query["query"]:
                result_query = await query_google_suggest(query["query"])
                tbl_suggest.add_rows(result_query[1])
            if query["question"]:
                result_question = await query_google_suggest(query["question"])
                tbl_questions.add_rows(result_question[1])

        
        txt_status.text("Loading... done")                




async def combine_keywords():
    st.header("Keywords")

    col1, col2, col3 = st.columns(3)
    with col1:
        kws_1 = st.text_area('Keywords 1',height=200,value="")
    with col2:
        kws_2 = st.text_area('Keywords 2',height=200,value="")
    with col3:
        kws_3 = st.text_area('Keywords 3',height=200,value="")
    
    btn_combine = st.button("Combine keywords")
    if btn_combine:
        content = [kws_1.strip().splitlines(),kws_2.strip().splitlines(),kws_3.strip().splitlines()]
        result = list(itertools.product(*content))
        st.text_area('Result',height=1000,value='\n'.join([' '.join(x) for x in result]))

async def main():
    st.set_page_config(layout="wide")
    st.title("Tools for SEO")
    tab1, tab2, tab3 = st.tabs(["Suggests","Google Scrap", "Keywords"])

    with tab1:
        await google_suggest()

    with tab2:
        await google_scrap()

    with tab3:
        await combine_keywords()


if __name__ == '__main__':
    asyncio.run(main())