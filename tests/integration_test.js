const { test, expect } = require('@playwright/test');

test.describe('Session Management Integration', () => {
  // Mocking the web application context.
  const mockApp = {
    storage: {
      setItem: async (key, value) => {
        mockApp.storage[key] = value;
      },
      getItem: async (key) => mockApp.storage[key] || null,
      removeItem: async (key) => delete mockApp.storage[key]
    },
    sessionManager: require('../target/session.js').default
  };

  test('Login flow', async () => {
    const loginResult = mockApp.sessionManager.login('admin');
    expect(loginResult.success).toBe(true);

    await mockApp.storage.setItem('sessionId', loginResult.sessionId);
    const storedSessionId = await mockApp.storage.getItem('sessionId');
    expect(storedSessionId).toBe(loginResult.sessionId);

    const session = mockApp.sessionManager.getSession(storedSessionId);
    expect(session.username).toBe('admin');
  });

  test('Logout flow', async () => {
    const loginResult = mockApp.sessionManager.login('admin');
    const sessionId = loginResult.sessionId;
    await mockApp.storage.setItem('sessionId', sessionId);

    mockApp.sessionManager.logout(sessionId);
    const session = mockApp.sessionManager.getSession(sessionId);
    expect(session).toBeNull();

    const storedSessionId = await mockApp.storage.getItem('sessionId');
    expect(storedSessionId).toBe(sessionId);
  });

    test('Profile update simulation', async () => {
        mockApp.sessionManager.login('admin');
        mockApp.sessionManager.updateProfile('admin', { email: 'integration@example.com' });
        const adminUser = mockApp.sessionManager.users.find(u => u.username === 'admin');
        expect(adminUser.email).toBe('integration@example.com');
    });
});