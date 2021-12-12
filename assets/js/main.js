/**
 * main.js
 * =======
 * [Sourced functions for HTML scripts.]
 */
const currentTheme = window.localStorage.getItem("theme");
const toggleSwitch = document.querySelector('input[type="checkbox"]');
const darkreader = require("darkreader");
const $ = require("jquery");

// trigger on import
// determine the saved state (if there is one)
function initTheme() {
  if (currentTheme) {
    document.documentElement.setAttribute("data-theme", currentTheme);
    if (currentTheme === "dark") {
      toggleSwitch.checked = true;
      darkreader.enable({
        brightness: 100,
        contrast: 90,
        sepia: 10,
      });
    }
  }
}

// noinspection JSUnusedGlobalSymbols
/**
 * [Set the count for number of messages held.]
 * @function setMessageCount
 * @param n
 */
// eslint-disable-next-line no-unused-vars
function setMessageCount(n) {
  const messageCount = $("#message_count");
  messageCount.text(n);
  messageCount.css("visibility", n ? "visible" : "hidden");
}

// noinspection JSUnusedGlobalSymbols
/**
 * [Set the percentage to show for task progress.]
 * @function setTaskProgress
 * @param {String} taskID
 * @param {String} progress
 */
// eslint-disable-next-line no-unused-vars
function setTaskProgress(taskID, progress) {
  $(`#${taskID}-progress`).text(progress);
}

/**
 * [Toggle between light and dark mode.]
 * @function toggleDarkReader
 */
function toggleDarkReader() {
  if (toggleSwitch.checked === true) {
    document.documentElement.setAttribute("data-theme", "dark");
    localStorage.setItem("theme", "dark");
    darkreader.enable({
      brightness: 100,
      contrast: 90,
      sepia: 10,
    });
  } else {
    document.documentElement.setAttribute("data-theme", "light");
    localStorage.setItem("theme", "light");
    darkreader.disable();
  }
}

function registerServiceWorker() {
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker
        .register("/static/build/service-worker.js")
        .then((registration) => {
          console.log("SW registered: ", registration);
        })
        .catch((registrationError) => {
          console.log("SW registration failed: ", registrationError);
        });
    });
  }
}

// noinspection JSUnusedGlobalSymbols
module.exports = {
  toggleDarkReader,
  setMessageCount,
  setTaskProgress,
  initTheme,
  registerServiceWorker,
  toggleSwitch,
};
