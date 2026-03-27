/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./*.html",
    "./blog/*.html",
  ],
  theme: {
    extend: {
      colors: {
        accent: "#00D4FF",
      },
      fontFamily: {
        heading: ['"Space Grotesk"', "sans-serif"],
        body: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
