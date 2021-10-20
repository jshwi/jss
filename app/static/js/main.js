/**
 * main.js
 * =======
 * [Sourced functions for HTML scripts.]
 */
const current_theme = localStorage.getItem("theme");
const toggle_switch = document.querySelector('input[type="checkbox"]');
const darkreader = document.getElementById("darkreader");

// trigger on import
// determine the saved state (if there is one)
if (current_theme) {
  document.documentElement.setAttribute("data-theme", current_theme);
  if (current_theme === "dark") {
    toggle_switch.checked = true;
    darkreader.disabled = undefined;
  }
}

/**
 * [Set the count for number of messages held.]
 * @function set_message_count
 * @param n
 */
function set_message_count(n) {
  let message_count = $("#message_count");
  message_count.text(n);
  message_count.css("visibility", n ? "visible" : "hidden");
}

/**
 * [Set the percentage to show for task progress.]
 * @function set_task_progress
 * @param {String} task_id
 * @param {String} progress
 */
function set_task_progress(task_id, progress) {
  $("#" + task_id + "-progress").text(progress);
}

/**
 * [Toggle between light and dark mode.]
 * @function toggle_darkreader
 */
function toggle_darkreader() {
  if (toggle_switch.checked === true) {
    document.documentElement.setAttribute("data-theme", "dark");
    localStorage.setItem("theme", "dark");
    darkreader.disabled = undefined;
  } else {
    document.documentElement.setAttribute("data-theme", "light");
    localStorage.setItem("theme", "light");
    darkreader.disabled = "disabled";
  }
}

// default to false if no saved state
toggle_switch.addEventListener("change", toggle_darkreader, false);
