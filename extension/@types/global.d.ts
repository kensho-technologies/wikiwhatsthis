// Copyright 2020-present Kensho Technologies, LLC.
interface Window {
  browser: any;
  chrome: any;
}

declare const pyodide: any;

declare module '*.joblib' {}
declare module '*.csv' {}
declare module '*.json' {}
declare module '*.npz' {}
declare module '*.py' {}
