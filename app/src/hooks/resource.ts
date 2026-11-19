/**
 * The one shape every data hook hands its consumers: the value once there is one, the reason it
 * could not be had, whether the first answer is still pending, and a way to ask again. A failed
 * background refresh never replaces a value already shown with an error.
 */
export interface Resource<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  retry: () => void;
}

export function errorText(e: unknown): string {
  return e instanceof Error ? e.message : String(e);
}
