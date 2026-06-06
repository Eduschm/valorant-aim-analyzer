import { describe, it, expect, afterEach } from 'vitest'
import { render, screen, fireEvent, cleanup, waitFor } from '@testing-library/react'
import { FaqAccordion } from '@/components/marketing/FaqAccordion'

describe('FaqAccordion', () => {
  afterEach(cleanup)

  it('renders all questions', () => {
    render(<FaqAccordion items={[
      { q: 'First question?', a: 'First answer.' },
      { q: 'Second question?', a: 'Second answer.' },
    ]} />)
    expect(screen.getByText('First question?')).toBeInTheDocument()
    expect(screen.getByText('Second question?')).toBeInTheDocument()
  })

  it('expands a collapsed question to reveal its answer', async () => {
    render(<FaqAccordion items={[
      { q: 'First question?', a: 'First answer.' },
      { q: 'Second question?', a: 'Second answer.' },
    ]} />)
    // First item is open by default; the second answer is hidden until clicked.
    expect(screen.queryByText('Second answer.')).not.toBeInTheDocument()
    fireEvent.click(screen.getByText('Second question?'))
    await waitFor(() => expect(screen.getByText('Second answer.')).toBeInTheDocument())
  })

  it('marks the open row with aria-expanded', () => {
    render(<FaqAccordion items={[{ q: 'Only one?', a: 'Yes.' }]} />)
    expect(screen.getByRole('button', { name: /Only one/i })).toHaveAttribute('aria-expanded', 'true')
  })
})
