/*
 * index
 * =====
 * Main Javascript file for app.
 *
 * This file bundles all JavaScript files together using ``Webpack``.
 */
const DarkMode = require("./darkMode");
const registerServiceWorker = require("./serviceWorker");

// noinspection JSUnresolvedFunction
require.context("../img", true, /.*/);
require("../xml/browserconfig.xml");

const darkMode = new DarkMode();

document.addEventListener("DOMContentLoaded", () => {
  registerServiceWorker();
  darkMode.addToggleListener();
});

module.exports = {
  darkMode,
};
