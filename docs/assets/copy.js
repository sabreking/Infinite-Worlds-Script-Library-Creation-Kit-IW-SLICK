(function () {
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var el = document.getElementById(btn.getAttribute("data-copy"));
      if (!el) return;
      var text = el.textContent;
      function ok() {
        var old = btn.textContent;
        btn.textContent = "COPIED!";
        setTimeout(function () { btn.textContent = old; }, 1400);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(ok).catch(selectAll);
      } else {
        selectAll();
      }
      function selectAll() {
        var r = document.createRange();
        r.selectNodeContents(el);
        var s = window.getSelection();
        s.removeAllRanges();
        s.addRange(r);
        btn.textContent = "NOW PRESS CTRL+C";
      }
    });
  });
})();
