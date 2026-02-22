'use strict';
/**
 * year-page.js — Full Gaian year calendar renderer
 * Requires: GAIAN_YEAR constant set by the page before this script runs.
 */

const WEEKDAY_NAMES_YP = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
const WEEKDAY_SYMBOLS_YP = ['\u263D','\u2642','\u263F','\u2643','\u2640','\u2644','\u2609'];
const GREG_MONTHS_SHORT = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

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

/**
 * Returns a Date set to 00:00:00 local time of Monday of ISO week 1 of `y`.
 * ISO week 1 is the week containing January 4.
 */
function isoWeek1Start(y) {
  const jan4 = new Date(y, 0, 4);
  const dow = jan4.getDay() || 7; // 1=Mon … 7=Sun
  const mon = new Date(jan4);
  mon.setDate(jan4.getDate() - (dow - 1));
  mon.setHours(0, 0, 0, 0);
  return mon;
}

/**
 * Returns 52 or 53 — the number of ISO weeks in Gregorian year `y`.
 * Dec 28 is always in the last ISO week of its year.
 */
function isoWeeksInYear(y) {
  const dec28 = new Date(y, 11, 28);
  const dow = dec28.getDay() || 7;
  // Move to Thursday of that week (which is in the same ISO year)
  const thu = new Date(dec28);
  thu.setDate(dec28.getDate() + (4 - dow));
  const jan1 = new Date(thu.getFullYear(), 0, 1);
  return Math.ceil((((thu - jan1) / 86400000) + 1) / 7);
}

/**
 * Anonymous Gregorian algorithm (Meeus/Jones/Butcher).
 * Returns a Date for Easter Sunday of Gregorian year `y`.
 */
function easterDate(y) {
  const a = y % 19;
  const b = Math.floor(y / 100);
  const c = y % 100;
  const d = Math.floor(b / 4);
  const e = b % 4;
  const f = Math.floor((b + 8) / 25);
  const g = Math.floor((b - f + 1) / 3);
  const h = (19 * a + b - d - g + 15) % 30;
  const i = Math.floor(c / 4);
  const k = c % 4;
  const l = (32 + 2 * e + 2 * i - h - k) % 7;
  const m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31); // 1-based
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

function formatGregorian(date) {
  const wd = WEEKDAY_NAMES_YP[(date.getDay() || 7) - 1].slice(0, 3);
  const day = date.getDate();
  const mon = GREG_MONTHS_SHORT[date.getMonth()];
  const yr = date.getFullYear();
  return `${wd} ${day} ${mon} ${yr}`;
}

/** Map 1-based dayOfYear (1–371) to { month, dayInMonth }. */
function gaianMonthAndDay(dayOfYear) {
  if (dayOfYear > 364) {
    return { month: GAIAN_MONTH_INFO[13], dayInMonth: dayOfYear - 364 };
  }
  const m0 = Math.floor((dayOfYear - 1) / 28);
  const dayInMonth = ((dayOfYear - 1) % 28) + 1;
  return { month: GAIAN_MONTH_INFO[m0], dayInMonth };
}

function buildYearCalendar(gaianYear) {
  const isoYear = gaianYear - 10000;
  const yearStart = isoWeek1Start(isoYear);
  const totalWeeks = isoWeeksInYear(isoYear);
  const totalDays = totalWeeks * 7; // 364 (52w) or 371 (53w)
  const yearEnd = datePlusDays(yearStart, totalDays - 1);
  const easter = easterDate(isoYear);
  const basePath = (typeof window !== 'undefined' && window.LANG_BASE) || '';

  // Update static heading elements
  const heading = document.getElementById('year-heading');
  if (heading) heading.textContent = `${gaianYear} GE`;

  const sub = document.getElementById('year-subheading');
  if (sub) {
    sub.textContent = `${formatGregorian(yearStart)} \u2014 ${formatGregorian(yearEnd)}`;
  }

  const wikiLink = document.getElementById('wiki-link');
  if (wikiLink) {
    wikiLink.href = `https://wiki.order.life/wiki/${gaianYear}_GE`;
    wikiLink.textContent = `${gaianYear} GE \u2014 Wiki`;
  }

  const container = document.getElementById('year-calendar');
  if (!container) return;

  // Collect all days
  const days = [];
  for (let i = 0; i < totalDays; i++) {
    const dayNum = i + 1;
    const gregDate = datePlusDays(yearStart, i);
    const { month, dayInMonth } = gaianMonthAndDay(dayNum);
    // In the Gaian perpetual calendar, day 1 is always Monday (weekdayIdx 0).
    const weekdayIdx = (dayInMonth - 1) % 7; // 0=Mon … 6=Sun
    days.push({ dayNum, gregDate, month, dayInMonth, weekdayIdx, isEaster: sameDay(gregDate, easter) });
  }

  // Group by month
  const monthGroups = [];
  let current = null;
  for (const day of days) {
    if (!current || current.month.num !== day.month.num) {
      current = { month: day.month, days: [] };
      monthGroups.push(current);
    }
    current.days.push(day);
  }

  // Render
  const html = [];
  for (const group of monthGroups) {
    const m = group.month;
    html.push(`<section class="year-month year-month-${m.id}">`);
    html.push(`<h2>${m.symbol} ${m.name}</h2>`);
    html.push('<table class="year-table">');
    html.push('<thead><tr>');
    html.push('<th>Gaian Date</th><th>#</th><th>Gregorian</th><th>Weekday</th><th>Gaiad</th><th>Notes</th>');
    html.push('</tr></thead><tbody>');
    for (const day of group.days) {
      const gaianDate = `${m.name}\u00a0${String(day.dayInMonth).padStart(2, '0')}`;
      const gregStr = formatGregorian(day.gregDate);
      const sym = WEEKDAY_SYMBOLS_YP[day.weekdayIdx];
      const wdName = WEEKDAY_NAMES_YP[day.weekdayIdx];
      let gaiadCell = '';
      if (day.dayNum <= 364) {
        const ch = String(day.dayNum).padStart(3, '0');
        gaiadCell = `<a href="${basePath}/gaiad/${ch}/">${day.dayNum}</a>`;
      }
      const notes = day.isEaster ? '\uD83D\uDC23 Easter' : '';
      const rowClass = day.isEaster ? ' class="easter-row"' : '';
      html.push(`<tr${rowClass}>`);
      html.push(`<td>${gaianDate}</td><td>${day.dayNum}</td><td>${gregStr}</td><td>${sym}\u202f${wdName}</td><td>${gaiadCell}</td><td>${notes}</td>`);
      html.push('</tr>');
    }
    html.push('</tbody></table></section>');
  }

  container.innerHTML = html.join('');
}

// Run immediately — this script is at the bottom of <body>, DOM is ready.
if (typeof GAIAN_YEAR !== 'undefined') {
  buildYearCalendar(GAIAN_YEAR);
}
