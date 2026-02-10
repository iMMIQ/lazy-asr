/**
 * Tests for API service functions
 */
import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { fetchVADProviders } from './api';

// Create MSW test server - only for VAD tests
const server = setupServer(
  // VAD providers endpoint
  http.get('/api/v1/vad/providers', () => {
    return HttpResponse.json({
      providers: [
        {
          name: 'silero',
          display_name: 'Silero VAD',
          description: 'High-quality VAD using Silero model',
        },
        {
          name: 'ten',
          display_name: 'Ten VAD',
          description: 'VAD using Ten model',
        },
        {
          name: 'pyannote',
          display_name: 'Pyannote VAD',
          description: 'VAD using Pyannote model',
        },
      ],
      default: 'ten',
    });
  })
);

describe('API Service - VAD Providers', () => {
  beforeAll(() => {
    server.listen({ onUnhandledRequest: 'warn' });
  });

  afterEach(() => {
    server.resetHandlers();
  });

  afterAll(() => {
    server.close();
  });

  describe('fetchVADProviders', () => {
    it('should return VAD providers on success', async () => {
      const result = await fetchVADProviders();

      expect(result.providers).toHaveLength(3);
      expect(result.default).toBe('ten');
      expect(result.providers[0].name).toBe('silero');
      expect(result.providers[1].name).toBe('ten');
      expect(result.providers[2].name).toBe('pyannote');
    });

    it('should throw error on API failure', async () => {
      server.use(
        http.get('/api/v1/vad/providers', () => {
          return HttpResponse.json(
            { detail: 'Failed to fetch VAD providers' },
            { status: 500 }
          );
        })
      );

      await expect(fetchVADProviders()).rejects.toThrow('Failed to fetch VAD providers');
    });

    it('should handle empty providers list', async () => {
      server.use(
        http.get('/api/v1/vad/providers', () => {
          return HttpResponse.json({
            providers: [],
            default: 'silero',
          });
        })
      );

      const result = await fetchVADProviders();

      expect(result.providers).toHaveLength(0);
      expect(result.default).toBe('silero');
    });

    it('should throw error on network failure', async () => {
      server.use(
        http.get('/api/v1/vad/providers', () => {
          return HttpResponse.error();
        })
      );

      await expect(fetchVADProviders()).rejects.toThrow();
    });
  });
});
