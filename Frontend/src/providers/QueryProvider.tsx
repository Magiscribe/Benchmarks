import { ReactNode, createContext, useContext, useState, useEffect, useMemo } from 'react';
import axios, { AxiosInstance } from 'axios';
import { useAuth } from './AuthProvider';

const DEFAULT_API_URL = import.meta.env.VITE_API_URL;

interface QueryContextType {
  client: AxiosInstance;
  initialized: boolean;
  setBaseUrl: (url: string | null) => void;
}

const AxiosContext = createContext<QueryContextType | null>(null);

export function useClient(baseUrl?: string) {
  const context = useContext(AxiosContext);

  if (!context) {
    throw new Error('useClient must be used within QueryProvider');
  }

  // Set custom URL if provided
  useEffect(() => {
    if (baseUrl) {
      context.setBaseUrl(baseUrl);
      return () => context.setBaseUrl(null); // Reset on unmount
    }
  }, [baseUrl, context]);

  return context;
}

interface QueryProviderProps {
  children: ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
  const [token, setToken] = useState<string | null>(null);
  const [initialized, setIsInitialized] = useState(false);
  const [currentBaseUrl, setCurrentBaseUrl] = useState<string>(DEFAULT_API_URL);
  const { user, getToken } = useAuth();

  useEffect(() => {
    async function fetchToken() {
      setIsInitialized(false);
      const newToken = await getToken();
      setToken(newToken?.toString() ?? null);
      setIsInitialized(true);
    }
    fetchToken();
  }, [user, getToken]);

  const axiosClient = useMemo(() => {
    return axios.create({
      baseURL: currentBaseUrl,
      headers: {
        'Content-Type': 'application/json',
        Authorization: token ? `Bearer ${token}` : undefined
      }
    });
  }, [token, user, currentBaseUrl]);

  // Add response interceptor for token refresh and retry logic
  axiosClient.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
      
      // Initialize retry counter if it doesn't exist
      if (!originalRequest._retry) {
        originalRequest._retry = 0;
      }

      // Only retry on 401 errors and limit to 3 retries
      if (error.response?.status === 401 && originalRequest._retry < 3) {
        originalRequest._retry += 1;
        console.log(`Retrying request (${originalRequest._retry}/3) due to 401 error`);
        
        const newToken = await getToken(); // Force refresh
        setToken(newToken?.toString() ?? null);
        if (newToken && error.config) {
          error.config.headers.Authorization = `Bearer ${newToken}`;
          return axiosClient(error.config);
        }
      }

      return Promise.reject(error);
    }
  );

  const contextValue = useMemo(
    () => ({
      client: axiosClient,
      initialized,
      setBaseUrl: (url: string | null) => setCurrentBaseUrl(url ?? DEFAULT_API_URL)
    }),
    [axiosClient, initialized]
  );

  return <AxiosContext.Provider value={contextValue}>{children}</AxiosContext.Provider>;
}
