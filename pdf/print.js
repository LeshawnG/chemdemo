const { chromium } = require('playwright');
(async () => {
  const [,, inp, out, pngdir] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 720, height: 1024 }, deviceScaleFactor: 1 });
  await p.goto('file://' + inp, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  // overflow check: content bottom vs footer top per page
  const report = await p.evaluate(() => [...document.querySelectorAll('section.page')].map((sec, i) => {
    const foot = sec.querySelector('footer');
    const limit = foot ? foot.getBoundingClientRect().top : sec.getBoundingClientRect().bottom;
    let maxB = 0;
    for (const el of sec.children) { if (el.tagName === 'FOOTER') continue; const r = el.getBoundingClientRect(); maxB = Math.max(maxB, r.bottom); }
    return { page: i + 1, spare: Math.round(limit - maxB) };
  }));
  console.log(JSON.stringify(report));
  await p.pdf({ path: out, width: '7.5in', height: '10.6667in', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
