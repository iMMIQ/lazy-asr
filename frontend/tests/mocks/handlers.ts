/**
 * MSW (Mock Service Worker) API handlers
 *
 * These handlers mock API responses for testing.
 * They intercept HTTP requests and return controlled responses.
 */
import { http, HttpResponse } from 'msw'

// Mock task data
const mockTasks = [
  {
    id: 'task-1',
    status: 'completed',
    progress: 100,
    text: 'Sample transcribed text',
    createdAt: new Date().toISOString()
  },
  {
    id: 'task-2',
    status: 'pending',
    progress: 0,
    text: null,
    createdAt: new Date().toISOString()
  }
]

// Mock scan result
const mockScanResult = {
  taskId: 'task-3',
  status: 'completed',
  progress: 100,
  text: 'This is a test transcription',
  duration: 12.5,
  segments: [
    { start: 0.0, end: 5.0, text: 'This is a test' },
    { start: 5.0, end: 12.5, text: 'transcription' }
  ],
  createdAt: new Date().toISOString()
}

export const handlers = [
  // POST /api/scan - Start a new scan
  http.post('/api/scan', async ({ request }) => {
    const formData = await request.formData()
    const file = formData.get('file') as File

    if (!file) {
      return HttpResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      )
    }

    // Return a mock task
    return HttpResponse.json({
      id: `task-${Date.now()}`,
      status: 'pending',
      progress: 0,
      filename: file.name,
      createdAt: new Date().toISOString()
    }, { status: 201 })
  }),

  // GET /api/tasks - List all tasks
  http.get('/api/tasks', () => {
    return HttpResponse.json({
      items: mockTasks,
      total: mockTasks.length
    })
  }),

  // GET /api/tasks/:id - Get task by ID
  http.get('/api/tasks/:id', ({ params }) => {
    const { id } = params
    const task = mockTasks.find(t => t.id === id)

    if (!task) {
      return HttpResponse.json(
        { error: 'Task not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json(task)
  }),

  // GET /api/scan/:id - Get scan result by ID
  http.get('/api/scan/:id', ({ params }) => {
    const { id } = params

    if (id === 'task-3') {
      return HttpResponse.json(mockScanResult)
    }

    return HttpResponse.json(
      { error: 'Scan not found' },
      { status: 404 }
    )
  }),

  // DELETE /api/tasks/:id - Delete a task
  http.delete('/api/tasks/:id', ({ params }) => {
    const { id } = params
    const taskIndex = mockTasks.findIndex(t => t.id === id)

    if (taskIndex === -1) {
      return HttpResponse.json(
        { error: 'Task not found' },
        { status: 404 }
      )
    }

    return HttpResponse.json({ success: true })
  }),

  // GET /health - Health check
  http.get('/health', () => {
    return HttpResponse.json({ status: 'healthy' })
  }),

  // POST /api/tasks/:id/cancel - Cancel a task
  http.post('/api/tasks/:id/cancel', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      status: 'cancelled'
    })
  })
]

// Helper to create a handler with custom response
export function createMockHandler(
  method: 'get' | 'post' | 'put' | 'delete',
  path: string,
  response: any,
  status = 200
) {
  const httpMethod = http[method]
  return httpMethod(path, () => HttpResponse.json(response, { status }))
}

// Helper to create an error handler
export function createErrorHandler(
  method: 'get' | 'post' | 'put' | 'delete',
  path: string,
  error: string,
  status = 500
) {
  const httpMethod = http[method]
  return httpMethod(path, () => HttpResponse.json({ error }, { status }))
}
