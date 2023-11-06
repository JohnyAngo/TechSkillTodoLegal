module.exports.region = () => ({
  dev: "us-east-1",
  prod: "us-east-1",
});

module.exports = {
  database: {
    MONGO_DB_USER: "jango-sls-aws",
    MONGO_DB_PASS: "1yIV0SdeEGFJGZms",
    MONGO_DB_NAME: "Exercise1",
    MONGO_DB_URL: "sls-mongo-example.ui4zke8.mongodb.net",
    MONGO_COLLECTION_NAME: "exercise1",
    MONGO_COLLECTION_NAME2: "dweet",
  }
};
