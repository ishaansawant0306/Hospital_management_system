// Global setup for Jest tests
// Provide a simple global.fetch mock and stub bootstrap Modal
global.fetch = global.fetch || jest.fn();

// Minimal bootstrap modal stub so components can call bootstrap.Modal
global.bootstrap = global.bootstrap || {
  Modal: jest.fn().mockImplementation(() => ({
    show: jest.fn(),
    hide: jest.fn()
  }))
};
