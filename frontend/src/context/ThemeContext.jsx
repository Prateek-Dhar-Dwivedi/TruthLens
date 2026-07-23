import {
    createContext,
    useState,
    useContext,
    useEffect
} from "react";

const ThemeContext = createContext();

export const ThemeProvider = ({
    children
}) => {

    const [darkMode, setDarkMode] = useState(
        localStorage.getItem("theme") === "dark"
    );

    useEffect(() => {

        if (darkMode) {

            document.body.classList.add("dark");

            localStorage.setItem(
                "theme",
                "dark"
            );

        } else {

            document.body.classList.remove("dark");

            localStorage.setItem(
                "theme",
                "light"
            );

        }

    }, [darkMode]);

    const toggleTheme = () => {

        setDarkMode(
            prev => !prev
        );

    };

    return (

        <ThemeContext.Provider
            value={{
                darkMode,
                toggleTheme
            }}
        >
            {children}
        </ThemeContext.Provider>

    );

};

export const useTheme = () =>
    useContext(ThemeContext);