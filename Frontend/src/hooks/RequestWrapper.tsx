import { useState } from 'react';

/**
 * Hook to handle API requests with loading state and error handling
 * @returns Object containing request function and error state
 */
export function useRequest() {
  const [error, setError] = useState<string>('');

  /**
   * Makes API requests with error handling
   * @param requestFn - The function that makes the actual API call
   * @param errorMessage - Error message to display if the request fails
   * @param loadingStateSetter - Optional function to update loading state
   * @returns The result of the API call or null if it failed
   */
  const request = async <T,>(
    requestFn: () => Promise<T>,
    errorMessage: string,
    loadingStateSetter?: (isLoading: boolean) => void
  ): Promise<T | null> => {
    try {
      loadingStateSetter?.(true);
      const result = await requestFn();
      setError('');
      return result;
    } catch {
      setError(errorMessage);
      return null;
    } finally {
      loadingStateSetter?.(false);
    }
  };

  return { request, error, setError };
}
