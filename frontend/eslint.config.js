const js = require("@eslint/js");
const globals = require("globals");
const reactHooks = require("eslint-plugin-react-hooks");

module.exports = [
  js.configs.recommended,
  {
    files: ["src/**/*.{js,jsx}"],
    linterOptions: {
      reportUnusedDisableDirectives: false,
    },
    plugins: {
      "react-hooks": reactHooks,
    },
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
      globals: {
        ...globals.browser,
        ...globals.es2021,
        process: "readonly",
      },
    },
    rules: {
      "no-unused-vars": "off",
      "no-useless-escape": "off",
      "no-empty-pattern": "off",
      "no-control-regex": "off",
      "no-dupe-keys": "warn",
      "no-undef": "off",
      "no-unsafe-finally": "off",
      "no-redeclare": "off",
      "no-empty": "off",
      "no-constant-condition": "off",
      "no-prototype-builtins": "off",
      "no-fallthrough": "off",
      "no-extra-boolean-cast": "off",
      "no-case-declarations": "off",
      "no-self-assign": "off",
      "no-cond-assign": "off",
      "no-func-assign": "off",
    },
  },
  {
    ignores: ["build/", "node_modules/", "public/"],
  },
];
