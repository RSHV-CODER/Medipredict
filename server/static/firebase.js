 // Import the functions you need from the SDKs you need
 import { initializeApp } from "https://www.gstatic.com/firebasejs/11.5.0/firebase-app.js";
 import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.5.0/firebase-analytics.js";
 // TODO: Add SDKs for Firebase products that you want to use
 // https://firebase.google.com/docs/web/setup#available-libraries

 // Your web app's Firebase configuration
 // For Firebase JS SDK v7.20.0 and later, measurementId is optional
 const firebaseConfig = {
   apiKey: "AIzaSyAdAFgH8J7KUE4cDINu7D3dWHXopdb59xs",
   authDomain: "healthmonitoring-5d174.firebaseapp.com",
   projectId: "healthmonitoring-5d174",
   storageBucket: "healthmonitoring-5d174.firebasestorage.app",
   messagingSenderId: "28352098706",
   appId: "1:28352098706:web:c8b7bed6d2b596df32514b",
   measurementId: "G-5QH8P9ZRWZ"
 };

 // Initialize Firebase
 const app = initializeApp(firebaseConfig);
 const analytics = getAnalytics(app);