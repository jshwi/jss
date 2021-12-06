const darkreader = require("darkreader");

// noinspection JSUnresolvedFunction
darkreader.setFetchMethod(window.fetch);

// trigger on import
// determine the saved state (if there is one)
class DarkMode {
  constructor() {
    this.toggleSwitch = document.querySelector('input[type="checkbox"]');
    this.currentTheme = window.localStorage.getItem("theme") || "light";
    this.toggleSwitch.checked = this.currentTheme === "dark";
    this.toggle();
  }

  addToggleListener() {
    // default to false if no saved state
    this.toggleSwitch.addEventListener("change", this.toggle, false);
  }

  /**
   * [Toggle between light and dark mode.]
   */
  toggle() {
    if (this.toggleSwitch.checked) {
      this.currentTheme = "dark";
      darkreader.enable({
        brightness: 100,
        contrast: 90,
        sepia: 10,
      });
    } else {
      this.currentTheme = "light";
      darkreader.disable();
    }
    document.documentElement.setAttribute("data-theme", this.currentTheme);
    window.localStorage.setItem("theme", this.currentTheme);
  }
}

module.exports = DarkMode;
