/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_COGNITO_USER_POOL_ID: string;
  readonly VITE_COGNITO_USER_POOL_CLIENT_ID: string;
  readonly VITE_ENABLE_COGNITO_LOGIN: string;
  readonly VITE_ENABLE_CUSTOM_PROVIDER: string;
  readonly VITE_CUSTOM_PROVIDER_NAME: string;
  readonly VITE_COGNITO_DOMAIN: string;
  readonly VITE_OAUTH_REDIRECT_SIGN_IN: string;
  readonly VITE_OAUTH_REDIRECT_SIGN_OUT: string;
  readonly VITE_OAUTH_SCOPES: string;
  readonly VITE_OAUTH_RESPONSE_TYPE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
