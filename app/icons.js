const { chromium } = require('playwright');
(async () => {
  const [,, svg, outdir] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 512, height: 512 } });
  await p.goto('file://' + svg); await p.screenshot({ path: outdir + '/icon-512.png' }); await b.close();
})();
