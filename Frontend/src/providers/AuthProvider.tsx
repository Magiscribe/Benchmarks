import * as Auth from 'aws-amplify/auth';
import {
  AuthUser,
  ConfirmResetPasswordInput,
  ConfirmSignInInput,
  ConfirmSignUpInput,
  ResetPasswordInput,
  SignInInput,
  SignUpInput,
  UpdateUserAttributesOutput,
  UpdatePasswordInput
} from 'aws-amplify/auth';
import { createContext, useContext, useEffect, useState } from 'react';

/**
 * Interface defining the authentication state and methods available in the auth context
 * @interface AuthState
 */
interface AuthState {
  /** Indicates if the auth state has finished loading */
  loaded: boolean;

  /** The current authenticated user or undefined if not authenticated */
  user: AuthUser | undefined;

  /** Additional attributes of the authenticated user */
  userAttributes: Auth.FetchUserAttributesOutput | undefined;

  /** Groups the authenticated user belongs to */
  groups: string[];

  /** Indicates if the user logged in via a federated identity provider */
  isFederatedLogin: boolean;

  /**
   * Register a new user
   * @param input - Sign up input containing username, password and other attributes
   * @returns Promise resolving to sign up output or undefined
   */
  signUp(input: SignUpInput): Promise<Auth.SignUpOutput | undefined>;

  /**
   * Confirm a user's registration
   * @param input - Confirmation input containing username and confirmation code
   * @returns Promise resolving to confirmation output or undefined
   */
  confirmSignUp(input: ConfirmSignUpInput): Promise<Auth.ConfirmSignUpOutput | undefined>;

  /**
   * Sign in a user
   * @param input - Sign in input containing username and password
   * @returns Promise resolving to sign in output or undefined
   */
  signIn(input: SignInInput): Promise<Auth.SignInOutput | undefined>;

  /**
   * Confirm sign in for MFA or custom challenges
   * @param input - Confirmation input containing challenge response
   * @returns Promise resolving to confirmation output or undefined
   */
  confirmSignIn(input: ConfirmSignInInput): Promise<Auth.ConfirmSignInOutput | undefined>;

  /**
   * Sign out the current user
   * @returns Promise that resolves when sign out is complete
   */
  signOut(): Promise<void>;

  /**
   * Initiate password reset flow
   * @param input - Reset password input containing username
   * @returns Promise that resolves when reset is initiated
   */
  resetPassword(input: Auth.ResetPasswordInput): Promise<Auth.ResetPasswordOutput | undefined>;

  /**
   * Confirm password reset with verification code
   * @param input - Confirmation input containing username, code, and new password
   * @returns Promise that resolves when password is reset
   */
  confirmResetPassword(input: Auth.ConfirmResetPasswordInput): Promise<void>;

  /**
   * Update the current user's password
   * @param input - Update password input containing old and new passwords
   * @returns Promise that resolves when password is updated
   */
  updatePassword(input: UpdatePasswordInput): Promise<void>;

  /**
   * Get the current authentication token
   * @returns Promise resolving to the JWT or undefined if not authenticated
   */
  getToken(): Promise<Auth.JWT | undefined>;

  /**
   * Update user attributes
   * @param attributes - Record of attribute key-value pairs to update
   * @returns Promise resolving to update output or undefined
   */
  updateUserAttributes(
    attributes: Record<string, string>
  ): Promise<UpdateUserAttributesOutput | undefined>;
}

/**
 * Authentication context for providing auth state throughout the application
 */
export const AuthContext = createContext<AuthState>({} as AuthState);

/**
 * Custom hook to access the authentication context
 * @returns The authentication state and methods
 */
export const useAuth = () => useContext(AuthContext);

/**
 * Props for the AuthProvider component
 * @interface AuthProps
 */
interface AuthProps {
  /** Child components that will have access to the auth context */
  children: React.ReactNode;
}

/**
 * Provider component that wraps the application and provides authentication state
 * @param props - The component props
 * @returns AuthProvider component
 */
