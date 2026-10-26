import {chromium} from '@playwright/test';
import {spawn} from 'node:child_process';
import assert from 'node:assert/strict';
const server=spawn(process.env.PYTHON||'python3',['-m','uvicorn','floodlens.api:app','--host','127.0.0.1','--port','8103'],{cwd:'..',stdio:'ignore'});
for(let i=0;i<60;i++){try{if((await fetch('http://127.0.0.1:8103/api/health')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
let browser;
try {
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||undefined,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:1250},deviceScaleFactor:1});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8103/');await page.getByText('Ready • synthetic scenario').waitFor();
 await page.getByRole('heading',{name:'A landscape under observation'}).waitFor();
 await page.getByRole('button',{name:'▶ Play'}).click();await page.getByRole('button',{name:'Ⅱ Pause'}).click();
 await page.getByLabel('Crossing',{exact:true}).selectOption('4');await page.getByLabel('Rotate 3D terrain').fill('1.2');
 await page.getByLabel('Simulation time').fill('0');await page.getByText('Observation unavailable').first().waitFor();
 await page.getByLabel('Simulation time').fill('35');
 await page.getByLabel('Gauge policy').selectOption('grid');await page.getByRole('button',{name:'Run scenario ↗'}).click();await page.getByText('Ready • synthetic scenario').waitFor();
 await page.getByRole('heading',{name:'The crossing, in time'}).waitFor();
 const plotBefore=await page.locator('.plot-record svg').getAttribute('viewBox');assert.equal(plotBefore,'0 0 430 195');
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true,'Desktop layout must not overflow horizontally');
 assert.equal(await page.evaluate(()=>getComputedStyle(document.documentElement).backgroundColor),'rgb(231, 215, 195)');
 assert.equal(await page.locator('canvas').evaluate(el=>getComputedStyle(el).transform),'none');
 await page.evaluate(()=>document.fonts.ready);await page.screenshot({path:'../docs/images/app.png',fullPage:true,animations:'disabled'});
 await page.setViewportSize({width:390,height:900});await page.getByRole('link',{name:'Open survey setup ↓'}).click();
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true,'Mobile layout must not overflow horizontally');
 await page.getByLabel('Inspection route').selectOption('nearest');await page.getByRole('button',{name:'Run scenario ↗'}).click();await page.getByText('Ready • synthetic scenario').waitFor();
 await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'../docs/images/mobile.png',fullPage:true,animations:'disabled'});
 const reduced=await browser.newPage({viewport:{width:1440,height:1250},reducedMotion:'reduce'});
 await reduced.goto('http://127.0.0.1:8103/');await reduced.getByText('Ready • synthetic scenario').waitFor();
 const motion=await reduced.evaluate(()=>({tab:getComputedStyle(document.querySelector('.sheet-tab')).animationName,underlay:getComputedStyle(document.querySelector('.sheet'),'::before').animationName,canvas:getComputedStyle(document.querySelector('canvas')).transform}));
 assert.deepEqual(motion,{tab:'none',underlay:'none',canvas:'none'});
 await reduced.getByLabel('Crossing',{exact:true}).selectOption('1');await reduced.getByLabel('Simulation time').fill('0');await reduced.getByText('Observation unavailable').first().waitFor();
 await reduced.screenshot({path:'../docs/images/reduced-motion.png',fullPage:true,animations:'disabled'});
 assert.deepEqual(errors,[]);console.log('PASS: desktop/mobile atlas, play/pause, rotation, crossing selection, arrival gating, policy rerun, no mobile overflow and reduced-motion.');
} finally {if(browser)await browser.close();server.kill();}
