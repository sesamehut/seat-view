// Optional visual smoke test. Install Playwright separately; not a runtime dependency.
// node tests/browser_check.mjs /absolute/path/to/preview/index.html ./docs/images
import {createRequire} from 'node:module';
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const [input,output]=process.argv.slice(2);
if(!input||!output)throw new Error('Usage: node tests/browser_check.mjs INDEX_HTML SCREENSHOT_DIRECTORY');
await fs.mkdir(output,{recursive:true});
const browser=await chromium.launch({channel:process.env.CHROME_CHANNEL||'chrome'});
const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});
const page=await context.newPage();const errors=[],requests=[];
page.on('pageerror',e=>errors.push(e.message));
await context.route(/^https?:/,route=>{requests.push(route.request().url());return route.abort();});
try{
  await page.goto(pathToFileURL(path.resolve(input)).href);
  await page.waitForFunction(()=>window.__seatView?.ready);
  assert.equal(await page.locator('.view').count(),3);
  await page.screenshot({path:path.join(output,'overview.png')});
  for(let i=0;i<3;i++){
    await page.locator('.view').nth(i).click();
    assert.equal(await page.locator('.view.active').count(),1);
    assert.match(await page.locator('#seat').getAttribute('class'),/active/);
    assert.ok(Number(await page.locator('#distance').textContent())>0);
    await page.screenshot({path:path.join(output,`view-${i+1}.png`)});
  }
  await page.locator('#sources-button').click();assert.ok(await page.locator('dialog').isVisible());
  await page.locator('#close-sources').click();
  const downloadPromise=page.waitForEvent('download');await page.locator('#save').click();
  const download=await downloadPromise;await download.saveAs(path.join(output,'export.png'));
  await page.setViewportSize({width:390,height:844});
  await page.locator('#overview').click();
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:path.join(output,'mobile.png'),fullPage:true});
  await page.locator('.view').nth(1).click();
  await page.screenshot({path:path.join(output,'mobile-seat.png'),fullPage:true});
  assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
  console.log(JSON.stringify({status:'PASS',views:3,desktop:[1440,1000],mobile:[390,844],httpRequests:requests.length,errors,export:download.suggestedFilename()}));
}finally{await browser.close();}
