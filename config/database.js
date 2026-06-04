const path = require('path');

module.exports = ({ env }) => {
  const isPostgres = env('DATABASE_URL');

  return {
    connection: {
      client: isPostgres ? 'postgres' : 'sqlite',
      connection: isPostgres 
        ? {
            connectionString: env('DATABASE_URL'),
            ssl: { rejectUnauthorized: false },
          }
        : {
            filename: path.join(__dirname, '..', env('DATABASE_FILENAME', '.tmp/data.db')),
          },
      useNullAsDefault: !isPostgres,
      acquireConnectionTimeout: env.int('DATABASE_CONNECTION_TIMEOUT', 60000),
    },
  };
};