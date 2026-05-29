class UserSessionManager {
  constructor() {
    this.users = [
      { username: 'admin', role: 'admin' },
      { username: 'dev_user', role: 'developer' },
    ];
    this.sessions = {};
  }

  login(username) {
    const user = this.users.find(u => u.username === username);
    if (!user) {
      return { success: false, message: 'User not found' };
    }
    const sessionId = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    this.sessions[sessionId] = { username: username, role: user.role };
    return { success: true, sessionId: sessionId, role: user.role };
  }

  logout(sessionId) {
    if (this.sessions[sessionId]) {
      delete this.sessions[sessionId];
      return true;
    }
    return false;
  }

  getSession(sessionId) {
    return this.sessions[sessionId] || null;
  }

  updateProfile(username, updates) {
    const user = this.users.find(u => u.username === username);
    if (!user) {
      return false;
    }
    Object.assign(user, updates);
    return true;
  }

  promoteToAdmin(username) {
    const user = this.users.find(u => u.username === username);
    if (!user) {
      return false;
    }
    user.role = 'admin';
    return true;
  }

  listAllUsers() {
    return this.users.map(user => ({ username: user.username, role: user.role }));
  }
}

module.exports = { UserSessionManager };