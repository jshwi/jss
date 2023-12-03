const hljs = require("highlight.js/lib/core");
const hljsPython = require("highlight.js/lib/languages/python");
const hljsShell = require("highlight.js/lib/languages/shell");
const hljsYaml = require("highlight.js/lib/languages/yaml");
const hljsIni = require("highlight.js/lib/languages/ini");

hljs.registerLanguage("python", hljsPython);
hljs.registerLanguage("shell", hljsShell);
hljs.registerLanguage("yaml", hljsYaml);
hljs.registerLanguage("ini", hljsIni);

document.addEventListener("DOMContentLoaded", () => {
  hljs.highlightAll();
});
