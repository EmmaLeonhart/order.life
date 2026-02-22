'use strict';
/**
 * year-festivals.js — World festivals overlay on the Gaian year calendar.
 * Renders holiday track bars (Chinese / Jewish / Christian / Islamic / Hindu)
 * plus full moon dots. Requires: GAIAN_YEAR constant set before this script.
 */

// ── Shared constants (mirrors year-page.js) ──────────────────────────────────
const GREG_MONTHS_FULL = ['January','February','March','April','May','June',
                           'July','August','September','October','November','December'];
const GREG_MONTHS_SHORT = ['Jan','Feb','Mar','Apr','May','Jun',
                            'Jul','Aug','Sep','Oct','Nov','Dec'];
const WEEKDAYS_FULL = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
const WD_PLANETS = ['\u263D','\u2642','\u263F','\u2643','\u2640','\u2644','\u2609'];
const WD_ABBR    = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

const GAIAN_MONTH_INFO = [
  { num: 1,  id: 'sagittarius', symbol: '\u2650', name: 'Sagittarius' },
  { num: 2,  id: 'capricorn',   symbol: '\u2651', name: 'Capricorn'   },
  { num: 3,  id: 'aquarius',    symbol: '\u2652', name: 'Aquarius'    },
  { num: 4,  id: 'pisces',      symbol: '\u2653', name: 'Pisces'      },
  { num: 5,  id: 'aries',       symbol: '\u2648', name: 'Aries'       },
  { num: 6,  id: 'taurus',      symbol: '\u2649', name: 'Taurus'      },
  { num: 7,  id: 'gemini',      symbol: '\u264A', name: 'Gemini'      },
  { num: 8,  id: 'cancer',      symbol: '\u264B', name: 'Cancer'      },
  { num: 9,  id: 'leo',         symbol: '\u264C', name: 'Leo'         },
  { num: 10, id: 'virgo',       symbol: '\u264D', name: 'Virgo'       },
  { num: 11, id: 'libra',       symbol: '\u264E', name: 'Libra'       },
  { num: 12, id: 'scorpius',    symbol: '\u264F', name: 'Scorpius'    },
  { num: 13, id: 'ophiuchus',   symbol: '\u26CE', name: 'Ophiuchus'   },
  { num: 14, id: 'horus',       symbol: '\uD800\uDD43', name: 'Horus' },
];
const IS_SABBATH = [false, false, false, false, true, true, true];

// ── Utility functions ────────────────────────────────────────────────────────
function isoWeek1Start(y) {
  const jan4 = new Date(y, 0, 4);
  const dow = jan4.getDay() || 7;
  const mon = new Date(jan4);
  mon.setDate(jan4.getDate() - (dow - 1));
  mon.setHours(0, 0, 0, 0);
  return mon;
}
function isoWeeksInYear(y) {
  const dec28 = new Date(y, 11, 28);
  const dow = dec28.getDay() || 7;
  const thu = new Date(dec28);
  thu.setDate(dec28.getDate() + (4 - dow));
  const jan1 = new Date(thu.getFullYear(), 0, 1);
  return Math.ceil((((thu - jan1) / 86400000) + 1) / 7);
}
function easterDate(y) {
  const a = y % 19, b = Math.floor(y / 100), c = y % 100;
  const d = Math.floor(b / 4), e = b % 4;
  const f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3);
  const h = (19 * a + b - d - g + 15) % 30;
  const i = Math.floor(c / 4), k = c % 4;
  const l = (32 + 2 * e + 2 * i - h - k) % 7;
  const m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31);
  const day = ((h + l - 7 * m + 114) % 31) + 1;
  return new Date(y, month - 1, day);
}
function datePlusDays(base, n) {
  const d = new Date(base.getTime());
  d.setDate(d.getDate() + n);
  return d;
}
function sameDay(a, b) {
  return a.getFullYear() === b.getFullYear()
      && a.getMonth()    === b.getMonth()
      && a.getDate()     === b.getDate();
}
function fmtFull(date) {
  const wd = WEEKDAYS_FULL[(date.getDay() || 7) - 1];
  return `${wd} ${date.getDate()} ${GREG_MONTHS_FULL[date.getMonth()]} ${date.getFullYear()}`;
}
function fmtShort(date) {
  const wd = WEEKDAYS_FULL[(date.getDay() || 7) - 1].slice(0, 3);
  return `${wd} ${date.getDate()} ${GREG_MONTHS_SHORT[date.getMonth()]} ${date.getFullYear()}`;
}