export const AuthProvider = ({ children }: AuthProps) => {
  const [loaded, setLoaded] = useState(false);
  const [authState, setAuthState] = useState<{
    user?: Auth.AuthUser;
    userAttributes?: Auth.FetchUserAttributesOutput;
    groups: string[];
    isFederatedLogin: boolean; // Add isFederatedLogin to state
  }>({ groups: [], isFederatedLogin: false }); // Initialize isFederatedLogin

  const { user, userAttributes, groups, isFederatedLogin } = authState; // Destructure isFederatedLogin

  // Check if authentication is completely disabled
  const authDisabled = import.meta.env.VITE_ENABLE_COGNITO_LOGIN !== 'true' && 
                      import.meta.env.VITE_ENABLE_CUSTOM_PROVIDER !== 'true';

  useEffect(() => {
    if (authDisabled) {
      // If auth is disabled, create a mock user and mark as loaded
      setAuthState({
        user: { userId: 'guest', username: 'guest' } as Auth.AuthUser,
        userAttributes: { email: 'guest@localhost' },
        groups: [],
        isFederatedLogin: false
      });
      setLoaded(true);
    } else {
      checkUser();
    }
  }, [authDisabled]);

  /**
   * Updates the authentication state with current user information
   */
  const updateAuthState = async () => {
    try {
      const currentUser = await Auth.getCurrentUser().catch(() => undefined);

      if (!currentUser) {
        setAuthState({ groups: [], isFederatedLogin: false }); // Reset isFederatedLogin on logout
        return;
      }

      const attributes = await Auth.fetchUserAttributes().catch((e) => undefined);
      const session = await Auth.fetchAuthSession().catch(() => undefined);
      const userGroups = (session?.tokens?.accessToken.payload['cognito:groups'] as string[]) || [];

      // Determine if the user is federated
      const isFederated = Boolean(
        attributes?.identities || // Standard federated identity attribute
        attributes?.nameidentifier || // Custom attribute from Magiscribe (example)
        attributes?.objectidentifier // Custom attribute from Magiscribe (example)
      );

      setAuthState({
        user: currentUser,
        userAttributes: attributes,
        groups: userGroups,
        isFederatedLogin: isFederated // Set isFederatedLogin state
      });
    } catch (error) {
      console.error('Error updating auth state:', error);
      setAuthState({ groups: [], isFederatedLogin: false }); // Reset on error
    }
  };

  /**
   * Check if a user is currently authenticated and update state accordingly
   */
  const checkUser = async () => {
    try {
      await updateAuthState();
    } finally {
      setLoaded(true);
    }
  };

  /**
   * Helper function to wrap authentication actions with common error handling and state updates
   * @param action - The authentication action to execute
   * @returns Promise resolving to the action result or undefined
   */
  const wrapAuthAction = async <T,>(action: () => Promise<T>): Promise<T | undefined> => {
    try {
      const result = await action();
      await updateAuthState();
      return result;
    } catch (error) {
      console.error('Auth action failed:', error);
      throw error;
    }
  };

  /**
   * Register a new user
   * @param input - Sign up input containing username, password and attributes
   * @returns Promise resolving to sign up output or undefined
   */
  const signUp = (input: SignUpInput) => wrapAuthAction(() => Auth.signUp(input));

  /**
   * Confirm a user's registration
   * @param input - Confirmation input containing username and confirmation code
   * @returns Promise resolving to confirmation output or undefined
   */
  const confirmSignUp = (input: ConfirmSignUpInput) =>
    wrapAuthAction(() => Auth.confirmSignUp(input));

  /**
   * Sign in a user
   * @param input - Sign in input containing username and password
   * @returns Promise resolving to sign in output or undefined
   */  const signIn = (input: SignInInput) => wrapAuthAction(async () => {
    const enableCustomProvider = import.meta.env.VITE_ENABLE_CUSTOM_PROVIDER === 'true';
    const enableCognitoLogin = import.meta.env.VITE_ENABLE_COGNITO_LOGIN === 'true';
    const customProviderName = import.meta.env.VITE_CUSTOM_PROVIDER_NAME || 'Magiscribe';
    
    // If neither authentication method is enabled, return success immediately
    if (!enableCustomProvider && !enableCognitoLogin) {
      return { isSignedIn: true, nextStep: { signInStep: 'DONE' } } as any;
    }
    
    // If only custom provider is enabled, or no input was provided, use the custom provider
    if (enableCustomProvider && (!input.username || !input.password || !enableCognitoLogin)) {
      await Auth.signInWithRedirect({
        provider: { custom: customProviderName },
      });
    } else if (enableCognitoLogin && input.username && input.password) {
      // Use Cognito login with username/password
      return Auth.signIn(input);
    } else {
      throw new Error('No valid authentication method available');
    }
  });

  /**
   * Confirm sign in for MFA or custom challenges
   * @param input - Confirmation input containing challenge response
   * @returns Promise resolving to confirmation output or undefined
   */
  const confirmSignIn = (input: ConfirmSignInInput) =>
    wrapAuthAction(() => Auth.confirmSignIn(input));

  /**
   * Initiate password reset flow
   * @param input - Reset password input containing username
   * @returns Promise that resolves when reset is initiated
   */
  const resetPassword = (input: ResetPasswordInput) =>
    wrapAuthAction(() => Auth.resetPassword(input));

  /**
   * Confirm password reset with verification code
   * @param input - Confirmation input containing username, code, and new password
   * @returns Promise that resolves when password is reset
   */
  const confirmResetPassword = (input: ConfirmResetPasswordInput) =>
    wrapAuthAction(() => Auth.confirmResetPassword(input));

  /**
   * Update the current user's password
   * @param input - Update password input containing old and new passwords
   * @returns Promise that resolves when password is updated
   */
  const updatePassword = (input: UpdatePasswordInput) =>
    wrapAuthAction(() => Auth.updatePassword(input));

  /**
   * Sign out the current user
   * @returns Promise that resolves when sign out is complete
   */
  const signOut = async () => {
    try {
      await Auth.signOut();
      setAuthState({ groups: [], isFederatedLogin: false }); // Reset state on sign out
    } catch (error) {
      console.error('Sign out failed:', error);
      throw error;
    }
  };

  /**
   * Get the current authentication token
   * @returns Promise resolving to the JWT or undefined if not authenticated
   */
  const getToken = async () => {
    try {
      const session = await Auth.fetchAuthSession();
      return session?.tokens?.idToken;
    } catch (error) {
      console.error('Failed to get token:', error);
      return undefined;
    }
  };

  /**
   * Update user attributes
   * @param attributes - Record of attribute key-value pairs to update
   * @returns Promise resolving to update output or undefined
   */
  const updateUserAttributes = (attributes: Record<string, string>) =>
    wrapAuthAction(async () => {
      const userAttributes: Record<string, string> = {};
      Object.entries(attributes).forEach(([userAttributeKey, value]) => {
        userAttributes[userAttributeKey] = value;
      });
      return await Auth.updateUserAttributes({ userAttributes });
    });

  return (
    <AuthContext.Provider
      value={{
        loaded,
        user,
        userAttributes,
        groups,
        isFederatedLogin, // Provide isFederatedLogin in context
        signUp,
        confirmSignUp,
        signIn,
        confirmSignIn,
        signOut,
        resetPassword,
        updatePassword,
        confirmResetPassword,
        getToken,
        updateUserAttributes
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
