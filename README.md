# Progress Documentation

- RPA
- About Robot Framework
- Automated testing softwares
- robocorp
- various libraries in robocorp

This document summarises all Robocorp RPA concepts studied through self-directed learning, and hands-on practice.

From the most basic concepts about RPA and how different tech stacks are used to help with the automation process

- base framwork,
- robocorp.* python packages
- environments - conda.yaml, uv and rcc
- browser automation with both playwright and selenium

Task Package file structure
___

| Files                   | usage                                                                          |
| ----------------------- | ------------------------------------------------------------------------------ |
| robot.yaml              | Robot manifest - entry point, task names, output dir                           |
| conda.yaml              | Defines Python version + all pip dependencies for RCC holotreev (environments) |
| tasks.py / tasks.robot  | Entry point - @task functions or *** Tasks *** section                         |
| devdata/env.json        | Local env variabless - points vault and work items to local files              |
| devdata/vault.json      | Local plaintext secrets (gitignored - never commit)                            |
| devdata/work-items-in/  | test input work item payloads for local runs                                   |
| devdata/work-items-out/ | output work items written here during local runs                               |
| libraries/              | custom Python helper modules imported by tasks.py                              |
| resources/              | Excel templates, PDFs, CSVs, locator files                                     |
| output/                 | Generates - log.html, report.html, screenshots                                 |

Core Libraries
___
Robocorp libraries come in two versions. The RPA.* libraries are the older Robot Framework style. The robocorp.* packages are the newly created python equivalents.

Browser automation
- `robocorp.browser`
- `RPA.Browser`

Data and files
- `robcorp.excel`, `RPA.Excel.Files`
- `RPA.Tables`, `RPA.PDF`, `RPA.Filesystem`

http, email
- `robocorp.http`, `RPA.http`
- `RPA.Email.Imapsmtp`

general
- `robocorp.vault` (for fetching secrets)
- `robocorp.workitems`
- `robocorp.tasks`
- `robocor.log`

Locating Items with Playwright
___
```python
page.get_by_label('Email') — by associated label text
page.get_by_placeholder('Enter email') — by placeholder attribute
page.get_by_text('Order confirmed') — by visible text
page.locator('#email') — CSS selector (id)
page.locator('.btn-primary') — CSS selector (class)
page.locator('xpath=//button[@type=submit]') — XPath
page.frame_locator('#iframe-id') — enter an iFrame context
page.locator('host >>> input') — pierce Shadow DOM
```

working with work items (data)
___
Work items are the core mechanism for processing data at scale in production robocorp deployments. They allow robots to process large queues of data with individual failure tracking, retry logic, and parallel execution

All the information in the payload are stored in dictionaries

a template for using work item
```python
@task
def process_orders():
	for item in workitems.inputs:
		try:
			payload = item.payload # your data dict
			name = payload['Name']
			process(name)
			item.done()
		except BusinessException:
			raise   # data is wrong, stop retrying (wrong format or other issues)
		except Exception as e:
			raise ApplicationException(str(e)) from e #error while trying to communicate the data
```

working with Files and API
___
- `import requests` for API http requests
	- The standard POST, GET, PUT and DELETE requests
	- api needs its own credentials sometimes when the backend is secure
##### Files
- For working with excel files we use the `open_workbook` package
- `read_csv` and `write_csv` for csv files
- Apart from that `pandas` can be used to manipulate data
- PDFs have many ways to be read from 
	```python
	open_pdf()
	text = pdf.get_text_from_pdf()
	# for metadata
	info = pdf.get_pdf_info()
	# and much more
	```
	regex can also be used to get info from pdf

	pdf package can also be used to create pdf's with data, append information later, manipulate visuals (images, tables, text) and merge multiples pdfs into one


Authentication challenges
___
- SSL/Oauth
	Once the login ceredential are filled
	-  wait for OTP input page to appear
	- connect to email with IMAP (SSL, port 993) and poll for the OTP email
	- find the mail using filters
	- extract n-numbered code from email body using regex
	- fill OTP field on website, submit, confirm login success
- Session cookie reuse?
	- `browser.context().storage_state()` saves auth state. Reloading next run will skip login entirely


web automation
___
- File upload	`page.set_input_files('input[type=file]', path)`
- File download with `page.expect_download()`
- iFrames - `page.frame_locator('#iframe-id')` switch context, then use normal locators inside
- Dynamic content `page.wait_for_selector()`, `page.wait_for_load_state('networkidle')`
- Pop-ups / dialogs	`page.on('dialog', lambda d: d.accept())` - register handler before triggering
- New tab handling	`browser.context().expect_page()`  capture new page when opened

solutions that ive used to capture failures while using robots
___
- screenshot on failure - wrap task in try/except, call browser.screenshot() before re-raising
- Retry - @retry(times=3, delay=2) for wrapping error prone functions


Hands-On Work
___
folders on github can be viewed for deployed robots (local)