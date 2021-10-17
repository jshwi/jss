function set_message_count(n) {
  let message_count = $("#message_count");
  message_count.text(n);
  message_count.css("visibility", n ? "visible" : "hidden");
}
function set_task_progress(task_id, progress) {
  $("#" + task_id + "-progress").text(progress);
}
