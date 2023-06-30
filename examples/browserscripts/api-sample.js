const { assert } = require("chai");

(async function () {
  /**
   * manipulate headers and retrieve all the customized headers
   */
  await $browser.addHeader("test", "test");
  await $browser.addHeaders({ "test1": "test1", "test2": "test2" });
  await $browser.deleteHeaders(["test1", "test2"]);
  $browser.getHeaders().forEach((value, key) => console.log(">>>>>>>>>>>>>>>>>>>", "User customized headers: ", key + "=" + value));

  /**
   * manipulate black and white list
   */
  await $browser.addHostnamesToBlacklist(["*google*", "*timeanddate*"]);
  await $browser.deleteHostnameFromBlacklist("*timeanddate*");

  /**
   * open url www.bing.com
   * find element by class selector
   * send keys to search synthetic in the page
   */
  console.log(">>>>>>>>>>>>>>>>>>>", "Access bing page");
  await $browser.get("http://www.bing.com");
  console.log(">>>>>>>>>>>>>>>>>>>", "Actions of search");
  await $browser.$(".sb_form_q");
  await $browser.actions().sendKeys("synthetic").sendKeys($driver.Key.ENTER).perform();

  /**
   * samples of getting current window handle
   * switch to a new window
   * open new page in new tab
   * 
   */
  console.log(">>>>>>>>>>>>>>>>>>>", "Windows handle: ", await $browser.getWindowHandle(), "Current url: ", await $browser.getCurrentUrl());
  console.log(">>>>>>>>>>>>>>>>>>>", "switch to calendar tab");
  let originalWindow = await $browser.getWindowHandle();
  await $browser.switchTo().newWindow();

  /**
   * navigate to www.timeanddate.com
   * assert page title by getTitle() api
   * assert page title by getPageSource() api
   */
  console.log(">>>>>>>>>>>>>>>>>>>", "Access time and date page");
  await $browser.get("http://www.timeanddate.com");
  let page = await $browser.getPageSource();
  assert.isTrue(page.includes("<title>timeanddate.com</title>"));
  console.log(">>>>>>>>>>>>>>>>>>>", "Page title: ", await $browser.getTitle());

  /**
   * get session and session id
   */
  let session = await $browser.getSession();
  console.log(">>>>>>>>>>>>>>>>>>>", "Session id: ", session.getId());

  /**
   * manage window size
   */
  await $browser.manage().window().maximize();

  /**
   * samples of finding element or elements by id or tag name
   */
  let elem = await $browser.waitForAndFindElement($driver.By.id("boxyear"), 1000);
  await elem.click();
  assert.equal("2023", await elem.getAttribute("value"));
  assert.equal("2023", await $browser.$('#boxyear').getAttribute("value"));

  let selLength = (await $browser.$$("<select>")).length;
  console.log(">>>>>>>>>>>>>>>>>>>", `There are ${selLength} selects`);
  let selects = await $browser.findElements($driver.By.css('select'));
  assert.equal(2, selects.length);
  for (const select of selects) {
    console.log(">>>>>>>>>>>>>>>>>>>", "Found select element: ", await select.getAttribute("name"));
  }

  let elems = await $browser.$$(".rd-box");
  for (const elem of elems) {
    console.log(">>>>>>>>>>>>>>>>>>>", "Four box titles: ", await elem.$('h2').$('a').getText());
  }

  /**
   * samples of finding a input button by value and click the button
   * wait until the title comes out
   * take a screenshot
   */
  await $browser.$('[value="View calendar"]').click();
  await $browser.wait($driver.until.titleContains('Year 2023 Calendar'), 10000);
  await $browser.takeScreenshot();

  /**
   * switch back to original window
   * take screenshot
   */
  await $browser.switchTo().window(originalWindow);
  await $browser.takeScreenshot();

  /**
   * samples of promise chain invocation, which is not recommended but compatible 
   * samples of waiting and polling function until timeout
   */
  $browser.deleteHostnameFromBlacklist("*google*");
  $browser.get("https://www.google.com");
  // Call the wait function.
  $browser.wait(function () {
    return $browser.getTitle().then(function (title) {
      return title.includes("Google");
    });
    //If the condition isn't satisfied within 10000 milliseconds (10 seconds), proceed anyway.
  }, 10000).then(function () {
    return $browser.findElement($driver.By.linkText("About")).click();
  }).then(function () {
    return $browser.navigate().back();
  });

})();
