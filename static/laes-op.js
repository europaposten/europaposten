/* Læs op: oplæsning af artikler med browserens indbyggede talesyntese (Web Speech API).
   Ingen eksterne tjenester. Teksten læses afsnit for afsnit, så lange artikler også
   virker i Chrome (der afbryder lange ytringer) og på iOS Safari. */
(function () {
  "use strict";
  var box = document.querySelector(".laes-op");
  if (!box) return;
  var synth = window.speechSynthesis;
  if (!synth || typeof window.SpeechSynthesisUtterance !== "function") return; // knappen forbliver skjult

  var btn = box.querySelector(".laes-op-knap");
  var stopBtn = box.querySelector(".laes-op-stop");
  var status = box.querySelector(".laes-op-status");
  var state = "idle"; // idle | playing | paused
  var queue = [];
  var idx = 0;
  var voice = null;
  var keepAlive = null;
  var session = 0;
  var MAX = 220; // tegn pr. ytring – holder Chrome stabil

  function pickVoice() {
    var voices = synth.getVoices() || [];
    var da = voices.filter(function (v) { return /^da([-_]|$)/i.test(v.lang); });
    voice = da.filter(function (v) { return /dk/i.test(v.lang) && v.localService; })[0] ||
            da.filter(function (v) { return /dk/i.test(v.lang); })[0] || da[0] || null;
  }
  pickVoice();
  if ("onvoiceschanged" in synth) synth.addEventListener("voiceschanged", pickVoice);

  function clean(t) { return (t || "").replace(/\s+/g, " ").trim(); }

  // Del lange afsnit ved sætningsgrænser (og som nødløsning ved mellemrum).
  function split(text) {
    if (text.length <= MAX) return [text];
    var out = [], cur = "";
    var parts = text.match(/[^.!?;:]+[.!?;:]*["”»«')]*\s*/g) || [text];
    parts.forEach(function (s) {
      if ((cur + s).length > MAX && cur) { out.push(cur.trim()); cur = ""; }
      while (s.length > MAX) {
        var cut = s.lastIndexOf(" ", MAX);
        if (cut < 40) cut = MAX;
        out.push(s.slice(0, cut).trim()); s = s.slice(cut);
      }
      cur += s;
    });
    if (cur.trim()) out.push(cur.trim());
    return out;
  }

  function collect() {
    var story = box.closest("article") || document;
    var items = [];
    var h1 = story.querySelector(".story-head h1");
    if (h1) { var ht = clean(h1.textContent); items.push(/[.!?:]$/.test(ht) ? ht : ht + "."); }
    var sf = story.querySelector(".story-head .standfirst");
    if (sf) items.push(clean(sf.textContent));
    var body = story.querySelector(".story-body");
    if (body) {
      var nodes = body.querySelectorAll("p, h2, h3, h4, li, blockquote, td, th");
      Array.prototype.forEach.call(nodes, function (el) {
        if (el.closest("figcaption, .ad-slot, .story-illustration, nav, footer, script, style, [aria-hidden='true']")) return;
        // undgå dobbeltlæsning af indlejrede elementer
        if (el.parentElement && el.parentElement.closest("p, li, blockquote, td, th") &&
            body.contains(el.parentElement.closest("p, li, blockquote, td, th"))) return;
        var t = clean(el.textContent);
        if (t) items.push(t);
      });
    }
    var out = [];
    items.forEach(function (t) { out = out.concat(split(t)); });
    return out;
  }

  function setState(s) {
    state = s;
    box.classList.toggle("is-active", s !== "idle");
    stopBtn.hidden = s === "idle";
    var label = s === "playing" ? "Pause" : s === "paused" ? "Fortsæt" : "Læs op";
    var aria = s === "playing" ? "Sæt oplæsningen på pause" : s === "paused" ? "Fortsæt oplæsningen" : "Læs artiklen op";
    btn.querySelector(".laes-op-tekst").textContent = label;
    btn.setAttribute("aria-label", aria);
    btn.setAttribute("aria-pressed", s === "playing" ? "true" : "false");
    status.textContent = s === "playing" ? "Oplæsning i gang" : s === "paused" ? "Oplæsning sat på pause" : "";
  }

  function stopKeepAlive() { if (keepAlive) { clearInterval(keepAlive); keepAlive = null; } }

  function speakNext(my) {
    if (my !== session) return;
    if (idx >= queue.length) { stopKeepAlive(); setState("idle"); return; }
    var u = new SpeechSynthesisUtterance(queue[idx]);
    u.lang = "da-DK";
    if (voice) u.voice = voice;
    u.rate = 1;
    u.onend = function () { if (my !== session) return; idx++; speakNext(my); };
    u.onerror = function (e) {
      if (my !== session) return;
      if (e && (e.error === "interrupted" || e.error === "canceled")) return;
      idx++; speakNext(my);
    };
    synth.speak(u);
  }

  function start() {
    queue = collect();
    if (!queue.length) return;
    idx = 0;
    session++;
    synth.cancel();
    setState("playing");
    var my = session;
    // Chrome-desktop kan gå i stå efter ca. 15 sek.; et let skub holder den i gang.
    stopKeepAlive();
    if (!/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {
      keepAlive = setInterval(function () {
        if (state === "playing" && synth.speaking && !synth.paused) { synth.pause(); synth.resume(); }
      }, 10000);
    }
    speakNext(my);
  }

  function stop() {
    session++;
    stopKeepAlive();
    synth.cancel();
    idx = 0;
    setState("idle");
  }

  btn.addEventListener("click", function () {
    if (state === "idle") start();
    else if (state === "playing") { synth.pause(); setState("paused"); }
    else {
      synth.resume();
      setState("playing");
      // Nogle browsere genoptager ikke korrekt – start da forfra fra det aktuelle afsnit.
      var my = session;
      setTimeout(function () {
        if (my === session && state === "playing" && !synth.speaking) { session++; synth.cancel(); speakNext(session); }
      }, 400);
    }
  });
  stopBtn.addEventListener("click", stop);
  window.addEventListener("pagehide", function () { synth.cancel(); });

  setState("idle");
  box.hidden = false;
})();
