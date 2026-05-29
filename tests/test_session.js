const userSessionManager = require('../target/session.js').default;

describe('UserSessionManager', () => {
  let sessionManager;

  beforeEach(() => {
    sessionManager = userSessionManager;
  });

  it('should authenticate a user and create a session', () => {
    const result = sessionManager.login('admin');
    expect(result.success).toBe(true);
    expect(result.sessionId).toBeDefined();
    expect(result.role).toBe('admin');
  });

  it('should return an error if the user is not found', () => {
    const result = sessionManager.login('nonexistent_user');
    expect(result.success).toBe(false);
    expect(result.message).toBe('User not found');
  });

  it('should retrieve session data', () => {
    const loginResult = sessionManager.login('admin');
    const session = sessionManager.getSession(loginResult.sessionId);
    expect(session).toBeDefined();
    expect(session.username).toBe('admin');
  });

  it('should return null for non-existent session', () => {
    const session = sessionManager.getSession('invalid_session_id');
    expect(session).toBeNull();
  });

  it('should update user profile', () => {
    sessionManager.updateProfile('admin', { email: 'new_email@example.com' });
    const adminUser = sessionManager.users.find(u => u.username === 'admin');
    expect(adminUser.email).toBe('new_email@example.com');
  });

  it('should promote a user to admin', () => {
    sessionManager.promoteToAdmin('dev_user');
    const devUser = sessionManager.users.find(u => u.username === 'dev_user');
    expect(devUser.role).toBe('admin');
  });

  it('should logout a user', () => {
    const loginResult = sessionManager.login('admin');
    const sessionId = loginResult.sessionId;
    sessionManager.logout(sessionId);
    const session = sessionManager.getSession(sessionId);
    expect(session).toBeNull();
  });

  it('should list all users', () => {
    const users = sessionManager.listAllUsers();
    expect(users).toBeDefined();
    expect(users.length).toBe(2);
    expect(users[0].username).toBe('admin');
    expect(users[1].username).toBe('dev_user');
  });

    it('should handle missing crypto implementation gracefully', () => {
        const originalCrypto = global.crypto;
        global.crypto = undefined;
        const result = sessionManager.login('admin');
        expect(result.success).toBe(true);
        expect(result.sessionId).toBeDefined();
        expect(result.role).toBe('admin');
        global.crypto = originalCrypto;
    });

    it('should demonstrate the profile update bug', () => {
        sessionManager.updateProfile('admin', {email: 'test@example.com'});
        const adminUser = sessionManager.users.find(u => u.username === 'admin');
        expect(adminUser.id).toBeUndefined();
        expect(adminUser.role).toBeUndefined();
    });
});