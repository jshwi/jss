/* eslint-env jest */
// noinspection JSValidateTypes
require("jest-localstorage-mock");
const nodeCrypto = require("crypto");

const { querySelectorAll } = document;
const windowSetInterval = window.setInterval;

beforeEach(() => {
  // to fully reset the state between tests, clear the storage
  // and reset all mocks
  // clearAllMocks will impact your other mocks too, so you can
  // optionally reset individual mocks instead:
  localStorage.clear();
  jest.clearAllMocks();
  localStorage.setItem.mockClear();
  document.querySelectorAll = querySelectorAll;
  window.setInterval = windowSetInterval;
});

// noinspection JSValidateTypes,JSCheckFunctionSignatures
window.crypto = {
  getRandomValues: (buffer) => nodeCrypto.randomFillSync(buffer),
};

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

Object.defineProperty(document, "querySelector", {
  writable: true,
  value: jest.fn().mockImplementation(() => ({
    checked: null,
  })),
});
