/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../templates/**/*.html"],
  darkMode:false,
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
}
