const $ = require("jquery");
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

function getMessageCount(url) {
  $(() => {
    let since = 0;
    setInterval(() => {
      $.ajax(`${url}?since${since}`).done((notifications) => {
        for (let i = 0; i < notifications.length; i += 1) {
          switch (notifications[i].name) {
            case "unread_message_count":
              setMessageCount(notifications[i].data);
              break;
            case "task_progress":
              // noinspection JSUnresolvedVariable
              setTaskProgress(
                notifications[i].data.task_id,
                notifications[i].data.progress
              );
              break;
            default:
              break;
          }
          since = notifications[i].timestamp;
        }
      });
    }, 10000);
  });
}

module.exports = { setTaskProgress, setMessageCount, getMessageCount };
