/* DO_NOT_UNDO — ThemeContext. Forced light mode globally.
   The toggleTheme function is a no-op by design — the user explicitly
   requires light mode only with high contrast. No dark mode toggle. */
import { createContext, useContext, useEffect, useState } from "react";

const ThemeContext = createContext({
  theme: "light",
  toggleTheme: () => {},
});

export const useTheme = () => useContext(ThemeContext);

// DO_NOT_UNDO — Forced light mode. Do not add dark mode toggle.
export const ThemeProvider = ({ children }) => {
  const [theme] = useState("light");

  useEffect(() => {
    document.documentElement.classList.remove("dark");
    localStorage.setItem("theme", "light");
  }, []);

  // toggleTheme is intentionally a no-op — forced light mode per user requirement
  const toggleTheme = () => {};

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeProvider;
