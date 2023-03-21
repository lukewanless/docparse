/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../templates/**/*.html"],
  darkMode:false,
  theme: {
    extend: {},
    container: {
      center: true,
    }
  },
  plugins: [require("daisyui")],
}
