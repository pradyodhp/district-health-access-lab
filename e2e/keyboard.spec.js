import {test, expect} from '@playwright/test'

// Tab and Enter only for primary journey, no click/focus shortcut.
async function tabTo(page, target) {
  for (let i=0; i<120; i++) {
    if (await target.evaluate(node => node === document.activeElement)) return
    await page.keyboard.press('Tab')
  }
  throw Error('Keyboard could not reach target')
}
async function activate(page, name) {
  const target=page.getByRole('button',{name,exact:true})
  await tabTo(page,target)
  await expect(target).toBeFocused()
  await page.keyboard.press('Enter')
}

test('keyboard-only primary journey with visible focus and memo',async({page})=>{
  await page.goto('/')
  await page.keyboard.press('Tab')
  await expect(page.getByRole('link',{name:'Skip to main content'})).toBeFocused()
  await page.screenshot({path:'artifacts/keyboard-skip.png'})
  await tabTo(page,page.getByRole('button',{name:'Decision workbench'})); await page.keyboard.press('Enter')
  await expect(page.getByText(/REAL DECISION: HOLD/)).toBeVisible()
  await activate(page,'Model & runs')
  await tabTo(page,page.getByRole('button',{name:'Run reproducible model'}))
  await page.screenshot({path:'artifacts/keyboard-run-focus.png'})
  expect(await page.evaluate(()=>getComputedStyle(document.activeElement).outlineStyle)).toBe('solid')
  await page.keyboard.press('Enter')
  await expect(page.getByText(/SAVED LOCAL RUN/)).toBeVisible()
  await activate(page,'Verify replay')
  await expect(page.getByRole('alert')).toContainText('reproduced')
  await activate(page,'Memo')
  await activate(page,'Generate memo from run')
  await expect(page.getByText('What we do not know')).toBeVisible()
  await page.screenshot({path:'artifacts/keyboard-memo.png',fullPage:true})
})

for (const width of [1366,768,390]) {
 test(`responsive ${width} with reduced motion and named controls`,async({page})=>{
  await page.setViewportSize({width,height:900})
  await page.emulateMedia({reducedMotion:'reduce'})
  await page.goto('/')
  await page.getByRole('button',{name:'Decision workbench'}).click()
  await expect(page.getByRole('textbox',{name:'Case name'})).not.toHaveValue('')
  for (const section of ['Case & evidence','Model & runs','Sensitivity & research','Allocation & robustness','Memo']) {
    await page.getByRole('button',{name:section,exact:true}).click()
    expect(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth)).toBe(true)
    await page.screenshot({path:`artifacts/${width}-${section.split(' ')[0]}.png`,fullPage:true})
    expect(await page.locator('button,select,input').evaluateAll(nodes=>nodes.filter(node=>
      !node.disabled && !node.textContent?.trim() && !node.getAttribute('aria-label') && !node.labels?.length
    ).length)).toBe(0)
  }
 })
}
