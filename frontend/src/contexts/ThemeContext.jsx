/* DO NOT UNDO — ThemeContext. All features in this file are approved and must be preserved. */
import { createContext, useContext, useEffect, useState } from "react";

const ThemeContext = createContext({
  theme: "light",
  toggleTheme: () => {},
});

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("dark");
    localStorage.setItem("theme", "light");
    setTheme("light");
  }, []);

  const toggleTheme = () => {
    setTheme("light");
    document.documentElement.classList.remove("dark");
    localStorage.setItem("theme", "light");
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeProvider;
