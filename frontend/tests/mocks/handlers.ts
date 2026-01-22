// tests/mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  // Mock submit files endpoint
  http.post('/api/submit', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      success: true,
      results: []
    })
  }),

  // Mock scan path endpoint
  http.post('/api/scan', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      success: true,
      files: []
    })
  }),

  // Mock get plugins endpoint
  http.get('/api/plugins', () => {
    return HttpResponse.json({
      plugins: ['whisper', 'faster-whisper', 'sherpa-onnx']
    })
  })
]
