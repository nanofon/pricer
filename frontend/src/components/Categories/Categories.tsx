import { getCategories } from "../api.ts";
import { useState, useEffect, useMemo } from "react";
import { AllCommunityModule, ModuleRegistry } from "ag-grid-community";
import { AgGridReact } from "ag-grid-react";
import type { ColDef } from "ag-grid-community";

ModuleRegistry.registerModules([AllCommunityModule]);

interface Category {
  category: string | null;
  deal_count: number;
  mean_diff: number;
  total_diff: number;
}

export const Categories = () => {
  const [isDark, setIsDark] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);

  const defaultColDef = useMemo(() => {
    return {
      resizable: true,
      sortable: true,
      filter: true,
      flex: 1,
    };
  }, []);

  const columnDefs: ColDef<Category>[] = [
    {
      field: "category",
      headerName: "Category",
      cellRenderer: (params: any) => {
        return (
          params?.data?.category?.slice(31, -1).replace("/", " -> ") || "None"
        );
      },
      flex: 2,
    },
    { field: "deal_count", headerName: "Total Count", flex: 1 },
    {
      field: "mean_diff",
      headerName: "Mean Diff",
      valueFormatter: (params: any) => params.value.toFixed(0),
      flex: 1,
    },
    { field: "total_diff", headerName: "Total Diff", flex: 1 },
  ];

  const fetchData = async (page: number, size: number) => {
    const data = await getCategories(page, size);
    setCategories([...categories, ...data]);
    if (data.length === size) {
      fetchData(page + 1, size);
    }
  };

  useEffect(() => {
    const fetchAllData = async (page: number = 1) => {
      try {
        const data = await getCategories(page, 50);
        if (data.length > 0) {
          setCategories((categories) => [...categories, ...data]);
          fetchAllData(page + 1);
        }
      } catch (error) {
        console.error("Error fetching categories:", error);
      }
    };
    fetchAllData();
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
    <div className={gridTheme} style={{ height: "90vh", width: "100%" }}>
      <AgGridReact<Category>
        className="ag-theme-alpine"
        rowData={categories}
        columnDefs={columnDefs}
        defaultColDef={defaultColDef}
        pagination={true}
        paginationPageSize={15}
        paginationPageSizeSelector={[15, 30, 50]}
      />
    </div>
  );
};
