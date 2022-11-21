/*
 * index
 * =====
 * Main Javascript file for app.
 *
 * This file bundles all JavaScript files together using ``Webpack``.
 */
require("@fortawesome/fontawesome-free");
require("jquery");
require("bootstrap");
require("bootstrap-icons/font/bootstrap-icons.css");
require("bootstrap4-toggle");
const $ = require("jquery");
const {
  setMessageCount,
  setTaskProgress,
  getMessageCount,
  whenDone,
} = require("./messages");
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
  setMessageCount,
  setTaskProgress,
  getMessageCount,
  $,
  whenDone,
};
