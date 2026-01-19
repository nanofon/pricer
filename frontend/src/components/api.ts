export const getStats = async () => {
  const response = await fetch(`/api/stats`);
  const data = await response.json();
  return data;
};

export const getListings = async (page: number, size: number) => {
  const response = await fetch(`/api/listings?page=${page}&size=${size}`);
  const data = await response.json();
  return data;
};

export const getCategories = async (page: number, size: number) => {
  const response = await fetch(`/api/categories?page=${page}&size=${size}`);
  const data = await response.json();
  return data;
};

export const setPriceNew = async (id: number, price_of_new: number) => {
  const response = await fetch(`/api/listings/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ price_of_new }),
  });
  const data = await response.json();
  return data;
};
