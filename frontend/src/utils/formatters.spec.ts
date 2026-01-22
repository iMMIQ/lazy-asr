// src/utils/formatters.spec.ts
import { describe, it, expect } from 'vitest';
import {
  formatFileSize,
  formatDuration,
  formatPercentage,
  formatTimestamp,
  truncateText,
  formatNumber
} from './formatters';

describe('formatFileSize', () => {
  it('should format zero bytes', () => {
    expect(formatFileSize(0)).toBe('0 Bytes');
  });

  it('should format bytes', () => {
    expect(formatFileSize(500)).toBe('500 Bytes');
    expect(formatFileSize(1023)).toBe('1023 Bytes');
  });

  it('should format kilobytes', () => {
    expect(formatFileSize(1024)).toBe('1 KB');
    expect(formatFileSize(1536)).toBe('1.5 KB');
    expect(formatFileSize(5120)).toBe('5 KB');
  });

  it('should format megabytes', () => {
    expect(formatFileSize(1024 * 1024)).toBe('1 MB');
    expect(formatFileSize(2.5 * 1024 * 1024)).toBe('2.5 MB');
  });

  it('should format gigabytes', () => {
    expect(formatFileSize(1024 * 1024 * 1024)).toBe('1 GB');
  });

  it('should format terabytes', () => {
    expect(formatFileSize(1024 * 1024 * 1024 * 1024)).toBe('1 TB');
  });

  it('should handle decimal values correctly', () => {
    const result = formatFileSize(1536);
    expect(result).toBe('1.5 KB');
  });
});

describe('formatDuration', () => {
  it('should format zero or invalid duration', () => {
    expect(formatDuration(0)).toBe('0s');
    expect(formatDuration(-1)).toBe('0s');
    expect(formatDuration(null as unknown as number)).toBe('0s');
  });

  it('should format seconds only', () => {
    expect(formatDuration(5)).toBe('5s');
    expect(formatDuration(59)).toBe('59s');
  });

  it('should format minutes and seconds', () => {
    expect(formatDuration(60)).toBe('1m 0s');
    expect(formatDuration(65)).toBe('1m 5s');
    expect(formatDuration(3599)).toBe('59m 59s');
  });

  it('should format hours, minutes, and seconds', () => {
    expect(formatDuration(3600)).toBe('1h 0m 0s');
    expect(formatDuration(3661)).toBe('1h 1m 1s');
    expect(formatDuration(7325)).toBe('2h 2m 5s');
  });
});

describe('formatPercentage', () => {
  it('should return 0% when total is 0', () => {
    expect(formatPercentage(0, 0)).toBe('0%');
    expect(formatPercentage(50, 0)).toBe('0%');
  });

  it('should calculate percentage correctly', () => {
    expect(formatPercentage(1, 4)).toBe('25.0%');
    expect(formatPercentage(1, 2)).toBe('50.0%');
    expect(formatPercentage(3, 4)).toBe('75.0%');
    expect(formatPercentage(1, 1)).toBe('100.0%');
  });

  it('should handle decimal results', () => {
    expect(formatPercentage(1, 3)).toBe('33.3%');
    expect(formatPercentage(2, 3)).toBe('66.7%');
  });
});

describe('formatTimestamp', () => {
  it('should format Date object', () => {
    const date = new Date('2024-01-15T10:30:00');
    const result = formatTimestamp(date);
    expect(result).toContain('2024');
  });

  it('should format timestamp string', () => {
    const result = formatTimestamp('2024-01-15T10:30:00');
    expect(result).toContain('2024');
  });

  it('should use default locale (zh-CN)', () => {
    const date = new Date('2024-01-15T10:30:00');
    const result = formatTimestamp(date);
    expect(typeof result).toBe('string');
  });

  it('should use custom locale', () => {
    const date = new Date('2024-01-15T10:30:00');
    const result = formatTimestamp(date, 'en-US');
    expect(typeof result).toBe('string');
  });
});

describe('truncateText', () => {
  it('should return empty string for null/undefined', () => {
    expect(truncateText(null as unknown as string)).toBe('');
    expect(truncateText(undefined as unknown as string)).toBe('');
  });

  it('should return text shorter than max length', () => {
    expect(truncateText('Hello', 10)).toBe('Hello');
  });

  it('should return text equal to max length', () => {
    expect(truncateText('Hello', 5)).toBe('Hello');
  });

  it('should truncate text longer than max length', () => {
    expect(truncateText('Hello World', 5)).toBe('Hello...');
  });

  it('should use default max length of 50', () => {
    const shortText = 'a'.repeat(30);
    expect(truncateText(shortText)).toBe(shortText);

    const longText = 'a'.repeat(100);
    expect(truncateText(longText).length).toBe(53); // 50 + '...'
  });
});

describe('formatNumber', () => {
  it('should format small numbers', () => {
    expect(formatNumber(5)).toBe('5');
    expect(formatNumber(123)).toBe('123');
  });

  it('should add thousands separator', () => {
    expect(formatNumber(1000)).toBe('1,000');
    expect(formatNumber(10000)).toBe('10,000');
    expect(formatNumber(100000)).toBe('100,000');
    expect(formatNumber(1000000)).toBe('1,000,000');
  });

  it('should format large numbers', () => {
    expect(formatNumber(1234567)).toBe('1,234,567');
    expect(formatNumber(1234567890)).toBe('1,234,567,890');
  });
});
