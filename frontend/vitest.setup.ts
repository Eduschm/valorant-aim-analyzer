import '@testing-library/jest-dom'

// jsdom lacks IntersectionObserver, which framer-motion's useInView relies on.
class MockIntersectionObserver {
  readonly root = null
  readonly rootMargin = ''
  readonly thresholds = []
  constructor(private cb: IntersectionObserverCallback) {}
  observe(target: Element) {
    // Report the element as in view immediately so animations settle.
    this.cb(
      [{ isIntersecting: true, target } as unknown as IntersectionObserverEntry],
      this as unknown as IntersectionObserver,
    )
  }
  unobserve() {}
  disconnect() {}
  takeRecords() {
    return []
  }
}

;(globalThis as any).IntersectionObserver = MockIntersectionObserver
;(globalThis as any).ResizeObserver =
  (globalThis as any).ResizeObserver ||
  class {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
