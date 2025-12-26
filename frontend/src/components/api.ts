const API_URL = "http://localhost:8000";

export const getStats = async () => {
  const response = await fetch(`${API_URL}/stats`);
  const data = await response.json();
  return data;
};

export const getListings = async (page: number, size: number) => {
  const response = await fetch(`${API_URL}/listings?page=${page}&size=${size}`);
  const data = await response.json();
  return data;
};

export const getCategories = async (page: number, size: number) => {
  const response = await fetch(
    `${API_URL}/categories?page=${page}&size=${size}`
  );
  const data = await response.json();
  return data;
};