// ── Full moon algorithm ──────────────────────────────────────────────────────
// Reference full moon: JD 2451551.259 (6 Jan 2000 18:14 UTC)
const FM_REF_JD    = 2451551.259;
const LUNAR_MONTH  = 29.530588853;
const JD_UNIX_EPOCH = 2440587.5; // JD of 1 Jan 1970 00:00 UTC

function jdToDate(jd) {
  return new Date((jd - JD_UNIX_EPOCH) * 86400000);
}
function dateToJD(d) {
  return d.getTime() / 86400000 + JD_UNIX_EPOCH;
}
function fullMoonsInRange(start, end) {
  const startJD = dateToJD(start);
  const endJD   = dateToJD(end);
  const n0 = Math.ceil((startJD - FM_REF_JD) / LUNAR_MONTH);
  const moons = [];
  for (let n = n0; ; n++) {
    const jd = FM_REF_JD + n * LUNAR_MONTH;
    if (jd > endJD) break;
    moons.push(jdToDate(jd));
  }
  return moons;
}

// ── Holiday lookup tables ────────────────────────────────────────────────────
// All months are 0-indexed (Jan=0 … Dec=11).

// Passover (15 Nisan). 2027+ estimated via 19-yr Metonic cycle; may be ±1 day.
const PASSOVER_GY = {
  2020:[3,8],  2021:[2,27], 2022:[3,15], 2023:[3,5],  2024:[3,22],
  2025:[3,12], 2026:[3,1],  2027:[3,20], 2028:[3,9],  2029:[2,29],
  2030:[3,19], 2031:[3,7],  2032:[2,26], 2033:[3,15], 2034:[3,4],
  2035:[3,23], 2036:[3,11], 2037:[2,31], 2038:[3,20], 2039:[3,9],
  2040:[2,27],
};

// Chinese New Year (1st day, 1st lunar month).
const CNY_GY = {
  2020:[0,25], 2021:[1,12], 2022:[1,1],  2023:[0,22], 2024:[1,10],
  2025:[0,29], 2026:[1,17], 2027:[1,6],  2028:[0,26], 2029:[1,13],
  2030:[1,3],  2031:[0,23], 2032:[1,11], 2033:[0,31], 2034:[1,19],
  2035:[1,8],  2036:[0,28], 2037:[1,15], 2038:[1,4],  2039:[0,24],
  2040:[1,12],
};
// Lantern Festival = CNY + 14 days (15th day of 1st month).

// Hanukkah — first day (evening candle lighting). 2026+ estimated.
const HANUKKAH_GY = {
  2020:[11,10], 2021:[10,28], 2022:[11,18], 2023:[11,7],
  2024:[11,25], 2025:[11,14], 2026:[11,4],  2027:[11,24],
  2028:[11,12], 2029:[11,1],  2030:[11,20], 2031:[11,8],
  2032:[10,27], 2033:[11,16], 2034:[11,6],  2035:[11,24],
  2036:[11,12], 2037:[11,2],  2038:[11,22], 2039:[11,10],
  2040:[10,28],
};

