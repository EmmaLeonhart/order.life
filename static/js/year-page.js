'use strict';
/**
 * year-page.js — Compact Gaian year calendar renderer
 * Layout: months as rows × 28 day columns, weekday header repeats ×4.
 * Requires: GAIAN_YEAR constant set by the page before this script runs.
 */

const GREG_MONTHS_FULL = ['January','February','March','April','May','June',
                           'July','August','September','October','November','December'];
const GREG_MONTHS_SHORT = ['Jan','Feb','Mar','Apr','May','Jun',
                            'Jul','Aug','Sep','Oct','Nov','Dec'];
const WEEKDAYS_FULL = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];

// Planetary symbols Mon–Sun
const WD_PLANETS = ['\u263D','\u2642','\u263F','\u2643','\u2640','\u2644','\u2609'];
const WD_ABBR    = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

// Passover (15 Nisan) Gregorian dates [month_0idx, day]; 2027+ estimated via 19-yr cycle
const PASSOVER_GY = {
  2020:[3,8],  2021:[2,27], 2022:[3,15], 2023:[3,5],  2024:[3,22],
  2025:[3,12], 2026:[3,1],  2027:[3,20], 2028:[3,9],  2029:[2,29],
  2030:[3,19], 2031:[3,7],  2032:[2,26], 2033:[3,15], 2034:[3,4],
  2035:[3,23], 2036:[3,11], 2037:[2,31], 2038:[3,20], 2039:[3,9],
  2040:[2,27],
};

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

// Sabbath days: Friday (idx 4), Saturday (idx 5), Sunday (idx 6)
const IS_SABBATH = [false, false, false, false, true, true, true];

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

// Anonymous Gregorian algorithm (Meeus/Jones/Butcher)
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
      && a.getMonth() === b.getMonth()
      && a.getDate() === b.getDate();
}

// "Monday 29 December 2025"
function fmtFull(date) {
  const wd = WEEKDAYS_FULL[(date.getDay() || 7) - 1];
  return `${wd} ${date.getDate()} ${GREG_MONTHS_FULL[date.getMonth()]} ${date.getFullYear()}`;
}

// "5 April 2026" — for Easter in prose
function fmtMedium(date) {
  return `${date.getDate()} ${GREG_MONTHS_FULL[date.getMonth()]} ${date.getFullYear()}`;
}

// "Mon 29 Dec 2025" — hover title on cells
function fmtShort(date) {
  const wd = WEEKDAYS_FULL[(date.getDay() || 7) - 1].slice(0, 3);
  return `${wd} ${date.getDate()} ${GREG_MONTHS_SHORT[date.getMonth()]} ${date.getFullYear()}`;
}

