import { getCategories } from "../api";
import { useState, useEffect, useMemo } from "react";
import {
  AllCommunityModule,
  ModuleRegistry,
  themeAlpine,
} from "ag-grid-community";
import { AgGridReact } from "ag-grid-react";
import type { ColDef } from "ag-grid-community";

ModuleRegistry.registerModules([AllCommunityModule]);

interface Category {
  json_ld_category: string | null;
  deal_count: number;
  total_diff: number;
  mean_diff: number;
}

export const Categories = () => {
  const [isDark, setIsDark] = useState(false);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
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
      field: "json_ld_category",
      cellRenderer: (params: any) => {
        return (
          params?.data?.json_ld_category?.slice(31, -1).replace("/", " -> ") ||
          "None"
        );
      },
      flex: 2,
    },
    { field: "deal_count", flex: 1 },
    { field: "total_diff", flex: 1 },
    {
      field: "mean_diff",
      valueGetter: (params: any) => parseInt(params.data.mean_diff),
      flex: 1,
    },
  ];

  useEffect(() => {
    getCategories(page, size).then((data: Category[]) => setCategories(data));
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
    <div className={gridTheme} style={{ height: "90dvh", width: "100%" }}>
      <AgGridReact<Category>
        rowData={categories}
        columnDefs={columnDefs}
        defaultColDef={defaultColDef}
        pagination={true}
        paginationPageSize={size}
        paginationPageSizeSelector={[10, 20, 50]}
      />
    </div>
  );
};
