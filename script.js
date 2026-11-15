// const server = "http://192.168.1.15:8000";

// const delay = 3000;
// const times = 5;

async function generateKeyPair() {
  const keyPair = await crypto.subtle.generateKey({
    name: "ECDSA", namedCurve: "P-256"
    }, false, ["sign", "verify"]
  );
  console.log(keyPair);
  return {
    public: btoa(String.fromCharCode(...new Uint8Array(
      await crypto.subtle.exportKey("raw", keyPair.publicKey)
    ))),
    private: keyPair.privateKey
  }
}

async function signKey(privateKey, key) {
  const buffer = new TextEncoder().encode(key);
  const signatureBuffer = await crypto.subtle.sign({
    name: "ECDSA", hash: {name: "SHA-256"}
  }, privateKey, buffer);
  const signatureBytes = new Uint8Array(signatureBuffer);
  return btoa(String.fromCharCode(...signatureBytes));
}

async function student(key) {
  const keyPair = await generateKeyPair();
  await signKey(keyPair.private, key);
  fetch("http://192.168.1.15:8000", {
    method: "POST",
    headers: {
      "user-login": "1",
      "user-password": "1",
      "user-signature": await signKey(keyPair.private, "secret"),
      "user-public-key": keyPair.public 
    },
    body: key
  });
}

async function teacher(key) {
  const keyPair = await generateKeyPair();
  await signKey(keyPair.private, key);
  fetch("http://192.168.1.15:8000", {
    method: "POST",
    headers: {
      "user-login": "x",
      "user-password": "x"
    },
    body: key
  });
}

// function generate() {
//   return Math.random().toString(36).substring(2, 13);
// }

// const container = document.getElementById("qrcode-container");
// const placeholder = container.innerHTML;

// const loginElement = document.getElementById("user-login");
// const passwordElement = document.getElementById("user-password");

// function sendKey(login, password, key) {
//   fetch(server, {
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
//     alert("укажите логин и пароль");
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