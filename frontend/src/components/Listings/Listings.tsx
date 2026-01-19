import { Toaster, toast } from "react-hot-toast";
import { useState, useEffect, useCallback, useRef } from "react";
import { ListingItem } from "./ListingItem/ListingItem.tsx";
import type { Listing } from "../../types/listing.ts";

export const Listings = () => {
  const [listings, setListings] = useState<Listing[]>([]);
  const [isEnd, setIsEnd] = useState(false);
  const [isFetching, setIsFetching] = useState(false); // Prevents duplicate requests

  const fetchNext = useCallback(async () => {
    if (isFetching || isEnd) return;

    setIsFetching(true);
    // Use the latest state to build the exclusion list
    const currentIds = listings.map((l) => l.id).join(",");

    try {
      const response = await fetch(
        `/api/listings/next-best?exclude=${currentIds}`
      );

      // Handle 204 No Content or empty responses
      if (response.status === 204) {
        setIsEnd(true);
        return;
      }

      const newListing: Listing = await response.json();

      if (!newListing) {
        setIsEnd(true);
      } else {
        setListings((prev) => [...prev, newListing]);
      }
    } catch (error) {
      console.error("Error fetching listings: ", error);
    } finally {
      setIsFetching(false);
    }
  }, [listings, isEnd, isFetching]);

  // The "Auto-Replenish" Engine
  useEffect(() => {
    if (listings.length < 5 && !isEnd && !isFetching) {
      fetchNext();
    }
  }, [listings.length, isEnd, isFetching, fetchNext]);

  const postNewPrice = useCallback(async (id: number, price: number) => {
    const updateProcess = async () => {
      const response = await fetch(`/api/listings/${id}/price_new`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ price }),
      });

      if (!response.ok) {
        throw new Error(
          `HTTP error at posting new price! status: ${response.status}`
        );
      }

      setListings((prev) => prev.filter((l) => l.id !== id));
      return response.json();
    };

    toast.promise(updateProcess(), {
      loading: "Posting new price...",
      success: "Price of new updated. Sent for repricing.",
      error: "Failed to update price.",
    });
  }, []);

  const markIlliquid = useCallback(async (id: number) => {
    const updateProcess = async () => {
      const response = await fetch(`/api/listings/${id}/illiquid`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) {
        throw new Error(
          `HTTP error at marking ${id} illiquid! status: ${response.status}`
        );
      }

      setListings((prev) => prev.filter((l) => l.id !== id));
      return response.json();
    };

    toast.promise(updateProcess(), {
      loading: "Marking as illiquid...",
      success: "Listing marked as illiquid.",
      error: "Failed to mark as illiquid.",
    });
  }, []);

  const markInvalid = useCallback(async (id: number) => {
    const updateProcess = async () => {
      const response = await fetch(`/api/listings/${id}/invalid`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) {
        throw new Error(
          `HTTP error at marking ${id} invalid! status: ${response.status}`
        );
      }

      setListings((prev) => prev.filter((l) => l.id !== id));
      return response.json();
    };

    toast.promise(updateProcess(), {
      loading: "Marking as invalid...",
      success: "Listing marked as invalid.",
      error: "Failed to mark as invalid.",
    });
  }, []);

  return (
    <div>
      <Toaster position="top-left" />
      {listings.map((listing) => (
        <ListingItem
          key={listing.id}
          listing={listing}
          onToggleInvalid={markInvalid}
          onToggleIlliquid={markIlliquid}
          onNewPrice={postNewPrice}
        />
      ))}
      {isEnd && listings.length === 0 && <p>No more listings found.</p>}
      {isFetching && <p>Loading next deal...</p>}
    </div>
  );
};
