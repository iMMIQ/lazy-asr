// src/services/api.spec.ts
import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import {
  fetchPlugins,
  processSingleFile,
  processMultipleFiles,
  getDownloadUrl,
  getBundleDownloadUrl,
  startScan,
  getScanStatus,
  getScanResult,
  getAllScans,
  cancelScan,
  getScanConfig,
  browseDirectory,
  getPathInfo,
  createMonitor,
  getAllMonitors,
  getMonitor,
  updateMonitor,
  deleteMonitor,
  toggleMonitor,
  getMonitorServiceStatus,
  startMonitorService,
  stopMonitorService,
  getDatabaseStatus
} from './api'
import type { ScanRequest, MonitorConfig } from '../types'

const mockServer = setupServer(
  // Plugin endpoints - note: axios uses baseURL of '/api/v1' so paths are relative to that
  http.get('/api/v1/asr/plugins', () => {
    return HttpResponse.json({
      plugins: [
        { name: 'faster-whisper', display_name: 'Faster Whisper', requires_api_key: true }
      ]
    })
  }),

  // Process endpoints
  http.post('/api/v1/asr/process', () => {
    return HttpResponse.json([])
  }),

  http.post('/api/v1/asr/process-multiple', () => {
    return HttpResponse.json([])
  }),

  // Scan endpoints
  http.post('/api/v1/asr/scan/start', () => {
    return HttpResponse.json({ scan_id: 'test-scan-id' })
  }),

  http.get('/api/v1/asr/scan/status/:scanId', () => {
    return HttpResponse.json({ scan_id: 'test-scan-id', status: 'completed' as const })
  }),

  http.get('/api/v1/asr/scan/result/:scanId', () => {
    return HttpResponse.json({ scan_id: 'test-scan-id', results: [] })
  }),

  http.get('/api/v1/asr/scan/all', () => {
    return HttpResponse.json({ scans: [] })
  }),

  http.post('/api/v1/asr/scan/cancel/:scanId', () => {
    return HttpResponse.json({ success: true })
  }),

  http.get('/api/v1/asr/scan/config', () => {
    return HttpResponse.json({ max_files: 100 })
  }),

  http.get('/api/v1/asr/scan/browse', () => {
    return HttpResponse.json({ subdirectories: [], media_files: [] })
  }),

  http.get('/api/v1/asr/scan/path-info', () => {
    return HttpResponse.json({ path: '/', exists: true, is_directory: true, is_readable: true })
  }),

  // Monitor endpoints
  http.post('/api/v1/asr/monitor/create', () => {
    return HttpResponse.json({ monitor_id: 'test-monitor-id' })
  }),

  http.get('/api/v1/asr/monitor/all', () => {
    return HttpResponse.json({ monitors: [], total_count: 0, active_count: 0 })
  }),

  // IMPORTANT: More specific paths must come before parameterized paths
  http.get('/api/v1/asr/monitor/status', () => {
    return HttpResponse.json({ is_running: true, active_monitors: 0, total_monitors: 0 })
  }),

  http.post('/api/v1/asr/monitor/service/start', () => {
    return HttpResponse.json({ success: true })
  }),

  http.post('/api/v1/asr/monitor/service/stop', () => {
    return HttpResponse.json({ success: true })
  }),

  http.get('/api/v1/asr/monitor/:monitorId', () => {
    return HttpResponse.json({ monitor_id: 'test-monitor-id', name: 'Test Monitor' })
  }),

  http.put('/api/v1/asr/monitor/:monitorId', () => {
    return HttpResponse.json({ success: true })
  }),

  http.delete('/api/v1/asr/monitor/:monitorId', () => {
    return HttpResponse.json({ success: true })
  }),

  http.post('/api/v1/asr/monitor/:monitorId/toggle', () => {
    return HttpResponse.json({ success: true })
  }),

  // Database endpoint
  http.get('/api/v1/asr/database/status', () => {
    return HttpResponse.json({ is_connected: true, database_type: 'sqlite', last_checked: new Date().toISOString() })
  })
)

