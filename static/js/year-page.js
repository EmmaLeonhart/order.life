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

// Sabbath days: Friday (idx 4), Saturday (idx 5), Sunday (idx 6) in 0-based Mon-Sun
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

// "Mon 29 Dec 2025" — used for cell title attributes
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

  // Pre-compute a Gregorian Date for each day of the Gaian year
  const gregDates = [];
  for (let i = 0; i < totalDays; i++) gregDates.push(datePlusDays(yearStart, i));

  // Find Easter's Gaian position (Easter is always on Gregorian Sunday = Gaian Sunday)
  let easterGaianName = '';
  for (let i = 0; i < totalDays; i++) {
    if (sameDay(gregDates[i], easter)) {
      const dayNum = i + 1;
      const mi = dayNum > 364 ? 13 : Math.floor((dayNum - 1) / 28);
      const dim = dayNum > 364 ? dayNum - 364 : ((dayNum - 1) % 28) + 1;
      easterGaianName = `${GAIAN_MONTH_INFO[mi].name}\u00a0${dim}`;
      break;
    }
  }

  // ── Update headings ──────────────────────────────────────────────────────
  const heading = document.getElementById('year-heading');
  if (heading) heading.textContent = `${gaianYear} GE`;

  const sub = document.getElementById('year-subheading');
  if (sub) {
    const horusNote = hasHorus ? '53-week year \u2014 Horus included'
                               : '52-week year \u2014 no Horus';
    const easterNote = easterGaianName
      ? `\u00a0\u00b7 Easter: ${fmtShort(easter)} (${easterGaianName})`
      : '';
    sub.textContent =
      `${fmtFull(yearStart)} \u2013 ${fmtFull(yearEnd)} \u00b7 ${horusNote}${easterNote}`;
  }

  const wikiLink = document.getElementById('wiki-link');
  if (wikiLink) {
    wikiLink.href = `https://wiki.order.life/wiki/${gaianYear}_GE`;
    wikiLink.textContent = `${gaianYear}\u00a0GE \u2014 Wiki`;
  }

  // ── Build compact grid table ─────────────────────────────────────────────
  const container = document.getElementById('year-calendar');
  if (!container) return;

  const WD_ABBR = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

  const html = [];
  html.push('<div class="year-cal-wrap">');
  html.push('<table class="gaian-year-table">');

  // Header: blank month cell + 28 weekday headers (4 × Mon-Sun)
  html.push('<thead><tr>');
  html.push('<th class="gyear-month-hdr"></th>');
  for (let dc = 0; dc < 28; dc++) {
    const wi = dc % 7;
    html.push(`<th class="${IS_SABBATH[wi] ? 'gyear-sab' : ''}">${WD_ABBR[wi]}</th>`);
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
      const wi = dc % 7;  // 0=Mon … 6=Sun
      const isSab = IS_SABBATH[wi];

      if (dayInMonth > daysInMonth) {
        // Unused cell (only applies to Horus row, days 8–28)
        html.push(`<td class="gyear-empty${isSab ? ' gyear-sab' : ''}"></td>`);
      } else {
        const dayOfYear = mi < 13 ? mi * 28 + dayInMonth : 364 + dayInMonth;
        const gd = gregDates[dayOfYear - 1];
        const isEaster = sameDay(gd, easter);

        let cls = isSab ? 'gyear-sab' : '';
        if (isEaster) cls = cls ? cls + ' gyear-easter' : 'gyear-easter';

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

if (typeof GAIAN_YEAR !== 'undefined') {
  buildYearCalendar(GAIAN_YEAR);
}
