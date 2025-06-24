import { MongoClient } from 'mongodb';
import bcrypt from 'bcryptjs';

const MONGODB_URI = 'mongodb://localhost:27017';
const DB_NAME = 'chat_app';

async function createAdminUser() {
  const client = new MongoClient(MONGODB_URI);

  try {
    await client.connect();
    console.log('Connected to MongoDB');

    const db = client.db(DB_NAME);
    const usersCollection = db.collection('users');

    // Check if admin user already exists
    const existingAdmin = await usersCollection.findOne({ email: 'admin@example.com' });
    if (existingAdmin) {
      console.log('Admin user already exists');
      return;
    }

    // Create admin user
    const hashedPassword = await bcrypt.hash('admin123', 10);
    const adminUser = {
      email: 'admin@example.com',
      password: hashedPassword,
      role: 'admin',
      is_online: false,
      last_seen: new Date(),
      isFirstLogin: true,
      created_at: new Date(),
      updated_at: new Date()
    };

    await usersCollection.insertOne(adminUser);
    console.log('Admin user created successfully');
  } catch (error) {
    console.error('Error creating admin user:', error);
  } finally {
    await client.close();
  }
}

createAdminUser();
