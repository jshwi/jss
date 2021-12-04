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
require("highlight.js");
const $ = require("jquery");
const moment = require("moment");
const {
  toggleDarkReader,
  setMessageCount,
  setTaskProgress,
} = require("./main");

// noinspection JSUnresolvedFunction
require.context("../img", true, /.*/);
require("../xml/browserconfig.xml");

module.exports = {
  toggleDarkReader,
  setMessageCount,
  setTaskProgress,
  moment,
  $,
};
