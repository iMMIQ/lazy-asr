/**
 * Component test example for TaskList
 *
 * This demonstrates best practices for testing React components:
 * - Testing user interactions
 * - Testing async operations
 * - Testing different states (loading, error, success)
 */
import { describe, it, expect, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from '../utils/test-utils'

// Mock component - replace with actual import when testing real components
function TaskList({ tasks, onTaskClick, onDelete, loading, error }: any) {
  if (loading) {
    return <div data-testid="loading-state">Loading...</div>
  }

  if (error) {
    return <div data-testid="error-state">{error}</div>
  }

  if (!tasks || tasks.length === 0) {
    return <div data-testid="empty-state">No tasks found</div>
  }

  return (
    <div data-testid="task-list">
      {tasks.map((task: any) => (
        <div key={task.id} data-testid={`task-${task.id}`}>
          <span>{task.status}</span>
          <button onClick={() => onTaskClick?.(task.id)}>View</button>
          <button onClick={() => onDelete?.(task.id)}>Delete</button>
        </div>
      ))}
    </div>
  )
}

// Mock TaskItem component
function TaskItem({ progress }: { progress: number }) {
  return <div data-testid="progress">{progress}%</div>
}

describe('TaskList', () => {
  const mockTasks = [
    { id: '1', status: 'completed', text: 'Task 1' },
    { id: '2', status: 'pending', text: 'Task 2' },
  ]

  describe('rendering', () => {
    it('renders empty state when no tasks', () => {
      renderWithProviders(<TaskList tasks={[]} />)
      expect(screen.getByTestId('empty-state')).toBeInTheDocument()
    })

    it('renders all tasks', () => {
      renderWithProviders(<TaskList tasks={mockTasks} />)

      expect(screen.getByTestId('task-1')).toBeInTheDocument()
      expect(screen.getByTestId('task-2')).toBeInTheDocument()
    })

    it('displays task status', () => {
      renderWithProviders(<TaskList tasks={mockTasks} />)

      expect(screen.getByText('completed')).toBeInTheDocument()
      expect(screen.getByText('pending')).toBeInTheDocument()
    })
  })

  describe('user interactions', () => {
    it('calls onTaskClick when view button is clicked', async () => {
      const user = userEvent.setup()
      const handleClick = vi.fn()

      renderWithProviders(
        <TaskList tasks={mockTasks} onTaskClick={handleClick} />
      )

      await user.click(screen.getAllByText('View')[0])
      expect(handleClick).toHaveBeenCalledWith('1')
    })

    it('calls onDelete when delete button is clicked', async () => {
      const user = userEvent.setup()
      const handleDelete = vi.fn()

      renderWithProviders(
        <TaskList tasks={mockTasks} onDelete={handleDelete} />
      )

      await user.click(screen.getAllByText('Delete')[0])
      expect(handleDelete).toHaveBeenCalledWith('1')
    })
  })

  describe('async behavior', () => {
    it('shows loading state initially', () => {
      renderWithProviders(<TaskList tasks={[]} loading={true} />)

      expect(screen.getByTestId('loading-state')).toBeInTheDocument()
    })

    it('handles error state', () => {
      renderWithProviders(<TaskList tasks={[]} error="Failed to load" />)

      expect(screen.getByText(/failed to load/i)).toBeInTheDocument()
    })
  })
})

describe('TaskItem', () => {
  it('updates progress when task progresses', async () => {
    const { rerender } = renderWithProviders(
      <TaskItem progress={0} />
    )

    expect(screen.getByText('0%')).toBeInTheDocument()

    rerender(<TaskItem progress={50} />)
    await waitFor(() => {
      expect(screen.getByText('50%')).toBeInTheDocument()
    })
  })
})
