import {test,expect} from '@playwright/test';
// Requires a disposable bench 900001, created and removed by the test operator.
test('shared adoption persists across independent browsers and rejects double booking',async({page,browser})=>{
 await page.goto('/');
 await expect(page.getByText('Supabase connected · sample bench locations')).toBeVisible();
 await page.getByRole('button',{name:'List view',exact:true}).click();
 await page.getByRole('textbox',{name:'Search benches'}).fill('VCP-900001');
 await expect(page.locator('tbody tr')).toHaveCount(1);
 const otherContext=await browser.newContext();const other=await otherContext.newPage();
 await other.goto('/');await other.getByRole('button',{name:'List view',exact:true}).click();
 await other.getByRole('textbox',{name:'Search benches'}).fill('VCP-900001');
 for(const p of [page,other]){
  await p.getByRole('button',{name:'Adopt now',exact:true}).click();
  await p.getByLabel('Public display name').fill('Supabase integration check');
  await p.getByLabel('Email address').fill('integration@example.com');
  await p.getByRole('checkbox').check();
 }
 await page.getByRole('button',{name:'Confirm adoption',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Your place in the park.'})).toBeVisible();
 await other.getByRole('button',{name:'Confirm adoption',exact:true}).click();
 await expect(other.getByRole('alert')).toContainText('This bench has just been adopted');
 await other.reload();await other.getByRole('button',{name:'List view',exact:true}).click();
 await other.getByRole('textbox',{name:'Search benches'}).fill('VCP-900001');
 await expect(other.locator('tbody')).toContainText('Supabase integration check');
 expect(await other.evaluate(()=>localStorage.getItem('vcp-benches-v1'))).toBeNull();
 await otherContext.close();
});
