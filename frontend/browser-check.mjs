import {chromium} from '@playwright/test';
import {spawn} from 'node:child_process';
const server=spawn(process.env.PYTHON||'python',['-m','uvicorn','floodlens.api:app','--host','127.0.0.1','--port','8103'],{cwd:'..',stdio:'ignore'});
for(let i=0;i<60;i++){try{if((await fetch('http://127.0.0.1:8103/api/health')).ok)break;}catch{} await new Promise(r=>setTimeout(r,100));}
try {
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||undefined,args:['--no-sandbox']});const page=await browser.newPage({viewport:{width:1440,height:1350},deviceScaleFactor:1});const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:8103/');await page.getByText('Ready • synthetic scenario').waitFor();await page.getByRole('button',{name:'▶ Play'}).click();await page.getByRole('button',{name:'Ⅱ Pause'}).click();await page.getByLabel('Crossing',{exact:true}).selectOption('4');await page.getByLabel('Rotate 3D terrain').fill('1.2');await page.getByLabel('Simulation time').fill('0');await page.getByText('Observation unavailable').first().waitFor();await page.getByLabel('Simulation time').fill('35');await page.getByLabel('Gauge policy').selectOption('grid');await page.getByRole('button',{name:'Run scenario ↗'}).click();await page.getByText('Ready • synthetic scenario').waitFor();await page.screenshot({path:'../docs/images/app.png',fullPage:true});
await page.setViewportSize({width:390,height:900});await page.screenshot({path:'../docs/images/mobile.png',fullPage:true});if(errors.length)throw new Error(errors.join('\n'));await browser.close();console.log('Live browser scenario, play/pause, rotate, time gating, crossing selection, policy rerun and screenshot checks passed');

} finally { server.kill(); }
