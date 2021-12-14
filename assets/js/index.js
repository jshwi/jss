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
require("darkreader");
const hljs = require("highlight.js/lib/core");
const $ = require("jquery");
const {
  toggleDarkReader,
  initTheme,
  toggleSwitch,
  registerServiceWorker,
} = require("./main");
const {
  setMessageCount,
  setTaskProgress,
  getMessageCount,
  whenDone,
} = require("./messages");

// noinspection JSUnresolvedFunction
require.context("../img", true, /.*/);
require("../xml/browserconfig.xml");

hljs.registerLanguage("python", require("highlight.js/lib/languages/python"));

hljs.highlightAll();

initTheme();

registerServiceWorker();

// default to false if no saved state
toggleSwitch.addEventListener("change", toggleDarkReader, false);

module.exports = {
  toggleDarkReader,
  setMessageCount,
  setTaskProgress,
  getMessageCount,
  $,
  whenDone,
};
