"""Real browser controls on synthetic stored QC, not an ASDF runtime test."""
import argparse
import importlib.util
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location('fixtures', Path(__file__).with_name('test_bias_qc_inspection.py'))
fixtures = importlib.util.module_from_spec(spec);spec.loader.exec_module(fixtures)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--chromium', type=Path, required=True)
    a = p.parse_args();a.work.mkdir(parents=True)
    target = a.work/'synthetic-bias-qc.html'
    target.write_text(fixtures.view.render(fixtures.sample_data(a.work)))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=str(a.chromium))
        page = browser.new_page(viewport=dict(width=1440,height=1000))
        errors,requests=[],[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('request',lambda request:requests.append(request.url))
        page.goto(target.resolve().as_uri())
        page.wait_for_selector('#plot svg')
        assert page.locator('#products tr').count()==3
        assert 'Incomplete collection' in page.locator('#errors').inner_text()
        assert 'shared by 3 products' in page.locator('#products').inner_text()
        assert page.locator('#plot path[data-row]').count()==1
        assert page.locator('#plot circle[data-row]').count()==4
        assert page.locator('#measurements tr').count()==15
        page.locator('#plot path[data-row]').first.click()
        assert 'read_noise' in page.locator('#detail').inner_text()
        original_requests=list(requests)
        # Change product only: all other measurements remain loaded and visible.
        page.select_option('#product',label='master-old.asdf')
        assert page.locator('#plot path[data-row]').count()==2
        assert page.locator('#plot circle[data-row]').count()==3
        assert page.locator('#measurements tr').count()==15
        assert page.locator('#measurements tr.selected').count()==6
        # Missing values are tabulated and never plotted as zero.
        page.fill('#search','variance')
        assert page.locator('#measurements tr').count()==5
        assert 'unavailable' in page.locator('#measurements').inner_text()
        page.fill('#search','');page.select_option('#detector',label='CCD_B')
        assert page.locator('#plot path[data-row]').count()==1
        assert page.locator('#plot circle[data-row]').count()==1
        page.select_option('#detector',label='All detectors')
        page.select_option('#scope',value='input')
        assert page.locator('#measurements tr').count()==150
        page.locator('#next').click()
        assert 'Page 2 / 3' in page.locator('#page').inner_text()
        page.select_option('#table-mode',value='metric')
        assert page.locator('#measurements tr').count()==10
        assert requests==original_requests, 'Selection reopened a resource'
        assert not errors, errors
        # Check touch-width layout and then retain a desktop overview.
        page.set_viewport_size(dict(width=390,height=844))
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Mobile page overflow'
        page.set_viewport_size(dict(width=1440,height=1000))
        page.select_option('#scope',value='product');page.select_option('#table-mode',value='all')
        page.locator('#provenance').locator('..').evaluate('(el)=>el.open=true')
        page.screenshot(path=str(a.work/'overview.png'),full_page=True)
        browser.close()
    print('PASS: real Chromium product/metric/detector selection, unavailable values, pagination, no refetch, mobile width and no JS errors.')


if __name__=='__main__':
    main()
