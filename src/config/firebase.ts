import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "AIzaSyAdK0XZhMmCJPnTcL8Rll9kfS1HImBK_p4",
  authDomain: "realtime-chat-ec5c9.firebaseapp.com",
  projectId: "realtime-chat-ec5c9",
  storageBucket: "realtime-chat-ec5c9.firebasestorage.app",
  messagingSenderId: "173502664319",
  appId: "1:173502664319:web:7ae32afe0b30d617fb394a",
  measurementId: "G-7GBXL6HC4D"
};
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
