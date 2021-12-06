/* eslint-env jest */
// noinspection JSUnusedLocalSymbols

const darkreader = require("darkreader");
const $ = require("jquery");
const main = require("../assets/js/main");
const messages = require("../assets/js/messages");
const DarkMode = require("../assets/js/darkMode");

describe("test dark-mode", () => {
  it('should have called `localStorage.getItem` with "theme"', () => {
    // eslint-disable-next-line no-unused-vars
    const darkMode = new DarkMode();
    expect(localStorage.getItem).toHaveBeenCalledWith("theme");
  });
  it.each`
    theme
    ${"dark"}
    ${"light"}
  `(
    'should have called `documentElement` with "data-theme" and "$theme"',
    ({ theme }) => {
      localStorage.setItem("theme", theme);
      const myMock = jest.spyOn(document.documentElement, "setAttribute");
      // eslint-disable-next-line no-unused-vars
      const darkMode = new DarkMode();
      expect(myMock).toHaveBeenCalledWith("data-theme", theme);
    }
  );
  it.each`
    checked  | mode         | theme
    ${false} | ${"disable"} | ${"light"}
    ${true}  | ${"enable"}  | ${"dark"}
  `("should be $theme", ({ checked, mode, theme }) => {
    const darkMode = new DarkMode();
    darkMode.toggleSwitch.checked = checked;
    const spyOnDocument = jest.spyOn(document.documentElement, "setAttribute");
    const spyOnDarkReader = jest.spyOn(darkreader, mode);
    darkMode.toggle();
    expect(spyOnDocument).toHaveBeenCalledWith("data-theme", theme);
    expect(spyOnDarkReader).toHaveBeenCalled();
  });
  it("should have been called with event listener", () => {
    const darkMode = new DarkMode();
    const addEventListener = jest.fn();
    darkMode.toggleSwitch.addEventListener = addEventListener;
    darkMode.addToggleListener();
    expect(addEventListener).toHaveBeenCalledWith(
      "change",
      darkMode.toggle,
      false
    );
  });
});

describe("test service worker", () => {
  let events = {};
  Object.defineProperty(global, "navigator", {
    writable: true,
    value: {},
  });
  beforeEach(() => {
    events = {};
    window.addEventListener = jest
      .fn()
      .mockImplementation((event, callback) => {
        events[event] = callback;
      });
  });
  it("should not have been passed to `window.addEventListener`", () => {
    // noinspection JSValidateTypes
    const spy = jest.spyOn(window, "addEventListener");
    main.registerServiceWorker();
    expect(spy).not.toBeCalled();
  });
  it.each`
    promise
    ${"resolve"}
    ${"reject"}
  `("should $promise", ({ promise }) => {
    expect.assertions(2);
    const serviceWorker = {
      register: jest.fn(() => Promise[promise]()),
    };
    // noinspection JSValidateTypes
    global.navigator.serviceWorker = serviceWorker;
    const spyOnWindowAddEventListener = jest.spyOn(window, "addEventListener");
    main.registerServiceWorker();
    events.load();
    expect(spyOnWindowAddEventListener).toBeCalled();
    expect(serviceWorker.register).toBeCalledWith(
      "/static/build/service-worker.js"
    );
  });
});

describe("test messages", () => {
  const dummyUrl = "/dummy/url";
  it.each`
    n    | visibility
    ${0} | ${"hidden"}
    ${1} | ${"visible"}
  `("should be $visibility", ({ n, visibility }) => {
    const spyOn$Text = jest.spyOn($.fn, "text");
    const spyOn$Css = jest.spyOn($.fn, "css");
    messages.setMessageCount(n);
    expect(spyOn$Text).toHaveBeenCalledWith(n);
    expect(spyOn$Css).toHaveBeenCalledWith("visibility", visibility);
  });
  it("should have been called with progress", () => {
    const data = { progress: Math.random().toString() };
    const spyOn$Text = jest.spyOn($.fn, "text");
    messages.setTaskProgress(data);
    expect(spyOn$Text).toHaveBeenCalledWith(data.progress);
  });
  it("should work with ajax", () => {
    window.$ = jest.fn();
    messages.getMessageCount(dummyUrl);
  });
  it.each`
    name
    ${"unread_message_count"}
    ${"task_progress"}
    ${"other"}
  `("should call correct function", ({ name }) => {
    const timestamp = Math.random();
    const data = {
      progress: Math.random().toString(),
      task_id: Math.random().toString(),
    };
    const notification = { name, data, timestamp };
    const notifications = [notification];
    messages.whenDone(notifications);
    expect(messages.tracker.getVal()).toEqual(timestamp);
  });
});