describe('API Service', () => {
  beforeAll(() => {
    mockServer.listen({ onUnhandledRequest: 'warn' })
  })

  afterEach(() => {
    mockServer.resetHandlers()
  })

  afterAll(() => {
    mockServer.close()
  })

  describe('fetchPlugins', () => {
    it('should fetch available ASR plugins', async () => {
      const result = await fetchPlugins()
      expect(result).toBeDefined()
      expect(result.plugins).toBeInstanceOf(Array)
    })
  })

  describe('processSingleFile', () => {
    it.skip('should process a single file', async () => {
      // FormData tests require special handling in test environment
      // TODO: Set up proper FormData mocking
      const formData = new FormData()
      formData.append('file', new File(['content'], 'test.mp3'))
      const result = await processSingleFile(formData)
      expect(result).toEqual([])
    })
  })

  describe('processMultipleFiles', () => {
    it.skip('should process multiple files', async () => {
      // FormData tests require special handling in test environment
      // TODO: Set up proper FormData mocking
      const formData = new FormData()
      formData.append('files', new File(['content'], 'test.mp3'))
      const result = await processMultipleFiles(formData)
      expect(result).toEqual([])
    })
  })

  describe('getDownloadUrl', () => {
    it('should generate download URL for file path', () => {
      const url = getDownloadUrl('/path/to/file.srt')
      expect(url).toContain('/api/v1/asr/download/')
      expect(url).toContain(encodeURIComponent('/path/to/file.srt'))
    })
  })

  describe('getBundleDownloadUrl', () => {
    it('should generate bundle download URL', () => {
      const url = getBundleDownloadUrl('task-123')
      expect(url).toContain('/api/v1/asr/download-bundle/task-123')
    })
  })

  describe('Scan APIs', () => {
    it('should start a scan', async () => {
      const scanRequest: ScanRequest = { path: '/test', max_files: 10 }
      const result = await startScan(scanRequest)
      expect(result.scan_id).toBe('test-scan-id')
    })

    it('should get scan status', async () => {
      const result = await getScanStatus('scan-123')
      expect(result.scan_id).toBe('test-scan-id')
    })

    it('should get scan result', async () => {
      const result = await getScanResult('scan-123')
      expect(result).toBeDefined()
    })

    it('should get all scans', async () => {
      const result = await getAllScans()
      expect(result.scans).toBeInstanceOf(Array)
    })

    it('should cancel a scan', async () => {
      const result = await cancelScan('scan-123')
      expect(result.success).toBe(true)
    })

    it('should get scan config', async () => {
      const result = await getScanConfig()
      expect(result).toBeDefined()
    })

    it('should browse directory', async () => {
      const result = await browseDirectory('/test')
      expect(result.subdirectories).toBeInstanceOf(Array)
      expect(result.media_files).toBeInstanceOf(Array)
    })

    it('should get path info', async () => {
      const result = await getPathInfo('/test')
      expect(result.exists).toBe(true)
    })
  })

  describe('Monitor APIs', () => {
    it('should create a monitor', async () => {
      const config: MonitorConfig = {
        name: 'Test',
        watch_path: '/test',
        recursive: true,
        file_patterns: ['*.mp3'],
        asr_method: 'faster-whisper',
        language: 'en',
        output_formats: ['srt'],
        is_active: true
      }
      const result = await createMonitor(config)
      expect(result.monitor_id).toBe('test-monitor-id')
    })

    it('should get all monitors', async () => {
      const result = await getAllMonitors()
      expect(result.monitors).toBeInstanceOf(Array)
    })

    it('should get a specific monitor', async () => {
      const result = await getMonitor('monitor-123')
      expect(result.monitor_id).toBe('test-monitor-id')
    })

    it('should update a monitor', async () => {
      const result = await updateMonitor('monitor-123', { name: 'Updated' })
      expect(result.success).toBe(true)
    })

    it('should delete a monitor', async () => {
      const result = await deleteMonitor('monitor-123')
      expect(result.success).toBe(true)
    })

    it('should toggle monitor status', async () => {
      const result = await toggleMonitor('monitor-123', true)
      expect(result.success).toBe(true)
    })

    it('should get monitor service status', async () => {
      const result = await getMonitorServiceStatus()
      expect(result.is_running).toBe(true)
    })

    it('should start monitor service', async () => {
      const result = await startMonitorService()
      expect(result.success).toBe(true)
    })

    it('should stop monitor service', async () => {
      const result = await stopMonitorService()
      expect(result.success).toBe(true)
    })
  })

  describe('Database API', () => {
    it('should get database status', async () => {
      const result = await getDatabaseStatus()
      expect(result.is_connected).toBe(true)
      expect(result.database_type).toBe('sqlite')
    })
  })
})
