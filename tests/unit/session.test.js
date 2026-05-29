const { UserSessionManager } = require('../../session');

describe('UserSessionManager', () => {
  let sessionManager;

  beforeEach(() => {
    sessionManager = new UserSessionManager();
  });

  it('should successfully log in a user', () => {
    const result = sessionManager.login('admin');
    expect(result.success).toBe(true);
    expect(result.sessionId).toBeDefined();
    expect(result.role).toBe('admin');
  });

  it('should fail to log in a non-existent user', () => {
    const result = sessionManager.login('nonexistent');
    expect(result.success).toBe(false);
    expect(result.message).toBe('User not found');
  });

  it('should retrieve session data for a valid session ID', () => {
    const loginResult = sessionManager.login('admin');
    const sessionData = sessionManager.getSession(loginResult.sessionId);
    expect(sessionData).toBeDefined();
    expect(sessionData.username).toBe('admin');
  });

  it('should return null for an invalid session ID', () => {
    const sessionData = sessionManager.getSession('invalidSessionId');
    expect(sessionData).toBeNull();
  });

  it('should update a user profile', () => {
    const initialUser = sessionManager.users.find(u => u.username === 'dev_user');
    const updates = { email: 'new_email@example.com', newField: 'newValue' };
    sessionManager.updateProfile('dev_user', updates);
    const updatedUser = sessionManager.users.find(u => u.username === 'dev_user');
    expect(updatedUser.email).toBe('new_email@example.com');
    expect(updatedUser.newField).toBe('newValue');
  });

  it('should not update profile of a non-existent user', () => {
    const result = sessionManager.updateProfile('nonexistent', { email: 'test@test.com' });
    expect(result).toBe(false);
  });

  it('should promote a user to admin', () => {
    sessionManager.promoteToAdmin('dev_user');
    const user = sessionManager.users.find(u => u.username === 'dev_user');
    expect(user.role).toBe('admin');
  });

  it('should not promote a non-existent user to admin', () => {
    const result = sessionManager.promoteToAdmin('nonexistent');
    expect(result).toBe(false);
  });

  it('should log out a user', () => {
    const loginResult = sessionManager.login('admin');
    const sessionId = loginResult.sessionId;
    const result = sessionManager.logout(sessionId);
    expect(result).toBe(true);
    expect(sessionManager.getSession(sessionId)).toBeNull();
  });

  it('should return false when trying to log out with a non-existent session id', () => {
    const result = sessionManager.logout('nonexistentSessionId');
    expect(result).toBe(false);
  });

  it('should list all users with username and role', () => {
    const users = sessionManager.listAllUsers();
    expect(users).toEqual(expect.arrayContaining([
      expect.objectContaining({ username: 'admin', role: 'admin' }),
      expect.objectContaining({ username: 'dev_user', role: 'developer' }),
    ]));
  });
});
