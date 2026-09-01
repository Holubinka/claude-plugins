const db = {
  async query(sql, params) {
    throw new Error("fixture: not connected");
  },
};

module.exports = { db };
