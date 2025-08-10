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

// Dark mode toggle functionality
document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.getElementById("darkModeToggle");
  const icon = toggleBtn.querySelector("i");
  const prefersDark = localStorage.getItem("darkMode") === "true";

  const applyTheme = (isDark) => {
    document.body.classList.toggle("dark-mode", isDark);
    icon.className = isDark ? "fa fa-sun-o" : "fa fa-moon-o";
  }
  applyTheme(prefersDark);
  toggleBtn.addEventListener("click", () => {
    const isDark = !document.body.classList.contains("dark-mode");
    localStorage.setItem("darkMode", isDark);
    applyTheme(isDark);
  });
});