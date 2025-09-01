/**
 * Date utility functions replacing moment.js with date-fns
 * Provides better performance and smaller bundle size
 */

import {
  format,
  parse,
  parseISO,
  isValid,
  addDays,
  addWeeks,
  addMonths,
  addYears,
  subDays,
  subWeeks,
  subMonths,
  subYears,
  startOfDay,
  endOfDay,
  startOfWeek,
  endOfWeek,
  startOfMonth,
  endOfMonth,
  startOfYear,
  endOfYear,
  differenceInDays,
  differenceInWeeks,
  differenceInMonths,
  differenceInYears,
  isBefore,
  isAfter,
  isSameDay,
  isSameWeek,
  isSameMonth,
  isSameYear,
  formatDistanceToNow,
  formatRelative,
  getUnixTime,
  fromUnixTime
} from 'date-fns'

import {
  zonedTimeToUtc,
  utcToZonedTime,
  format as formatTz
} from 'date-fns-tz'

/**
 * Enhanced date utility class with timezone support
 */
class DateUtil {
  constructor(timezone = 'UTC') {
    this.timezone = timezone
  }

  /**
   * Format date with timezone support
   */
  format(date, formatString = 'yyyy-MM-dd HH:mm:ss', timezone = this.timezone) {
    if (!this.isValid(date)) return ''
    
    const zonedDate = utcToZonedTime(date, timezone)
    return formatTz(zonedDate, formatString, { timeZone: timezone })
  }

  /**
   * Parse date string
   */
  parse(dateString, formatString = 'yyyy-MM-dd HH:mm:ss', referenceDate = new Date()) {
    if (typeof dateString === 'string' && dateString.includes('T')) {
      return parseISO(dateString)
    }
    return parse(dateString, formatString, referenceDate)
  }

  /**
   * Check if date is valid
   */
  isValid(date) {
    return isValid(new Date(date))
  }

  /**
   * Get current date in timezone
   */
  now(timezone = this.timezone) {
    const utcDate = new Date()
    return utcToZonedTime(utcDate, timezone)
  }

  /**
   * Convert to UTC
   */
  toUTC(date, timezone = this.timezone) {
    return zonedTimeToUtc(date, timezone)
  }

  /**
   * Convert from UTC to timezone
   */
  fromUTC(date, timezone = this.timezone) {
    return utcToZonedTime(date, timezone)
  }

  /**
   * Add time periods
   */
  add(date, amount, unit) {
    switch (unit) {
      case 'days':
      case 'day':
        return addDays(date, amount)
      case 'weeks':
      case 'week':
        return addWeeks(date, amount)
      case 'months':
      case 'month':
        return addMonths(date, amount)
      case 'years':
      case 'year':
        return addYears(date, amount)
      default:
        return date
    }
  }

  /**
   * Subtract time periods
   */
  subtract(date, amount, unit) {
    switch (unit) {
      case 'days':
      case 'day':
        return subDays(date, amount)
      case 'weeks':
      case 'week':
        return subWeeks(date, amount)
      case 'months':
      case 'month':
        return subMonths(date, amount)
      case 'years':
      case 'year':
        return subYears(date, amount)
      default:
        return date
    }
  }

  /**
   * Get start of period
   */
  startOf(date, unit) {
    switch (unit) {
      case 'day':
        return startOfDay(date)
      case 'week':
        return startOfWeek(date)
      case 'month':
        return startOfMonth(date)
      case 'year':
        return startOfYear(date)
      default:
        return date
    }
  }

  /**
   * Get end of period
   */
  endOf(date, unit) {
    switch (unit) {
      case 'day':
        return endOfDay(date)
      case 'week':
        return endOfWeek(date)
      case 'month':
        return endOfMonth(date)
      case 'year':
        return endOfYear(date)
      default:
        return date
    }
  }

  /**
   * Calculate differences
   */
  diff(date1, date2, unit = 'days') {
    switch (unit) {
      case 'days':
      case 'day':
        return differenceInDays(date1, date2)
      case 'weeks':
      case 'week':
        return differenceInWeeks(date1, date2)
      case 'months':
      case 'month':
        return differenceInMonths(date1, date2)
      case 'years':
      case 'year':
        return differenceInYears(date1, date2)
      default:
        return 0
    }
  }

  /**
   * Comparison methods
   */
  isBefore(date1, date2) {
    return isBefore(date1, date2)
  }

  isAfter(date1, date2) {
    return isAfter(date1, date2)
  }

  isSame(date1, date2, unit = 'day') {
    switch (unit) {
      case 'day':
        return isSameDay(date1, date2)
      case 'week':
        return isSameWeek(date1, date2)
      case 'month':
        return isSameMonth(date1, date2)
      case 'year':
        return isSameYear(date1, date2)
      default:
        return false
    }
  }

  /**
   * Human-readable formats
   */
  fromNow(date) {
    return formatDistanceToNow(date, { addSuffix: true })
  }

  relative(date, baseDate = new Date()) {
    return formatRelative(date, baseDate)
  }

  /**
   * Unix timestamp methods
   */
  unix(date = new Date()) {
    return getUnixTime(date)
  }

  fromUnix(timestamp) {
    return fromUnixTime(timestamp)
  }

  /**
   * Common date formats
   */
  toISO(date) {
    return date.toISOString()
  }

  toDateString(date) {
    return this.format(date, 'yyyy-MM-dd')
  }

  toTimeString(date) {
    return this.format(date, 'HH:mm:ss')
  }

  toDateTime(date) {
    return this.format(date, 'yyyy-MM-dd HH:mm:ss')
  }

  /**
   * Localization support
   */
  setLocale(locale) {
    // For future implementation with date-fns locales
    this.locale = locale
  }

  /**
   * Create a new DateUtil instance with different timezone
   */
  tz(timezone) {
    return new DateUtil(timezone)
  }
}

// Create default instance
const dateUtil = new DateUtil()

// Export both class and instance
export { DateUtil }
export default dateUtil

// Export commonly used functions for direct import
export {
  format,
  parse,
  parseISO,
  isValid,
  addDays,
  addWeeks,
  addMonths,
  addYears,
  subDays,
  subWeeks,
  subMonths,
  subYears,
  startOfDay,
  endOfDay,
  startOfWeek,
  endOfWeek,
  startOfMonth,
  endOfMonth,
  startOfYear,
  endOfYear,
  differenceInDays,
  differenceInWeeks,
  differenceInMonths,
  differenceInYears,
  isBefore,
  isAfter,
  isSameDay,
  isSameWeek,
  isSameMonth,
  isSameYear,
  formatDistanceToNow,
  formatRelative,
  getUnixTime,
  fromUnixTime,
  zonedTimeToUtc,
  utcToZonedTime
}