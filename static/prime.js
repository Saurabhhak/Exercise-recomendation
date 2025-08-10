let nav = document.querySelector("nav");
document.querySelector("#menu-btn").onclick = () => {
  nav.classList.toggle("active");
};
window.onscroll = () => {
  nav.classList.remove("active");
};