import asyncio, subprocess, time, sys
from playwright.async_api import async_playwright
BG = "background:radial-gradient(ellipse at 30% 35%, #5a4a3a 0%, #2a2620 45%, #0d0c0a 100%);"
pages = {
 "stream_overlay": f"""<body style='margin:0;{BG}'><div style='position:absolute;left:120px;top:110px;color:#ffffffaa;font:600 46px Poppins'>[ Fallbrook video playing on the 24/7 stream ]</div>
   <iframe src='/fallbrook/index.html?layout=lowerthird&src=stream' style='position:absolute;inset:0;width:1920px;height:1080px;border:0;background:transparent' allowtransparency></iframe></body>""",
 "store_screen": f"""<body style='margin:0;background:#000'><div style='position:absolute;left:0;top:0;width:1920px;height:810px;{BG}'><div style='position:absolute;left:120px;top:110px;color:#ffffffaa;font:600 46px Poppins'>[ Video zone: Fallbrook playlist ]</div></div>
   <iframe src='/fallbrook/index.html?layout=strip&src=store' style='position:absolute;left:0;top:810px;width:1920px;height:270px;border:0'></iframe></body>""",
 "full_card": """<body style='margin:0'><iframe src='/fallbrook/index.html?layout=card&src=store' style='position:absolute;inset:0;width:1920px;height:1080px;border:0'></iframe></body>""",
}
for k,v in pages.items(): open(f"site/_{k}.html","w").write(v)
async def main():
    srv = subprocess.Popen([sys.executable,"-m","http.server","8765","-d","site"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    time.sleep(1)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = await b.new_page(viewport={"width":1920,"height":1080})
        for k in pages:
            for shot in (0,1):
                await pg.goto(f"http://localhost:8765/_{k}.html"); await pg.wait_for_timeout(1800)
                if shot: 
                    # advance to the 3rd ad (a later day) by evaluating inside the iframe
                    f = pg.frames[1]; await f.evaluate("()=>{const a=[...document.querySelectorAll('.ad')];a.forEach(e=>e.classList.remove('on'));a[4].classList.add('on')}"); await pg.wait_for_timeout(900)
                await pg.screenshot(path=f"preview/{k}_{shot+1}.png")
        await b.close()
    srv.terminate()
asyncio.run(main())
