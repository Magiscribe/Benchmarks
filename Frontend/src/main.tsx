import './i18n/i18n';
import { Amplify } from 'aws-amplify';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { AuthProvider } from './providers/AuthProvider';
import { QueryProvider } from './providers/QueryProvider';
import router from './router';
import './styles/index.css';

// Get authentication configuration from environment variables
const enableCustomProvider = import.meta.env.VITE_ENABLE_CUSTOM_PROVIDER === 'true';
const customProviderName = import.meta.env.VITE_CUSTOM_PROVIDER_NAME || 'Magiscribe';
const cognitoDomain = import.meta.env.VITE_COGNITO_DOMAIN;

// Parse arrays from comma-separated strings in environment variables
const redirectSignIn = import.meta.env.VITE_OAUTH_REDIRECT_SIGN_IN?.split(',') || ['http://localhost:5173'];
const redirectSignOut = import.meta.env.VITE_OAUTH_REDIRECT_SIGN_OUT?.split(',') || ['http://localhost:5173'];
const oauthScopes = import.meta.env.VITE_OAUTH_SCOPES?.split(',') || ['email', 'openid', 'profile', 'aws.cognito.signin.user.admin'];
const responseType = import.meta.env.VITE_OAUTH_RESPONSE_TYPE || 'code';

// Build the Amplify configuration
Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID,
      userPoolClientId: import.meta.env.VITE_COGNITO_USER_POOL_CLIENT_ID,
      loginWith: {
        // Keep email login if needed, or adjust based on VITE_ENABLE_COGNITO_LOGIN
        email: import.meta.env.VITE_ENABLE_COGNITO_LOGIN === 'true', 
        oauth: enableCustomProvider ? {
          redirectSignIn,
          redirectSignOut,
          responseType,
          scopes: oauthScopes,
          domain: cognitoDomain,
          providers: [
            { custom: customProviderName },
          ]
        } : undefined
      },
      userAttributes: {
        email: {
          required: true
        }
      },
      signUpVerificationMethod: 'code'
    }
  }
});

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <AuthProvider>
      <QueryProvider>
        <RouterProvider router={router} />
      </QueryProvider>
    </AuthProvider>
  </React.StrictMode>
);
