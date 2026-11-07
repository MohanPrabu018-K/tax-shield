const path = require('path');
const { MongoMemoryServer } = require(path.join(__dirname, '../frontend/node_modules/mongodb-memory-server'));

async function main() {
  try {
    console.log('[INFO] Initializing MongoDB Memory Server (Genuine Isolated mongod)...');
    const mongod = await MongoMemoryServer.create({
      instance: {
        port: 27017,
        dbName: 'tax_shield_test',
      },
    });
    const uri = mongod.getUri();
    console.log(`[READY] Genuine MongoDB Community Server is listening at ${uri} (port 27017)`);

    const cleanup = async () => {
      console.log('[INFO] Stopping MongoDB Memory Server...');
      await mongod.stop();
      process.exit(0);
    };

    process.on('SIGINT', cleanup);
    process.on('SIGTERM', cleanup);
  } catch (err) {
    console.error('[ERROR] Failed to start MongoDB Memory Server:', err);
    process.exit(1);
  }
}

main();
