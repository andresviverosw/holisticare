/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#f0faf4",
          100: "#dcf5e5",
          200: "#bbe9ce",
          300: "#88d5ab",
          400: "#52b880",
          500: "#2d9b5f",   // primary green
          600: "#1f7d4b",
          700: "#1a633c",
          800: "#184f32",
          900: "#15412a",
        },
        neutral: {
          50:  "#f8f9fa",
          100: "#f1f3f5",
          200: "#e9ecef",
          300: "#dee2e6",
          400: "#ced4da",
          500: "#adb5bd",
          600: "#868e96",
          700: "#495057",
          800: "#343a40",
          900: "#212529",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
