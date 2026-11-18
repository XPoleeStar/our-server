// let host = "http://192.168.1.15:8000";

// const delay = 3000;
// const times = 10;

async function signSessionKey(keyPair, sessionKey) {
  const buffer = new TextEncoder().encode(sessionKey);
  const signatureBuffer = await crypto.subtle.sign({
    name: "ECDSA", hash: {name: "SHA-256"}
  }, keyPair.privateKey, buffer);
  const signatureBytes = new Uint8Array(signatureBuffer);
  return btoa(String.fromCharCode(...signatureBytes));
}

async function generateKeyPair() {
  return await crypto.subtle.generateKey({
    name: "ECDSA", namedCurve: "P-256"
    }, false, ["sign", "verify"]
  );
}

async function exportPublicKey(keyPair) {
  return btoa(String.fromCharCode(...new Uint8Array(
    await crypto.subtle.exportKey("raw", keyPair.publicKey)
  )));
}

const db = indexedDB.open('user', 1);

db.onupgradeneeded = () => {
  db.result.createObjectStore('data');
}

// async function test(hostname, login, password, key, sign) {
//   const headers = {
//     "user-login": login,
//     "user-password": password
//   };
//   if (sign) {
//     if (keys == undefined) {
//       keys = await generateKeyPair();
//     }
//     headers["user-signature"] = await sign(keys.private, key);
//     headers["user-public-key"] = keys.public;
//   }
//   fetch(hostname, {
//     method: "POST",
//     headers,
//     body: key
//   });
// }


function generateKey() {
  return Math.random().toString(36).substring(2, 13);
}

// const container = document.getElementById("qrcode-container");
// const placeholder = container.innerHTML;

// const loginElement = document.getElementById("user-login");
// const passwordElement = document.getElementById("user-password");

// function sendKey(login, password, key) {
//   fetch(host, {
//     method: "POST",
//     headers: {
//       "user-login": login,
//       "user-password": password
//     },
//     body: key
//   }).then(response => {
//     if (!response.ok) {
//       if (response.status == 404) {
//         alert("user not found");
//       }
//     }
//     return response;
//   });
// }

// document.getElementById("scan-button")
// .addEventListener("click", () => {
//   container.innerHTML = placeholder;

//   if (!loginElement.value || !passwordElement.value) {
    
//     return;
//   }

//   const scanner = new Html5Qrcode("qrcode-container");
//   scanner.start(
//     {facingMode: "environment"},
//     {fps: 10},
//     (key) => {
//       scanner.stop();
//       sendKey(
//         loginElement.value,
//         passwordElement.value,
//       key);
//     }
//   );
// });

// document.getElementById("show-button")
// .addEventListener("click", () => {
//   if (!loginElement.value || !passwordElement.value) {
//       alert("укажите логин и пароль");
//       return;
//   }
//   const key = generate();
//   container.innerHTML = "";
//   new QRCode(container, {text: key});
//   const result = sendKey(
//     loginElement.value,
//     passwordElement.value,
//   key);
//   console.log(result);

//   let counter = 0;
//   const interval = setInterval(() => {
//     counter++;

//     const key = generate();
//     container.innerHTML = "";
//     new QRCode(container, {text: key});
//     sendKey(
//       loginElement.value,
//       passwordElement.value,
//     "secretkey");

//     if (counter == times) {
//       clearInterval(interval);
//       container.innerHTML = placeholder;
//     }
//   }, delay);

// });