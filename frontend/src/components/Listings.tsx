import { getListings } from "./api.ts";
import { useState, useEffect, useMemo } from "react";
import { AllCommunityModule, ModuleRegistry } from "ag-grid-community";
import { AgGridReact } from "ag-grid-react";
import type { ColDef } from "ag-grid-community";
import { Modal } from "./Modal/Modal.tsx";

ModuleRegistry.registerModules([AllCommunityModule]);

interface Listing {
  id: number;
  url: string;
  name: string;
  description: string;
  category: string | null;
  city: string | null;
  image: string | null;
  price: number;
  price_predicted: number;
  price_difference: number;
}

export const Listings = () => {
  const [selectedRow, setSelectedRow] = useState<Listing | null>(null);
  const [isDark, setIsDark] = useState(false);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(15);
  const [listings, setListings] = useState<Listing[]>([]);

  const onRowSelected = (event: any) => {
    setSelectedRow(event.data);
  };

  const defaultColDef = useMemo(() => {
    return {
      resizable: true,
      sortable: true,
      filter: true,
      flex: 1,
    };
  }, []);

  const columnDefs: ColDef<Listing>[] = [
    {
      field: "image",
      cellRenderer: (params: any) => {
        return (
          <img
            src={params?.data?.image}
            alt={params?.data?.name}
            style={{ width: "50px", height: "50px" }}
          />
        );
      },
      headerName: "Image",
      flex: 1,
    },
    {
      field: "url",
      cellRenderer: (params: any) => {
        return (
          <a href={params?.data?.url} target="_blank">
            *
          </a>
        );
      },
      headerName: "link",
      flex: 1,
    },
    {
      field: "category",
      cellRenderer: (params: any) => {
        return (
          params?.data?.category?.slice(31, -1).replace("/", " -> ") || "None"
        );
      },
      flex: 3,
    },
    { field: "name" },
    { field: "description" },
    { field: "city" },
    { field: "price", flex: 1 },
    { field: "price_predicted", flex: 1 },
    {
      field: "price_difference",
      flex: 1,
    },
  ];

  useEffect(() => {
    getListings(page, size).then((data: Listing[]) => {
      setListings(data);
    });
  }, []);

  useEffect(() => {
    setIsDark(document.documentElement.classList.contains("dark"));

    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains("dark"));
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });
    return () => observer.disconnect();
  }, []);

  const gridTheme = isDark ? "ag-theme-alpine-dark" : "ag-theme-alpine";

  return (
    <div style={{ position: "relative", height: "90vh", width: "100%" }}>
      <div className={gridTheme} style={{ height: "100%", width: "100%" }}>
        <AgGridReact<Listing>
          rowData={listings}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          pagination={true}
          paginationPageSize={size}
          paginationPageSizeSelector={[15, 30, 50]}
          onRowClicked={onRowSelected}
        />
      </div>
      {selectedRow && (
        <Modal selectedRow={selectedRow} onClose={() => setSelectedRow(null)} />
      )}
    </div>
  );
};
