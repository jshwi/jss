const $ = require("jquery");

class Tracker {
  constructor(int) {
    this.val = int;
  }

  setVal(int) {
    this.val = int;
  }

  getVal() {
    return this.val;
  }
}

const tracker = new Tracker(0);

/**
 * [Set the count for number of messages held.]
 * @function setMessageCount
 * @param n
 */
function setMessageCount(n) {
  const count = $("#message_count");
  count.text(n);
  count.css("visibility", n ? "visible" : "hidden");
}

/**
 * [Set the percentage to show for task progress.]
 * @function setTaskProgress
 */
function setTaskProgress(data) {
  $(`#${data.task_id}-progress`).text(data.progress);
}

function whenDone(notifications) {
  Object.keys(notifications).forEach((i) => {
    const obj = notifications[i];
    switch (obj.name) {
      case "unread_message_count":
        setMessageCount(obj.data);
        break;
      case "task_progress":
        setTaskProgress(obj.data);
        break;
      default:
        break;
    }
    tracker.setVal(obj.timestamp);
  });
}

/* istanbul ignore next */
function ajax(url) {
  $.ajax(`${url}?since${tracker.getVal()}`).done((notifications) => {
    whenDone(notifications);
  });
}

/* istanbul ignore next */
function getCount(url) {
  tracker.setVal(0);
  setInterval(() => {
    ajax(url);
  }, 10000);
}

/* istanbul ignore next */
function getMessageCount(url) {
  $(() => {
    getCount(url);
  });
}

module.exports = {
  setTaskProgress,
  setMessageCount,
  getMessageCount,
  whenDone,
  tracker,
  $,
};
