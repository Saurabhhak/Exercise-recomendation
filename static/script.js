let loginForm = document.querySelector(".login-form");
document.querySelector("#login-btn").onclick = () => {
  loginForm.classList.toggle("active");
  // searchForm.classList.remove('active');
  // shoppingCart.classList.remove("active");
  navBar.classList.remove("active");

};

let navBar = document.querySelector(".navbar");
document.querySelector("#menu-btn").onclick = () => {
  navBar.classList.toggle("active");
  // searchForm.classList.remove('active');
  // shoppingCart.classList.remove("active");
  loginForm.classList.remove("active");
};
window.onscroll = () => {
  // searchForm.classList.remove("active");
  // shoppingCart.classList.remove("active");
  loginForm.classList.remove("active");
  navBar.classList.remove("active");
};

