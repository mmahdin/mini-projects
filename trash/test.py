import asyncio
from asyncio.subprocess import PIPE
import aiohttp

async def get(url):
    print("Start: %s" % url)
    response = await aiohttp.request("GET", url)
    print("Finish: %s" % url)
    response.close()
    return 1

async def cmd(cmd):
    print("Start: %s" % cmd)
    proc = await asyncio.create_subprocess_shell(
            cmd, stdin=None, stderr=None, stdout=PIPE)
    print("Proc created: %s" % cmd)
    out = await proc.stdout.read()
    print("Finish: %s" % cmd)
    return out

async def run_all(url1, url2, shellcmd):
    r1 = await get(url1)
    r2 = await get(url2)
    s1 = await cmd(shellcmd)
    results = await asyncio.gather(r1, r2, s1)

    for res in results:
        print(res)


loop = asyncio.get_event_loop()
loop.run_until_complete(run_all("http://google.com.au", "http://google.com", "ls ~/"))
loop.close()