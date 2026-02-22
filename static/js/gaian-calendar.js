/**
 * Gaian Calendar Logic
 * 13 months x 28 days + Horus intercalary (week 53)
 * Year = ISO week-year + 10,000
 */

const GAIAN_MONTHS = [
  { num: 1,  id: 'sagittarius', symbol: '\u2650', name_en: 'Sagittarius' },
  { num: 2,  id: 'capricorn',   symbol: '\u2651', name_en: 'Capricorn' },
  { num: 3,  id: 'aquarius',    symbol: '\u2652', name_en: 'Aquarius' },
  { num: 4,  id: 'pisces',      symbol: '\u2653', name_en: 'Pisces' },
  { num: 5,  id: 'aries',       symbol: '\u2648', name_en: 'Aries' },
  { num: 6,  id: 'taurus',      symbol: '\u2649', name_en: 'Taurus' },
  { num: 7,  id: 'gemini',      symbol: '\u264A', name_en: 'Gemini' },
  { num: 8,  id: 'cancer',      symbol: '\u264B', name_en: 'Cancer' },
  { num: 9,  id: 'leo',         symbol: '\u264C', name_en: 'Leo' },
  { num: 10, id: 'virgo',       symbol: '\u264D', name_en: 'Virgo' },
  { num: 11, id: 'libra',       symbol: '\u264E', name_en: 'Libra' },
  { num: 12, id: 'scorpius',    symbol: '\u264F', name_en: 'Scorpius' },
  { num: 13, id: 'ophiuchus',   symbol: '\u26CE', name_en: 'Ophiuchus' },
  { num: 14, id: 'horus',       symbol: '𓅃', name_en: 'Horus' },
];

function getISODayOfWeek(date) {
  const d = date.getDay();
  return d === 0 ? 7 : d;
}

function getISOWeekInfo(date) {
  const d = new Date(date.getTime());
  d.setHours(0, 0, 0, 0);
  d.setDate(d.getDate() + 4 - (d.getDay() || 7));
  const yearStart = new Date(d.getFullYear(), 0, 1);
  const weekOfYear = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
  return { weekYear: d.getFullYear(), weekOfYear };
}

function gregorianToGaian(date) {
  const { weekYear, weekOfYear } = getISOWeekInfo(date);
  const dayOfWeek = getISODayOfWeek(date);
  const monthIndex0 = Math.floor((weekOfYear - 1) / 4);
  const weekInMonth0 = (weekOfYear - 1) % 4;
  const month = monthIndex0 + 1;
  const dayOfMonth = weekInMonth0 * 7 + dayOfWeek;
  return {
    year: weekYear + 10000,
    month,
    day: dayOfMonth,
    monthData: GAIAN_MONTHS[month - 1],
  };
}

function dayOfYear(monthNum, dayInMonth) {
  if (monthNum <= 13) return (monthNum - 1) * 28 + dayInMonth;
  return 364 + dayInMonth; // Horus
}

/**
 * Update all elements with class 'gaian-date-live' to show today's Gaian date.
 * Expects data attributes for localized month names on the element.
 */
function updateLiveGaianDate() {
  const now = new Date();
  const today = gregorianToGaian(now);
  const els = document.querySelectorAll('.gaian-date-live');
  els.forEach(el => {
    // If server already rendered a localized, linked date, don't override it.
    if (el.dataset.server === '1') return;

    const lang = el.dataset.lang || 'en';
    const monthNames = window.GAIAN_MONTH_NAMES || {};
    const monthName = monthNames[today.monthData.id] || today.monthData.name_en;
    const geAbbrev = el.dataset.geAbbrev || 'GE';
    const basePath = el.dataset.basePath != null ? el.dataset.basePath : (window.LANG_BASE != null ? window.LANG_BASE : ('/' + lang));

    // Weekday info (ISO: Mon=1..Sun=7)
    const weekdayNum = getISODayOfWeek(now);
    const weekdaySymbols = ['☽','♂','☿','♃','♀','♄','☉'];
    const weekdaySymbol = weekdaySymbols[weekdayNum - 1] || '';
    const weekdayName = (window.GAIAN_WEEKDAY_NAMES && window.GAIAN_WEEKDAY_NAMES[weekdayNum - 1]) || null;
    const weekdayText = weekdayName || ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][weekdayNum - 1];

    // Build clickable date display
    const weekdayLink = `<a href="${basePath}/week/${weekdayNum}/">${weekdayText}</a>`;
    const monthNum = String(today.monthData.num).padStart(2, '0');
    const monthLink = `<a href="${basePath}/calendar/${monthNum}/">${monthName}</a>`;
    const dayLink = `<a href="${basePath}/calendar/${monthNum}/${String(today.day).padStart(2,'0')}/">${today.day}</a>`;
    const yearLink = `<a href="${basePath}/calendar/year/${today.year}/">${today.year}</a>`;
    const geLink = `<a href="${basePath}/calendar/gaian-era">${geAbbrev}</a>`;

    el.innerHTML = `${weekdaySymbol}${today.monthData.symbol} ${weekdayLink}, ${monthLink} ${dayLink}, ${yearLink} ${geLink}`;
  });
}

document.addEventListener('DOMContentLoaded', updateLiveGaianDate);
