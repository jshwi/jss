/**
 * main.js
 * =======
 * [Sourced functions for HTML scripts.]
 */
const currentTheme = window.localStorage.getItem('theme')
const toggleSwitch = document.querySelector('input[type="checkbox"]')
const darkreader = require('darkreader')
const $ = require('jquery')

const hljs = require('highlight.js/lib/core')
const moment = require('moment')

hljs.registerLanguage('python', require('highlight.js/lib/languages/python'))

hljs.highlightAll()

// noinspection JSUnresolvedFunction
darkreader.setFetchMethod(window.fetch)

// trigger on import
// determine the saved state (if there is one)
if (currentTheme) {
  document.documentElement.setAttribute('data-theme', currentTheme)
  if (currentTheme === 'dark') {
    toggleSwitch.checked = true
    darkreader.enable({
      brightness: 100,
      contrast: 90,
      sepia: 10
    })
  }
}

// noinspection JSUnusedGlobalSymbols
/**
 * [Set the count for number of messages held.]
 * @function setMessageCount
 * @param n
 */
// eslint-disable-next-line no-unused-vars
function setMessageCount (n) {
  const messageCount = $('#message_count')
  messageCount.text(n)
  messageCount.css('visibility', n ? 'visible' : 'hidden')
}

// noinspection JSUnusedGlobalSymbols
/**
 * [Set the percentage to show for task progress.]
 * @function setTaskProgress
 * @param {String} taskID
 * @param {String} progress
 */
// eslint-disable-next-line no-unused-vars
function setTaskProgress (taskID, progress) {
  $(`#${taskID}-progress`).text(progress)
}

/**
 * [Toggle between light and dark mode.]
 * @function toggleDarkReader
 */
function toggleDarkReader () {
  if (toggleSwitch.checked === true) {
    document.documentElement.setAttribute('data-theme', 'dark')
    window.localStorage.setItem('theme', 'dark')
    darkreader.enable({
      brightness: 100,
      contrast: 90,
      sepia: 10
    })
  } else {
    document.documentElement.setAttribute('data-theme', 'light')
    window.localStorage.setItem('theme', 'light')
    darkreader.disable()
  }
}

// default to false if no saved state
toggleSwitch.addEventListener('change', toggleDarkReader, false)

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/static/build/service-worker.js')
      .then((registration) => {
        console.log('SW registered: ', registration)
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError)
      })
  })
}

moment.locale('en')

function flaskMomentRender (elem) {
  const timestamp = moment(elem.dataset.timestamp)
  const func = elem.dataset.function
  const { format } = elem.dataset
  const { timestamp2 } = elem.dataset
  const noSuffix = elem.dataset.nosuffix
  const { units } = elem.dataset
  const args = []
  if (format) args.push(format)
  if (timestamp2) args.push(moment(timestamp2))
  if (noSuffix) args.push(noSuffix)
  if (units) args.push(units)
  elem.textContent = timestamp[func](...args)
  elem.classList.remove('flask-moment')
  elem.style.display = ''
}

function flaskMomentRenderAll () {
  const moments = document.querySelectorAll('.flask-moment')
  moments.forEach((m) => {
    flaskMomentRender(m)
    const { refresh } = m.dataset
    if (refresh && refresh > 0) {
      (function onRefresh (elem, interval) {
        setInterval(() => {
          flaskMomentRender(elem)
        }, interval)
      })(m, refresh)
    }
  })
}

document.addEventListener('DOMContentLoaded', flaskMomentRenderAll)

// noinspection JSUnusedGlobalSymbols
module.exports = { toggleDarkReader, setMessageCount, setTaskProgress }
