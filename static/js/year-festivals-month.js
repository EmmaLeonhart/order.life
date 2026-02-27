'use strict';
/**
 * year-festivals-month.js — Per-month zoomed-in festivals view.
 * Shows all 28 days with Gregorian correspondence dates, and expands
 * holiday days into full cards with Gregorian extension bridges.
 * Requires: GAIAN_YEAR, GAIAN_MONTH constants and GAIAN_FIXED_EXTENSIONS
 * (from festival-data.js) before this script runs.
 */

(function () {

  var MONTH_NAMES = [
    'Sagittarius','Capricorn','Aquarius','Pisces','Aries','Taurus',
    'Gemini','Cancer','Leo','Virgo','Libra','Scorpius','Ophiuchus','Horus'
  ];
  var MONTH_SYMBOLS = [
    '♐','♑','♒','♓','♈','♉','♊','♋','♌','♍','♎','♏','⛎','𓅃'
  ];
  var GREG_MONTHS_FULL = [
    'January','February','March','April','May','June',
    'July','August','September','October','November','December'
  ];
  var GREG_MONTHS_SHORT = [
    'Jan','Feb','Mar','Apr','May','Jun',
    'Jul','Aug','Sep','Oct','Nov','Dec'
  ];
  var WD_ABBR = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

  function isoWeek1Start(y) {
    var jan4 = new Date(y, 0, 4);
    var dow  = jan4.getDay() || 7;
    var mon  = new Date(jan4);
    mon.setDate(jan4.getDate() - (dow - 1));
    mon.setHours(0, 0, 0, 0);
    return mon;
  }

  function run() {
    var container = document.getElementById('mfm-container');
    if (!container) return;

    var gaianYear  = window.GAIAN_YEAR;
    var gaianMonth = window.GAIAN_MONTH;
    var isoYear    = gaianYear - 10000;
    var basePath   = window.LANG_BASE || '';

    var weekStart    = isoWeek1Start(isoYear);
    var startOffset  = gaianMonth <= 13 ? (gaianMonth - 1) * 28 : 364;
    var daysInMonth  = gaianMonth === 14 ? 7 : 28;

    // Compute Gregorian date for each day of this month
    var gregDates = [];
    for (var i = 0; i < daysInMonth; i++) {
      gregDates.push(new Date(weekStart.getTime() + (startOffset + i) * 86400000));
    }

    var firstGreg = gregDates[0];
    var lastGreg  = gregDates[daysInMonth - 1];
    var gregRange =
      firstGreg.getDate() + '\u00a0' + GREG_MONTHS_FULL[firstGreg.getMonth()] + '\u00a0' + firstGreg.getFullYear() +
      ' – ' +
      lastGreg.getDate() + '\u00a0' + GREG_MONTHS_FULL[lastGreg.getMonth()] + '\u00a0' + lastGreg.getFullYear();

    // Update subheading
    var sub = document.getElementById('mfm-subheading');
    if (sub) sub.textContent = gregRange;

    // Get holidays for this month from GAIAN_FIXED_EXTENSIONS
    var extensions = (typeof GAIAN_FIXED_EXTENSIONS !== 'undefined') ? GAIAN_FIXED_EXTENSIONS : [];
    var holByDay = {};
    extensions.forEach(function (h) {
      if (h.month === gaianMonth) holByDay[h.day] = h;
    });

    // Prev / next month numbers (skip Horus in nav — it's rare)
    var prevM = gaianMonth > 1 ? gaianMonth - 1 : null;
    var nextM = gaianMonth < 13 ? gaianMonth + 1 : null;

    function monthHref(m) {
      return basePath + '/calendar/' + gaianYear + '/festivals/' + pad2(m) + '/';
    }

    function pad2(n) { return n < 10 ? '0' + n : '' + n; }

    // ── Navigation bar ────────────────────────────────────────────────────────
    var navHtml = '<div class="mfm-nav">';
    if (prevM) {
      navHtml += '<a class="mfm-nav-btn" href="' + monthHref(prevM) + '">← ' + MONTH_SYMBOLS[prevM - 1] + '\u00a0' + MONTH_NAMES[prevM - 1] + '</a>';
    } else {
      navHtml += '<span></span>';
    }
    navHtml += '<a class="mfm-nav-btn mfm-nav-year" href="' + basePath + '/calendar/' + gaianYear + '/festivals/">↑ All of ' + gaianYear + '</a>';
    if (nextM) {
      navHtml += '<a class="mfm-nav-btn" href="' + monthHref(nextM) + '">' + MONTH_SYMBOLS[nextM - 1] + '\u00a0' + MONTH_NAMES[nextM - 1] + ' →</a>';
    } else {
      navHtml += '<span></span>';
    }
    navHtml += '</div>';

    // ── Day list ──────────────────────────────────────────────────────────────
    var listHtml = '<div class="mfm-list">';

    for (var d = 1; d <= daysInMonth; d++) {
      var gd      = gregDates[d - 1];
      var wd      = WD_ABBR[(d - 1) % 7];
      var isSab   = (d - 1) % 7 >= 4;          // Fri=4, Sat=5, Sun=6
      var hol     = holByDay[d] || null;
      var gregStr = gd.getDate() + ' ' + GREG_MONTHS_SHORT[gd.getMonth()] + ' ' + gd.getFullYear();
      var dayHref = basePath + '/calendar/' + gaianYear + '/' + pad2(gaianMonth) + '/' + pad2(d) + '/';

      if (hol) {
        // ── Holiday row (expanded) ────────────────────────────────────────
        var bridgesHtml = '';
        if (hol.extensions && hol.extensions.length) {
          bridgesHtml = '<div class="mfm-bridges">';
          hol.extensions.forEach(function (ext) {
            var greg = GREG_MONTHS_SHORT[ext.greg_month - 1] + '\u00a0' + ext.greg_day;
            var qidHtml = ext.qid
              ? ' <a href="https://www.wikidata.org/wiki/' + ext.qid + '" target="_blank" rel="noopener" class="mfm-qid">' + ext.qid + '</a>'
              : '';
            bridgesHtml +=
              '<span class="mfm-bridge">' +
                '<span class="mfm-arrow">→</span>' +
                '<span class="mfm-bname">' + ext.name + '</span>' +
                '<span class="mfm-bdate">' + greg + '</span>' +
                qidHtml +
              '</span>';
          });
          bridgesHtml += '</div>';
        }

        listHtml +=
          '<div class="mfm-row mfm-hol-row' + (isSab ? ' mfm-sabbath' : '') + '">' +
            '<div class="mfm-row-main">' +
              '<a href="' + dayHref + '" class="mfm-dnum">' + d + '</a>' +
              '<span class="mfm-wd' + (isSab ? ' mfm-wd-sab' : '') + '">' + wd + '</span>' +
              '<span class="mfm-hname">' + hol.emoji + '\u00a0' + hol.summary + '</span>' +
              '<span class="mfm-greg">' + gregStr + '</span>' +
            '</div>' +
            bridgesHtml +
          '</div>';

      } else {
        // ── Plain day row ─────────────────────────────────────────────────
        listHtml +=
          '<div class="mfm-row' + (isSab ? ' mfm-sabbath' : '') + '">' +
            '<div class="mfm-row-main">' +
              '<a href="' + dayHref + '" class="mfm-dnum">' + d + '</a>' +
              '<span class="mfm-wd' + (isSab ? ' mfm-wd-sab' : '') + '">' + wd + '</span>' +
              '<span class="mfm-greg">' + gregStr + '</span>' +
            '</div>' +
          '</div>';
      }
    }

    listHtml += '</div>';

    container.innerHTML = navHtml + listHtml;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }

})();
