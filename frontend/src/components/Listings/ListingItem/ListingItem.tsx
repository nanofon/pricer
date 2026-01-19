import { useState, useMemo, memo } from "react";
import styles from "./ListingItem.module.css";
import type { Listing } from "../../../types/listing.ts";

export type ListingItemProps = {
  listing: Listing;
  onNewPrice: (id: number, price: number) => void;
  onToggleIlliquid: (id: number) => void;
  onToggleInvalid: (id: number) => void;
};

const ListingItemComponent = ({
  listing,
  onNewPrice,
  onToggleIlliquid,
  onToggleInvalid,
}: ListingItemProps) => {
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);
  const [newPrice, setNewPrice] = useState(listing.price_new?.toString() || "");
  const [isIlliquid, setIsIlliquid] = useState(listing.is_illiquid);
  const [isInvalid, setIsInvalid] = useState(listing.is_invalid);

  const handlePriceUpdate = () => {
    onNewPrice(listing.id, parseFloat(newPrice));
  };

  const handleIlliquidUpdate = () => {
    setIsIlliquid(!isIlliquid);
    onToggleIlliquid(listing.id);
  };

  const handleInvalidUpdate = () => {
    setIsInvalid(!isInvalid);
    onToggleInvalid(listing.id);
  };

  return (
    <div className={styles.container}>
      <div className={styles.imageSection}>
        <img src={listing.image} alt={listing.name} className={styles.image} />
      </div>

      <div className={styles.detailsSection}>
        <div className={styles.header}>
          <h2 className={styles.title}>
            {listing.url ? (
              <a
                href={listing.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "inherit", textDecoration: "none" }}
              >
                {listing.name}
              </a>
            ) : (
              listing.name
            )}
          </h2>

          <div className={styles.statsGrid}>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Listing Price</span>
              <span className={styles.statValue}>{listing.price}</span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Predicted</span>
              <span className={styles.statValue}>
                {listing.price_predicted}
              </span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Delta</span>
              <span
                className={styles.statValue}
                style={{
                  color: listing.price_difference > 0 ? "#10b981" : "#ef4444",
                }}
              >
                {listing.price_difference > 0 ? "+" : ""}
                {listing.price_difference}
              </span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Days to sell</span>
              <span className={styles.statValue}>
                {listing.median_survival_days}
              </span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>New Price</span>
              <input
                type="number"
                className={styles.priceInput}
                value={newPrice}
                onChange={(e) => setNewPrice(e.target.value)}
                onBlur={handlePriceUpdate}
              />
            </div>
          </div>
        </div>

        <div className={styles.descriptionSection}>
          <pre
            className={`${styles.descriptionText} ${
              !isDescriptionExpanded ? styles.descriptionTruncated : ""
            }`}
          >
            {listing.description}
          </pre>
          <button
            className={styles.descriptionToggle}
            onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
          >
            {isDescriptionExpanded ? "Show less" : "Show more"}
          </button>
        </div>

        <div className={styles.controlsSection}>
          <div className={styles.checkboxGroup}>
            <label className={styles.checkboxLabel}>
              <input
                type="checkbox"
                className={styles.checkbox}
                checked={isIlliquid}
                onChange={(e) => handleIlliquidUpdate()}
              />
              Illiquid
            </label>

            <label className={styles.checkboxLabel}>
              <input
                type="checkbox"
                className={styles.checkbox}
                checked={isInvalid}
                onChange={(e) => handleInvalidUpdate()}
              />
              Invalid Listing
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};

export const ListingItem = memo(ListingItemComponent);
