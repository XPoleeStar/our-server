const server = "http://127.0.0.1:8000";

const delay = 30;
const times = 10;

function generate() {
  return Math.random().toString(36).substring(2, 13);
}

const container = document.getElementById("qrcode-container");
const placeholder = container.innerHTML;

const loginElement = document.getElementById("user-login");
const passwordElement = document.getElementById("user-password");

function sendKey(login, password, key) {
  fetch(server, {
    method: "POST",
    headers: {
      "user-login": login,
      "user-password": password
    },
    body: key
  }).then(response => {
    if (!response.ok) {
      if (response.status == 404) {
        alert("user not found");
      }
    }
  });
}

document.getElementById("scan-button")
.addEventListener("click", () => {
  container.innerHTML = placeholder;

  const scanner = new Html5Qrcode("qrcode-container");
  scanner.start(
    {facingMode: "environment"},
    {fps: 10},
    (key) => {
      scanner.stop();
      sendKey(
        loginElement.value,
        passwordElement.value,
      key);
    }
  );
});

document.getElementById("show-button")
.addEventListener("click", () => {
  const key = generate();
  container.innerHTML = "";
  new QRCode(container, {text: key});
  sendKey(
    loginElement.value,
    passwordElement.value,
  "secretkey");

  let counter = 0;
  const interval = setInterval(() => {
    counter++;

    const key = generate();
    container.innerHTML = "";
    new QRCode(container, {text: key});
    sendKey(
      loginElement.value,
      passwordElement.value,
    "secretkey");

    if (counter == times) {
      clearInterval(interval);
      container.innerHTML = placeholder;
    }
  }, delay);

});

