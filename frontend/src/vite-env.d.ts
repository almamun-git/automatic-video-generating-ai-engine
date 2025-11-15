/// <reference types="vite/client" />

// Optional: add IntelliSense for your custom env vars
interface ImportMetaEnv {
  readonly VITE_API_BASE?: string;
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}