// Islamic dates per Gregorian year: [1_Ramadan, Eid_al_Fitr, Eid_al_Adha].
// Calculated; actual dates depend on regional moon sighting (±1–2 days).
const ISLAMIC_GY = {
  2020: { ram:[3,23], fitr:[4,24], adha:[6,31] },
  2021: { ram:[3,12], fitr:[4,13], adha:[6,20] },
  2022: { ram:[3,2],  fitr:[4,2],  adha:[6,9]  },
  2023: { ram:[2,22], fitr:[3,21], adha:[5,28] },
  2024: { ram:[2,10], fitr:[3,9],  adha:[5,16] },
  2025: { ram:[2,1],  fitr:[2,30], adha:[5,6]  },
  2026: { ram:[1,17], fitr:[2,18], adha:[4,27] },
  2027: { ram:[1,6],  fitr:[2,5],  adha:[4,16] },
  2028: { ram:[0,26], fitr:[1,24], adha:[4,4]  },
  2029: { ram:[0,14], fitr:[1,12], adha:[3,24] },
  2030: { ram:[0,3],  fitr:[1,1],  adha:[3,13] },
  2031: { ram:[11,23],fitr:[0,21], adha:[3,2]  }, // Dec 23 in prev greg year covered separately
  2032: { ram:[11,11],fitr:[0,11], adha:[2,19] },
  2033: { ram:[0,1],  fitr:[1,30], adha:[2,8]  },
  2034: { ram:[11,21],fitr:[0,19], adha:[1,28] },
  2035: { ram:[11,10],fitr:[0,9],  adha:[1,17] },
  2036: { ram:[10,29],fitr:[11,27],adha:[1,6]  },
  2037: { ram:[10,18],fitr:[11,16],adha:[0,26] },
  2038: { ram:[10,7], fitr:[11,5], adha:[0,15] },
  2039: { ram:[9,27], fitr:[10,25],adha:[0,4]  },
  2040: { ram:[9,15], fitr:[10,14],adha:[11,22] },
};

// Diwali (Amavasya of Kartik). 2026+ estimated.
const DIWALI_GY = {
  2020:[10,14], 2021:[10,4], 2022:[9,24], 2023:[10,12],
  2024:[10,1],  2025:[9,20], 2026:[10,8], 2027:[9,28],
  2028:[9,16],  2029:[10,4], 2030:[9,24], 2031:[9,14],
  2032:[10,1],  2033:[9,21], 2034:[9,10], 2035:[9,29],
  2036:[9,18],  2037:[10,6], 2038:[9,26], 2039:[9,16],
  2040:[10,3],
};

// ── Track span helpers ───────────────────────────────────────────────────────
/**
 * Returns 'none' | 'start' | 'mid' | 'end' | 'dot' for a day within [spanStart, spanEnd].
 */
function spanStatus(date, spanStart, spanEnd) {
  if (!spanStart || !spanEnd) return 'none';
  const t = date.getTime();
  const s = spanStart.getTime();
  const e = spanEnd.getTime();
  if (t < s || t > e) return 'none';
  const atS = sameDay(date, spanStart);
  const atE = sameDay(date, spanEnd);
  if (atS && atE) return 'dot';
  if (atS) return 'start';
  if (atE) return 'end';
  return 'mid';
}

/**
 * Returns tick label if date matches any named event, else null.
 * events: array of { date, label, cls? }
 */
function matchEvent(date, events) {
  for (const ev of events) {
    if (ev.date && sameDay(date, ev.date)) return ev;
  }
  return null;
}

// ── Cell HTML builder ────────────────────────────────────────────────────────
function trackDiv(status, colorCls, tick) {
  if (status === 'none') return `<div class="ft t-none"></div>`;
  const tickHtml = tick
    ? `<span class="ft-tick${tick.cls ? ' ' + tick.cls : ''}" title="${tick.label}"></span>`
    : '';
  return `<div class="ft t-${status} ${colorCls}">${tickHtml}</div>`;
}

