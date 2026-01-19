export type Listing = {
  id: number;
  url: string;
  category: string;
  name: string;
  description: string;
  city: string;
  image: string;
  price: number;
  price_predicted: number;
  price_difference: number;
  price_new?: number;
  is_illiquid?: boolean;
  is_invalid?: boolean;
  median_survival_days?: number;
  current_days_on_market?: number;
};
