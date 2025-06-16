import { initializeApp } from "https://www.gstatic.com/firebasejs/11.9.1/firebase-app.js";
import { getDatabase, ref, set, get, push, onValue } from "https://www.gstatic.com/firebasejs/11.9.1/firebase-database.js";

const firebaseConfig = {
  apiKey: "AIzaSyA2d7MCr7YlIF7gCDZWM0AHbqM59aJHOxM",
  authDomain: "base-datos-rv.firebaseapp.com",
  databaseURL: "https://base-datos-rv-default-rtdb.firebaseio.com",
  projectId: "base-datos-rv",
  storageBucket: "base-datos-rv.firebasestorage.app",
  messagingSenderId: "511305176330",
  appId: "1:511305176330:web:975b31ec0bd7af0f9e56f3",
  measurementId: "G-2XS3472VRD"
};

const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

export function guardarDato(ruta, dato) {
  return set(ref(db, ruta), dato);
}

export function leerDato(ruta) {
  return get(ref(db, ruta)).then(snapshot => snapshot.exists() ? snapshot.val() : null);
}

export function escucharDato(ruta, callback) {
  onValue(ref(db, ruta), (snapshot) => callback(snapshot.val()));
}

export function agregarDato(ruta, dato) {
  return push(ref(db, ruta), dato);
}

export function inicializarUsuarios() {
  const usuarios = {
    Thomas: { password: "1108" },
    Ricardo: { password: "1234" },
    Tania: { password: "1234" }
  };
  return guardarDato('usuarios', usuarios);
}

export function registrarTrabajo(trabajo) {
  return push(ref(db, 'trabajos'), trabajo);
}