function buildCell(gd, dayInMonth, href, yearData, fullMoonSet) {
  const { passover, easter, cny, lantern, hanukkahStart, islamicRam,
          islamicFitr, islamicAdha, diwali, jewishEnd, today } = yearData;

  // ── Full moon ──
  const isMoon = fullMoonSet.some(fm => sameDay(fm, gd));

  // ── Track 1: Chinese (CNY → Lantern) ──
  const chSt = spanStatus(gd, cny, lantern);
  const chEvents = [
    { date: cny,     label: 'Chinese New Year' },
    { date: lantern, label: 'Lantern Festival'  },
  ];
  const chTick = matchEvent(gd, chEvents);

  // ── Track 2: Jewish sequence (Purim → end of Sukkot) ──
  const purim    = passover ? datePlusDays(passover, -30) : null;
  const shavuot  = passover ? datePlusDays(passover,  50) : null;
  const rh       = passover ? datePlusDays(passover, 163) : null;
  const yk       = passover ? datePlusDays(passover, 172) : null;
  const sukkot   = passover ? datePlusDays(passover, 177) : null;
  const sukkotEnd= passover ? datePlusDays(passover, 183) : null; // 7 days of Sukkot
  const jwSt = spanStatus(gd, purim, sukkotEnd);
  const jwEvents = [
    { date: purim,   label: 'Purim'        },
    { date: passover,label: 'Passover'      },
    { date: shavuot, label: 'Shavuot'       },
    { date: rh,      label: 'Rosh Hashanah' },
    { date: yk,      label: 'Yom Kippur'    },
    { date: sukkot,  label: 'Sukkot'        },
  ];
  const jwTick = matchEvent(gd, jwEvents);

  // ── Track 2b: Hanukkah (shares same track; different part of year) ──
  const hanukkahEnd = hanukkahStart ? datePlusDays(hanukkahStart, 7) : null;
  const hkSt = spanStatus(gd, hanukkahStart, hanukkahEnd);
  // Determine which night (1–8); night 8 is diaspora-only
  let hkTick = null;
  if (hanukkahStart && hkSt !== 'none') {
    const nightNum = Math.round((gd.getTime() - hanukkahStart.getTime()) / 86400000) + 1;
    if (nightNum === 8) hkTick = { label: 'Hanukkah — 8th night (diaspora)', cls: 'tk-diaspora' };
    else if (nightNum === 1) hkTick = { label: 'Hanukkah begins' };
  }

  // Merge: if jwSt is active, use jewish color; else use hanukkah color
  const track2st   = jwSt !== 'none' ? jwSt : hkSt;
  const track2col  = jwSt !== 'none' ? 'c-jewish' : 'c-hanukk';
  const track2tick = jwSt !== 'none' ? jwTick : hkTick;

  // ── Track 3: Christian (Ash Wed → Pentecost) ──
  const ashWed    = datePlusDays(easter, -46);
  const palmSun   = datePlusDays(easter, -7);
  const ascension = datePlusDays(easter,  39);
  const pentecost = datePlusDays(easter,  49);
  const chriSt = spanStatus(gd, ashWed, pentecost);
  const chriEvents = [
    { date: ashWed,    label: 'Ash Wednesday'  },
    { date: palmSun,   label: 'Palm Sunday'     },
    { date: easter,    label: 'Easter'          },
    { date: ascension, label: 'Ascension Day'   },
    { date: pentecost, label: 'Pentecost'       },
  ];
  const chriTick = matchEvent(gd, chriEvents);

  // ── Track 4: Islamic (Ramadan → Eid al-Fitr) + Eid al-Adha dot + Diwali dot ──
  const islSt = spanStatus(gd, islamicRam, islamicFitr);
  const islEvents = [
    { date: islamicRam,  label: 'Ramadan begins' },
    { date: islamicFitr, label: 'Eid al-Fitr'    },
  ];
  const islTick = matchEvent(gd, islEvents);

  // Eid al-Adha and Diwali override islamic track only if Ramadan not active
  let track4st   = islSt;
  let track4col  = 'c-islamic';
  let track4tick = islTick;
  if (islSt === 'none') {
    if (islamicAdha && sameDay(gd, islamicAdha)) {
      track4st = 'dot'; track4col = 'c-islamic';
      track4tick = { label: 'Eid al-Adha' };
    } else if (diwali && sameDay(gd, diwali)) {
      track4st = 'dot'; track4col = 'c-diwali';
      track4tick = { label: 'Diwali' };
    }
  }

  // ── Today ──
  const isToday = today && sameDay(gd, today);

  // ── Assemble HTML ──
  const moonHtml = isMoon
    ? `<div class="fd-moon-row"><span class="fd-moon" title="Full moon"></span></div>`
    : `<div class="fd-moon-row"></div>`;

  const tracks =
    trackDiv(chSt,     'c-chinese',   chTick) +
    trackDiv(track2st, track2col,     track2tick) +
    trackDiv(chriSt,   'c-christian', chriTick) +
    trackDiv(track4st, track4col,     track4tick);

  const titleParts = [fmtShort(gd)];
  if (isMoon) titleParts.push('Full moon');
  if (chTick)     titleParts.push(chTick.label);
  if (track2tick) titleParts.push(track2tick.label);
  if (chriTick)   titleParts.push(chriTick.label);
  if (track4tick) titleParts.push(track4tick.label);

  const ddStr = String(dayInMonth).padStart(2, '0');
  return (
    `<div class="fd-moon-row">${isMoon ? '<span class="fd-moon" title="Full moon"></span>' : ''}</div>` +
    `<div class="fd-tracks">${tracks}</div>` +
    `<a href="${href}" title="${titleParts.join(' · ')}">${dayInMonth}</a>`
  );
}

