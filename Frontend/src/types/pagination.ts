export interface PaginatedResponse<T> {
  items: T[];
  nextToken?: string;
}
