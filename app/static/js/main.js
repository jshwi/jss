/**
 * main.js
 * =======
 * [Sourced functions for HTML scripts.]
 */

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
