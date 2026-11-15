#!/usr/bin/env python3
"""Second Brain Studios visual QA agent.
Run: python3 evaluate.py
Requires: pip install playwright pillow; python -m playwright install chromium
Starts a local server, captures desktop/mobile screenshots, and checks design elements.
Compare screenshots manually to the original mockup. This is not an image-similarity model.
"""
import json, pathlib, subprocess, time
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).parent
server=subprocess.Popen(["python3","-m","http.server","8765","--directory",str(ROOT)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(1)
checks={}
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True)
  for label,width,height in [("desktop",1440,1000),("mobile",390,844)]:
   page=browser.new_page(viewport={"width":width,"height":height})
   page.goto("http://127.0.0.1:8765/",wait_until="networkidle")
   page.screenshot(path=str(ROOT/("qa-"+label+".png")),full_page=True)
   if label=="desktop":
    checks["hero_image"]=page.locator(".hero").evaluate("(el)=>getComputedStyle(el).backgroundImage.includes('hero.svg')")
    checks["serif_headline"]=page.locator("h1").evaluate("(el)=>getComputedStyle(el).fontFamily.includes('Georgia')")
    checks["benefit_blocks"]=page.locator(".benefit").count()==3
    checks["process_cards"]=page.locator(".step").count()==3
    checks["example_cards"]=page.locator(".case").count()==3
    checks["insights"]=page.locator(".insight").count()==3
    checks["cta"]=page.locator(".bottom-cta").count()==1
    for route in ["how","work","insights","press","about","faq","booking"]:
     page.goto("http://127.0.0.1:8765/#"+route)
     checks["route_"+route]=page.locator(".page-head h1").count()==1
   else:
    checks["mobile_menu"]=page.locator("#menu").is_visible()
   page.close()
  browser.close()
finally:
 server.terminate()
result={"passed":sum(checks.values()),"total":len(checks),"checks":checks,"note":"Structural checks only. Inspect qa-desktop.png and qa-mobile.png against the reference mockup."}
(ROOT/"qa-results.json").write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
