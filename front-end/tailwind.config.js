/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{svelte,js,ts,jsx,tsx}"],
  theme: {
    fontFamily: {
      sans: ["Lexend"],
    },
    colors: {
      "accent": "#4744d9",
      "light-accent": "#D5D4F9",
      "black": "#333",
      "white": "#F5F5F5",
      "background": "#EDECF4",
      "dark-gray": "#999999",
      "light-gray": "#BDBDBD",
    },
  },
  plugins: [],
};