function buildYearCalendar(gaianYear) {
  const isoYear = gaianYear - 10000;
  const yearStart = isoWeek1Start(isoYear);
  const totalWeeks = isoWeeksInYear(isoYear);
  const totalDays = totalWeeks * 7;
  const yearEnd = datePlusDays(yearStart, totalDays - 1);
  const easter = easterDate(isoYear);
  const hasHorus = totalWeeks === 53;
  const basePath = (window.LANG_BASE) || '';

  // Today — only highlight when viewing the current Gaian year
  const todayRaw = new Date();
  todayRaw.setHours(0, 0, 0, 0);
  const thu = new Date(todayRaw);
  thu.setDate(todayRaw.getDate() + (4 - (todayRaw.getDay() || 7)));
  const isCurrentYear = (thu.getFullYear() + 10000) === gaianYear;
  const today = isCurrentYear ? todayRaw : null;

  // Passover
  const pd = PASSOVER_GY[isoYear];
  const passover = pd ? new Date(isoYear, pd[0], pd[1]) : null;

  // Pre-compute a Gregorian Date for each day of the Gaian year
  const gregDates = [];
  for (let i = 0; i < totalDays; i++) gregDates.push(datePlusDays(yearStart, i));

  // Find Easter's Gaian position
  let easterGaianStr = '';
  for (let i = 0; i < totalDays; i++) {
    if (sameDay(gregDates[i], easter)) {
      const dayNum = i + 1;
      const mi = dayNum > 364 ? 13 : Math.floor((dayNum - 1) / 28);
      const dim = dayNum > 364 ? dayNum - 364 : ((dayNum - 1) % 28) + 1;
      easterGaianStr = `${GAIAN_MONTH_INFO[mi].name}\u00a0${dim}`;
      break;
    }
  }

  // ── Update static heading ────────────────────────────────────────────────
  const heading = document.getElementById('year-heading');
  if (heading) heading.textContent = `${gaianYear} GE`;

  const sub = document.getElementById('year-subheading');
  if (sub) sub.textContent = `${fmtFull(yearStart)} \u2013 ${fmtFull(yearEnd)}`;

  // ── Prose intro ──────────────────────────────────────────────────────────
  const intro = document.getElementById('year-intro');
  if (intro) {
    const yearType = hasHorus
      ? 'a <strong>leap year</strong> (53\u00a0weeks, including the Horus intercalary period)'
      : 'a <strong>common year</strong> (52\u00a0weeks)';
    const easterLine = easterGaianStr
      ? `<p>Easter falls on <strong>${fmtMedium(easter)}</strong> (${easterGaianStr}).</p>`
      : '';
    const passoverLine = passover
      ? `<p>Passover begins on <strong>${fmtMedium(passover)}</strong>.</p>`
      : '';
    const prevPath = `${basePath}/calendar/year/${gaianYear - 1}/`;
    const nextPath = `${basePath}/calendar/year/${gaianYear + 1}/`;
    const festivalsPath = `${basePath}/calendar/year/${gaianYear}/festivals/`;

    intro.innerHTML =
      `<p><strong>${gaianYear}\u00a0GE</strong> is ${yearType}.</p>`
      + easterLine
      + passoverLine
      + `<p style="font-size:0.85rem"><a href="${festivalsPath}">Festivals \u0026 world calendars \u2192</a></p>`
      + `<p class="year-nav">`
      + `<a href="${prevPath}">\u2190 ${gaianYear - 1}\u00a0GE</a>`
      + `\u2002\u00b7\u2002`
      + `<a href="${nextPath}">${gaianYear + 1}\u00a0GE \u2192</a>`
      + `</p>`;
  }

  // ── Build compact grid table ─────────────────────────────────────────────
  const container = document.getElementById('year-calendar');
  if (!container) return;

  const html = [];
  html.push('<div class="year-cal-wrap">');
  html.push('<table class="gaian-year-table">');

  // Header: blank month cell + 28 weekday headers (4 × Mon–Sun), each a link
  html.push('<thead><tr>');
  html.push('<th class="gyear-month-hdr"></th>');
  for (let dc = 0; dc < 28; dc++) {
    const wi = dc % 7;
    const cls = IS_SABBATH[wi] ? ' class="gyear-sab"' : '';
    const weekNum = wi + 1; // Mon=1 … Sun=7
    html.push(
      `<th${cls}>`
      + `<a href="${basePath}/calendar/week/${weekNum}/">`
      + `${WD_PLANETS[wi]}<br>${WD_ABBR[wi]}`
      + `</a></th>`
    );
  }
  html.push('</tr></thead>');

  // Body: one row per month
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
        const isEaster   = sameDay(gd, easter);
        const isPassover = passover && sameDay(gd, passover);
        const isToday    = today && sameDay(gd, today);
        let cls = isSab ? 'gyear-sab' : '';
        if (isEaster)   cls = (cls ? cls + ' ' : '') + 'gyear-easter';
        if (isPassover) cls = (cls ? cls + ' ' : '') + 'gyear-passover';
        if (isToday)    cls = (cls ? cls + ' ' : '') + 'gyear-today';

        const ddStr = String(dayInMonth).padStart(2, '0');
        const href = `${basePath}/calendar/${m.id}/${ddStr}/`;
        html.push(
          `<td${cls ? ` class="${cls}"` : ''}>`
          + `<a href="${href}" title="${fmtShort(gd)}">${dayInMonth}</a>`
          + `</td>`
        );
      }
    }
    html.push('</tr>');
  }
  html.push('</tbody></table></div>');

  container.innerHTML = html.join('');
}

// Run: use template-injected constant, or fall back to reading the year from the URL
// (the URL fallback serves requests caught by the 404 handler for non-pregenerated years).
(function () {
  var yr = (typeof GAIAN_YEAR !== 'undefined') ? GAIAN_YEAR : (function () {
    var m = window.location.pathname.match(/\/calendar\/year\/(\d+)\//);
    return m ? parseInt(m[1], 10) : null;
  })();
  if (yr) buildYearCalendar(yr);
})();
