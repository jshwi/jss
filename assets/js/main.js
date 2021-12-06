/**
 * main.js
 * =======
 * [Sourced functions for HTML scripts.]
 */
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
module.exports = { registerServiceWorker };