// ── Main builder ─────────────────────────────────────────────────────────────
function buildFestivalsCalendar(gaianYear) {
  const isoYear  = gaianYear - 10000;
  const yearStart = isoWeek1Start(isoYear);
  const totalWeeks = isoWeeksInYear(isoYear);
  const totalDays  = totalWeeks * 7;
  const yearEnd    = datePlusDays(yearStart, totalDays - 1);
  const easter     = easterDate(isoYear);
  const hasHorus   = totalWeeks === 53;
  const basePath   = window.LANG_BASE || '';

  // Today (for current-year highlighting)
  const todayRaw = new Date();
  todayRaw.setHours(0, 0, 0, 0);
  const thu = new Date(todayRaw);
  thu.setDate(todayRaw.getDate() + (4 - (todayRaw.getDay() || 7)));
  const today = (thu.getFullYear() + 10000) === gaianYear ? todayRaw : null;

  // Pre-compute Gregorian date for each Gaian day
  const gregDates = [];
  for (let i = 0; i < totalDays; i++) gregDates.push(datePlusDays(yearStart, i));

  // Full moons
  const fullMoons = fullMoonsInRange(yearStart, yearEnd);

  // Helper to build a Date from a lookup entry [m, d] or null
  function gy(table, yr) {
    const e = table[yr];
    return e ? new Date(yr, e[0], e[1]) : null;
  }

  // We need to look up holidays that may fall in isoYear OR the adjacent years
  // (since the Gaian year can span parts of two Gregorian years).
  // Collect all relevant dates by checking isoYear-1, isoYear, isoYear+1
  // then filtering to those within yearStart…yearEnd.
  function findInRange(table, build) {
    for (const yr of [isoYear - 1, isoYear, isoYear + 1]) {
      const d = build(table, yr);
      if (d && d >= yearStart && d <= yearEnd) return d;
    }
    return null;
  }
  function findIslamicInRange(field) {
    for (const yr of [isoYear - 1, isoYear, isoYear + 1]) {
      const e = ISLAMIC_GY[yr];
      if (!e) continue;
      const d = new Date(yr, e[field][0], e[field][1]);
      if (d >= yearStart && d <= yearEnd) return d;
    }
    return null;
  }

  const passover     = findInRange(PASSOVER_GY,  (t,y) => gy(t, y));
  const cny          = findInRange(CNY_GY,        (t,y) => gy(t, y));
  const lantern      = cny ? datePlusDays(cny, 14) : null;
  const hanukkahStart= findInRange(HANUKKAH_GY,  (t,y) => gy(t, y));
  const diwali       = findInRange(DIWALI_GY,    (t,y) => gy(t, y));
  const islamicRam   = findIslamicInRange('ram');
  const islamicFitr  = findIslamicInRange('fitr');
  const islamicAdha  = findIslamicInRange('adha');

  const yearData = {
    passover, easter, cny, lantern, hanukkahStart,
    islamicRam, islamicFitr, islamicAdha, diwali, today,
  };

  // ── Update headings ──
  const heading = document.getElementById('year-heading');
  if (heading) heading.textContent = `${gaianYear} GE \u2014 Festivals`;

  const sub = document.getElementById('year-subheading');
  if (sub) sub.textContent = `${fmtFull(yearStart)} \u2013 ${fmtFull(yearEnd)}`;

  // ── Prose intro ──
  const intro = document.getElementById('year-intro');
  if (intro) {
    const yearPath   = `${basePath}/calendar/year/${gaianYear}/`;
    const prevPath   = `${basePath}/calendar/year/${gaianYear - 1}/festivals/`;
    const nextPath   = `${basePath}/calendar/year/${gaianYear + 1}/festivals/`;
    intro.innerHTML =
      `<p><a href="${yearPath}">\u2190 Back to ${gaianYear}\u00a0GE year view</a></p>` +
      `<p class="year-nav">` +
      `<a href="${prevPath}">\u2190 ${gaianYear - 1}\u00a0GE</a>` +
      `\u2002\u00b7\u2002` +
      `<a href="${nextPath}">${gaianYear + 1}\u00a0GE \u2192</a>` +
      `</p>`;
  }

  // ── Build table ──
  const container = document.getElementById('year-calendar');
  if (!container) return;

  const html = [];
  html.push('<div class="year-cal-wrap">');
  html.push('<table class="gaian-year-table">');

  // Header
  html.push('<thead><tr>');
  html.push('<th class="gyear-month-hdr"></th>');
  for (let dc = 0; dc < 28; dc++) {
    const wi = dc % 7;
    const cls = IS_SABBATH[wi] ? ' class="gyear-sab"' : '';
    const weekNum = wi + 1;
    html.push(
      `<th${cls}><a href="${basePath}/calendar/week/${weekNum}/">`
      + `${WD_PLANETS[wi]}<br>${WD_ABBR[wi]}</a></th>`
    );
  }
  html.push('</tr></thead>');

  // Body
  html.push('<tbody>');
  const numMonths = hasHorus ? 14 : 13;
  for (let mi = 0; mi < numMonths; mi++) {
    const m = GAIAN_MONTH_INFO[mi];
    const daysInMonth = mi === 13 ? 7 : 28;
    html.push('<tr>');
    html.push(`<th class="gyear-month-hdr">${m.symbol}\u00a0${m.name}</th>`);

    for (let dc = 0; dc < 28; dc++) {
      const dayInMonth = dc + 1;
      const wi = dc % 7;
      const isSab = IS_SABBATH[wi];

      if (dayInMonth > daysInMonth) {
        html.push(`<td class="gyear-empty${isSab ? ' gyear-sab' : ''}"></td>`);
      } else {
        const dayOfYear = mi < 13 ? mi * 28 + dayInMonth : 364 + dayInMonth;
        const gd = gregDates[dayOfYear - 1];
        const isToday = today && sameDay(gd, today);
        let tdCls = ['fd-cell'];
        if (isSab)   tdCls.push('gyear-sab');
        if (isToday) tdCls.push('gyear-today');

        const ddStr = String(dayInMonth).padStart(2, '0');
        const href  = `${basePath}/calendar/${m.id}/${ddStr}/`;

        const inner = buildCell(gd, dayInMonth, href, yearData, fullMoons);
        html.push(`<td class="${tdCls.join(' ')}">${inner}</td>`);
      }
    }
    html.push('</tr>');
  }
  html.push('</tbody></table></div>');
  container.innerHTML = html.join('');
}

// Run: use template-injected constant, or fall back to reading the year from the URL.
(function () {
  var yr = (typeof GAIAN_YEAR !== 'undefined') ? GAIAN_YEAR : (function () {
    var m = window.location.pathname.match(/\/calendar\/year\/(\d+)\//);
    return m ? parseInt(m[1], 10) : null;
  })();
  if (yr) buildFestivalsCalendar(yr);
})();
