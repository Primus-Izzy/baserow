/**
 * Optimized utility functions replacing full Lodash imports
 * Tree-shakable alternative to reduce bundle size
 */

// Import only specific functions instead of entire lodash library
import debounce from 'lodash.debounce'
import throttle from 'lodash.throttle'
import cloneDeep from 'lodash.clonedeep'
import merge from 'lodash.merge'
import get from 'lodash.get'
import set from 'lodash.set'
import has from 'lodash.has'
import omit from 'lodash.omit'
import pick from 'lodash.pick'
import groupBy from 'lodash.groupby'
import sortBy from 'lodash.sortby'
import orderBy from 'lodash.orderby'
import uniq from 'lodash.uniq'
import uniqBy from 'lodash.uniqby'
import flatten from 'lodash.flatten'
import chunk from 'lodash.chunk'
import isEmpty from 'lodash.isempty'
import isEqual from 'lodash.isequal'

/**
 * Native JavaScript alternatives to common Lodash functions
 * These provide better performance and smaller bundle size
 */
export const nativeUtils = {
  /**
   * Check if value is undefined or null
   */
  isNil(value) {
    return value == null
  },

  /**
   * Check if value is an object
   */
  isObject(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value)
  },

  /**
   * Check if value is an array
   */
  isArray(value) {
    return Array.isArray(value)
  },

  /**
   * Check if value is a string
   */
  isString(value) {
    return typeof value === 'string'
  },

  /**
   * Check if value is a number
   */
  isNumber(value) {
    return typeof value === 'number' && !isNaN(value)
  },

  /**
   * Check if value is a function
   */
  isFunction(value) {
    return typeof value === 'function'
  },

  /**
   * Find item in array by predicate
   */
  find(array, predicate) {
    return array.find(predicate)
  },

  /**
   * Filter array by predicate
   */
  filter(array, predicate) {
    return array.filter(predicate)
  },

  /**
   * Map array with function
   */
  map(array, fn) {
    return array.map(fn)
  },

  /**
   * Reduce array to single value
   */
  reduce(array, fn, initial) {
    return array.reduce(fn, initial)
  },

  /**
   * Get first element of array
   */
  first(array) {
    return array[0]
  },

  /**
   * Get last element of array
   */
  last(array) {
    return array[array.length - 1]
  },

  /**
   * Get unique values from array
   */
  unique(array) {
    return [...new Set(array)]
  },

  /**
   * Flatten array by one level
   */
  flattenOnce(array) {
    return array.flat()
  },

  /**
   * Deep flatten array
   */
  flattenDeep(array) {
    return array.flat(Infinity)
  },

  /**
   * Create object from array of key-value pairs
   */
  fromPairs(pairs) {
    return Object.fromEntries(pairs)
  },

  /**
   * Get object keys
   */
  keys(obj) {
    return Object.keys(obj)
  },

  /**
   * Get object values
   */
  values(obj) {
    return Object.values(obj)
  },

  /**
   * Get object entries
   */
  entries(obj) {
    return Object.entries(obj)
  },

  /**
   * Capitalize first letter of string
   */
  capitalize(str) {
    if (!str) return ''
    return str.charAt(0).toUpperCase() + str.slice(1)
  },

  /**
   * Convert string to camelCase
   */
  camelCase(str) {
    return str.replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) => {
      return index === 0 ? word.toLowerCase() : word.toUpperCase()
    }).replace(/\s+/g, '')
  },

  /**
   * Convert string to kebab-case
   */
  kebabCase(str) {
    return str
      .match(/[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g)
      ?.join('-')
      .toLowerCase()
  },

  /**
   * Convert string to snake_case
   */
  snakeCase(str) {
    return str
      .match(/[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g)
      ?.join('_')
      .toLowerCase()
  },

  /**
   * Trim whitespace from string
   */
  trim(str) {
    return str?.trim() || ''
  },

  /**
   * Generate random number between min and max
   */
  random(min = 0, max = 1) {
    return Math.random() * (max - min) + min
  },

  /**
   * Generate random integer between min and max
   */
  randomInt(min = 0, max = 100) {
    return Math.floor(Math.random() * (max - min + 1)) + min
  },

  /**
   * Clamp number between min and max
   */
  clamp(number, min, max) {
    return Math.min(Math.max(number, min), max)
  }
}

/**
 * Export optimized Lodash functions for specific use cases
 */
export const optimizedLodash = {
  // Performance-critical functions that benefit from Lodash implementation
  debounce,
  throttle,
  cloneDeep,
  merge,
  get,
  set,
  has,
  omit,
  pick,
  groupBy,
  sortBy,
  orderBy,
  uniq,
  uniqBy,
  flatten,
  chunk,
  isEmpty,
  isEqual,

  // Native alternatives for simpler operations
  ...nativeUtils
}

/**
 * Utility function to migrate from full Lodash import
 * Usage: import { _ } from './lodashUtils'
 */
export const _ = optimizedLodash

export default optimizedLodash