db = db.getSiblingDB('ai-platform');
db.createUser({
  user: "testuser",
  pwd: "testpass",
  roles: [ { role: "readWrite", db: "ai-platform" } ]
});
// Fjern eksisterende brugere, hvis der er nogen
db.users.remove({});

db.users.insertOne({
  username: "testuser",
  hash: "$2b$10$V9DPdFjXZIA0RzE.wfA3wO8b1X2ZYqxE2Q8W.X5wRVW15UEvVr8E6", // hashed "testpass"
  salt: "somerandomsalt"
});
